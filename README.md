# SkyBoard

**A small Python library for live aviation data: nearby airports, nearby aircraft, airport weather and take-off / landing detection.**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha-orange)]()

SkyBoard answers questions such as *"Which airport am I closest to?"*, *"Which aircraft is currently flying nearest to me?"*, *"What is the weather at that airport?"* and *"How many aircraft are in the air above it right now?"* — using free, public data sources and an offline airport database bundled with the package.

---

## Table of contents

- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick start](#quick-start)
- [API reference](#api-reference)
  - [GetLocation](#getlocation)
  - [AirportNearest](#airportnearest)
  - [AirportInfo](#airportinfo)
  - [AircraftNearest](#aircraftnearest)
  - [AircraftInfo](#aircraftinfo)
  - [AircraftTotal](#aircrafttotal)
- [Programs](#programs)
  - [FlightMonitor](#flightmonitor)
- [Examples](#examples)
- [Project structure](#project-structure)
- [Data sources](#data-sources)
- [Known limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## How it works

SkyBoard is a set of independent modules. Each module exposes a single `get()` function that returns a plain Python dictionary, so the modules can be combined freely or used one at a time.

| Module | What it does | Data source | Network required |
|---|---|---|---|
| `GetLocation` | Estimates your position from surrounding Wi-Fi access points | BeaconDB geolocation API | Yes |
| `AirportNearest` | Finds the closest airport to given coordinates | Bundled `airports.csv` | No |
| `AirportInfo` | Returns current temperature and wind at an airport | AviationWeather.gov (METAR) | Yes |
| `AircraftNearest` | Finds the aircraft currently closest to given coordinates | OpenSky Network | Yes |
| `AircraftInfo` | Returns position, speed and heading for a callsign | OpenSky Network | Yes |
| `AircraftTotal` | Counts aircraft in a box around an airport | OpenSky Network + `airports.csv` | Yes |

Every `get()` accepts an optional `VERBOSE=True` flag, which prints a step-by-step log of what the module is doing. This is intended for debugging and is off by default.

Distances are computed with the haversine formula on a sphere of radius 6371 km, and are returned in kilometres.

---

## Requirements

- Python 3.10 or newer
- [`requests`](https://pypi.org/project/requests/)
- An internet connection for every module except `AirportNearest`
- **For `GetLocation` only:** Linux with NetworkManager, because the Wi-Fi scan is performed by calling `nmcli`. All other modules are platform independent.

---

## Installation

### From source (recommended)

```bash
git clone https://github.com/davidmachek/SkyBoard.git
cd SkyBoard
pip install requests
```

Then run your scripts from the repository root with the `src` directory on the import path:

```bash
PYTHONPATH=src python examples/example1.py
```

On Windows (PowerShell):

```powershell
$env:PYTHONPATH="src"
python examples\example1.py
```

### As an installed package

```bash
pip install .
```

Note that in the current version this installs the Python modules but **not** the bundled `airports.csv`, so `AirportNearest` and `AircraftTotal` will raise `FileNotFoundError`. See [Known limitations](#known-limitations) for the one-line fix.

---

## Quick start

```python
from skyboard import GetLocation, AirportNearest, AirportInfo

location = GetLocation.get()
print(location)
# {'lat': 50.0755, 'lng': 14.4378}

airport = AirportNearest.get(location["lat"], location["lng"], ONLY_LARGE=True)
print(airport)
# {'distance_km': 13.00107111912316,
#  'name': 'Václav Havel Airport Prague',
#  'icao_code': 'LKPR',
#  'municipality': 'Prague'}

weather = AirportInfo.get(airport["icao_code"])
print(weather)
# {'temp': 7.0, 'wind_dir': 240, 'wind_speed': 11}
```

If you do not want to rely on Wi-Fi geolocation, simply pass coordinates yourself — every function that needs a position takes plain latitude and longitude.

---

## API reference

### GetLocation

```python
GetLocation.get(VERBOSE=False) -> dict
```

Scans nearby Wi-Fi access points with `nmcli`, sends their MAC addresses and signal strengths to the BeaconDB geolocation API, and returns the estimated position.

**Returns**

```python
{"lat": 50.0755, "lng": 14.4378}
```

**Raises / exits:** if no access points are found, the process exits with status 1. If `nmcli` is not installed, `subprocess.check_output` raises `FileNotFoundError`.

No GPS hardware is required, but Wi-Fi must be switched on and at least one network must be visible.

---

### AirportNearest

```python
AirportNearest.get(lat, lon, VERBOSE=False, ONLY_LARGE=False) -> dict | None
```

Searches the bundled offline airport database. Heliports, closed airfields and records without an ICAO code are always skipped. With `ONLY_LARGE=True` the search is restricted to airports classified as `large_airport` — useful when you want a real international airport rather than a grass strip two kilometres away.

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `lat` | `float` | — | Latitude in decimal degrees |
| `lon` | `float` | — | Longitude in decimal degrees |
| `ONLY_LARGE` | `bool` | `False` | Restrict the result to large international airports |
| `VERBOSE` | `bool` | `False` | Print progress information |

**Returns**

```python
{
    "distance_km": 13.00107111912316,
    "name": "Václav Havel Airport Prague",
    "icao_code": "LKPR",
    "municipality": "Prague",
}
```

Returns `None` if nothing matches.

**Example — the same position, with and without the filter**

```python
from skyboard import AirportNearest

lat, lon = 50.0755, 14.4378  # Prague city centre

print(AirportNearest.get(lat, lon))
# {'distance_km': 8.82, 'name': 'Letňany Airfield', 'icao_code': 'LKLT', ...}

print(AirportNearest.get(lat, lon, ONLY_LARGE=True))
# {'distance_km': 13.00, 'name': 'Václav Havel Airport Prague', 'icao_code': 'LKPR', ...}
```

This module works fully offline.

---

### AirportInfo

```python
AirportInfo.get(ICAO, VERBOSE=False) -> dict | tuple
```

Downloads the most recent METAR observation for the given airport from AviationWeather.gov and extracts three fields.

**Returns**

```python
{"temp": 7.0, "wind_dir": 240, "wind_speed": 11}
```

Values are temperature in degrees Celsius, wind direction in degrees, and wind speed in knots, exactly as published in the METAR. Fields missing from the report are returned as the string `"UNKNOWN"`.

If the airport publishes no METAR, or the request fails, the function returns the tuple `(None, None, None)`. Check the result before subscripting it:

```python
info = AirportInfo.get("LKPR")
if isinstance(info, dict):
    print(info["temp"])
else:
    print("No weather data available")
```

---

### AircraftNearest

```python
AircraftNearest.get(LAT, LON, VERBOSE=False) -> dict | tuple
```

Downloads the global OpenSky state vector snapshot and returns the aircraft closest to the given position.

**Returns**

```python
{"callsign": "RYR6TZ", "distance": "12.44"}
```

`distance` is a string in kilometres, formatted to two decimal places. When no aircraft can be resolved, the function returns `(False, False)`.

---

### AircraftInfo

```python
AircraftInfo.get(callsign, VERBOSE=False) -> dict | None
```

Looks up a single aircraft by callsign. The callsign is trimmed and upper-cased automatically, so `" ryr6tz "` and `"RYR6TZ"` are equivalent.

**Returns**

```python
{
    "callsign": "RYR6TZ",
    "country": "Ireland",
    "lat": 50.13,
    "lon": 14.51,
    "speed": 218.4,     # metres per second
    "heading": 271.5,   # degrees
}
```

Returns `None` if the callsign is not currently airborne, or if the request fails.

**Example — chaining the two aircraft modules**

```python
from skyboard import AircraftNearest, AircraftInfo

nearest = AircraftNearest.get(50.0755, 14.4378)
if isinstance(nearest, dict):
    details = AircraftInfo.get(nearest["callsign"])
    if details:
        print(f"{details['callsign']} at {details['lat']}, {details['lon']} "
              f"heading {details['heading']} deg")
```

---

### AircraftTotal

```python
AircraftTotal.get(icao, VERBOSE=False) -> dict | None
```

Resolves the airport coordinates from the bundled database, builds a bounding box of plus/minus 0.2 degrees around it (roughly 22 km north-south) and counts the aircraft reported inside it.

**Returns**

```python
{"count": 14}
```

Returns `None` for an unknown ICAO code or a failed request. The count includes aircraft on the ground as well as in the air.

---

## Programs

The `Programs` directory contains ready-to-run tools built on top of the library rather than importable building blocks.

### FlightMonitor

```python
FlightMonitor.run(icao_code)
```

Polls the airspace around an airport every five seconds, keeps the previous state of every aircraft, and prints an event whenever an aircraft changes between airborne and on-ground:

- **TAKEOFF** — the aircraft was on the ground, is now airborne, and exceeds 40 knots
- **LANDING** — the aircraft was airborne and is now on the ground

```bash
PYTHONPATH=src python -c "import sys; sys.path.insert(0,'Programs'); import FlightMonitor; FlightMonitor.run('LKPR')"
```

Sample output:

```
Tracking: Václav Havel Airport Prague (LKPR)
TAKEOFF: CSA1234 | 152 kts
LANDING: RYR6TZ | 138 -> 0 kts
TAKEOFF: DLH9LT | 147 kts
```

The loop runs until interrupted with Ctrl+C. Because it depends on how frequently OpenSky refreshes its data, individual events can be missed if an aircraft transitions between two polls.

---

## Examples

The `examples` directory contains two runnable scripts.

**`example1.py` — the full chain**

Determines your location, finds the nearest large airport, reads its weather, counts the aircraft above it, then finds the nearest aircraft and prints its details. This is the fastest way to check that everything is wired up correctly.

```bash
PYTHONPATH=src python examples/example1.py
```

**`example2.py` — continuous monitoring**

Starts `FlightMonitor` on Prague (`LKPR`).

**A third example you can build in a minute — a departure board for any airport, no geolocation needed:**

```python
from skyboard import AirportInfo, AircraftTotal, AirportNearest

for icao in ["LKPR", "EGLL", "EDDF", "LFPG"]:
    weather = AirportInfo.get(icao)
    traffic = AircraftTotal.get(icao)

    temp = weather["temp"] if isinstance(weather, dict) else "n/a"
    count = traffic["count"] if traffic else "n/a"

    print(f"{icao}  temp {temp:>5}  aircraft in area {count:>4}")
```

```
LKPR  temp   7.0  aircraft in area   14
EGLL  temp   9.0  aircraft in area   38
EDDF  temp   6.0  aircraft in area   31
LFPG  temp   8.0  aircraft in area   27
```

---

## Project structure

```
SkyBoard/
├── src/
│   └── skyboard/
│       ├── __init__.py           re-exports all six modules
│       ├── GetLocation.py        Wi-Fi based geolocation
│       ├── AirportNearest.py     offline nearest-airport search
│       ├── AirportInfo.py        METAR weather lookup
│       ├── AircraftNearest.py    nearest aircraft
│       ├── AircraftInfo.py       aircraft detail by callsign
│       ├── AircraftTotal.py      aircraft count around an airport
│       └── airports.csv          offline airport database
├── Programs/
│   └── FlightMonitor.py          take-off / landing monitor
├── examples/
│   ├── example1.py
│   └── example2.py
├── main.py                       demo script
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## Data sources

| Source | Used for | Notes |
|---|---|---|
| [OpenSky Network](https://opensky-network.org/) | Live aircraft positions | Anonymous access is rate limited. Heavy polling will start returning empty responses. |
| [AviationWeather.gov](https://aviationweather.gov/) | METAR observations | Public US government service, no key required. |
| [BeaconDB](https://beacondb.net/) | Wi-Fi geolocation | Community-run, open geolocation database. |
| `airports.csv` | Offline airport lookup | 85,556 records in the OurAirports schema, of which 10,203 carry an ICAO code and 1,179 are classified as large airports. |

SkyBoard requires no API keys and no registration.

---

## Known limitations

These are honest notes on the current 0.1.0 state rather than a roadmap.

1. **`airports.csv` is not installed by `pip install .`** The package data is not declared, so the file stays behind in the source tree. Add the following to `pyproject.toml` to fix it:

   ```toml
   [tool.setuptools.package-data]
   skyboard = ["airports.csv"]
   ```

2. **The import name is `skyboard`, not `SkyBoard`.** `pyproject.toml` declares the package as `skyboard`, and Linux and macOS filesystems are case sensitive, so `from SkyBoard import ...` — as used in `main.py`, `example1.py` and `example2.py` — fails outside Windows. Either rename the imports in those files, or rename the package directory and the `name` field consistently.

3. **`Programs` is outside the package.** It is neither inside `src/skyboard/` nor declared in `pyproject.toml`, so `from SkyBoard.Programs import FlightMonitor` cannot resolve after installation. Moving `Programs/` to `src/skyboard/Programs/` with an `__init__.py` would make it importable — and would also fix the `../airports.csv` path inside `FlightMonitor.py`, which currently points at a file that does not exist.

4. **`GetLocation` calls `exit(1)`.** A library should raise an exception and let the caller decide; the current behaviour terminates the host application.

5. **Inconsistent error returns.** `AirportInfo` returns a three-element tuple on failure and a dict on success; `AircraftNearest` returns `(False, False)`. Returning `None` uniformly would make the API easier to use.

6. **Bare `except:` blocks** in several modules swallow every exception, including `KeyboardInterrupt`, which makes failures hard to diagnose.

7. **No tests and no caching.** Every call re-downloads the full global OpenSky snapshot, and `AirportNearest` re-parses the whole 85,000-row CSV.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'SkyBoard'` | Case-sensitive filesystem | Import `skyboard` in lower case |
| `FileNotFoundError: .../airports.csv` | Package data not installed | Run from the source tree, or apply the `package-data` fix above |
| `FileNotFoundError: 'nmcli'` | NetworkManager not present | Skip `GetLocation` and pass coordinates directly |
| `GetLocation` exits with status 1 | No Wi-Fi networks visible | Enable Wi-Fi, or pass coordinates directly |
| `AirportInfo` returns `(None, None, None)` | Airport publishes no METAR | Use a large airport ICAO code such as `LKPR` |
| Aircraft functions return nothing | OpenSky rate limit reached | Wait a few minutes and reduce the polling frequency |

---

## Contributing

Contributions are welcome. Please keep the existing shape of the library: one module per capability, one public `get()` function per module, plain dictionaries as return values, and no mandatory API keys.

1. Fork the repository and create a branch for your change.
2. Keep changes focused; one fix or feature per pull request.
3. Describe how you tested the change, including the coordinates or ICAO codes used.

Bug reports should state your operating system, Python version, the module involved, and the output produced with `VERBOSE=True`.

---

## License

Released under the MIT License. See [LICENSE](LICENSE) for the full text.

Copyright (c) 2026 David Machek.

The bundled airport data and the third-party services listed above are covered by their own respective terms.
