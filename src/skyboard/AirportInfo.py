import requests

def get(ICAO,VERBOSE=False):
    url = f"https://aviationweather.gov/api/data/metar?ids={ICAO}&format=json"
    try:
        if VERBOSE: print("AirportInfo * INFO: Connecting to aviationweather")
        r = requests.get(url, timeout=10)
        if r.status_code == 204:
            if VERBOSE: print("AirportInfo * INFO: aviationweather responded with HTTP status 204, returning None")
            return None,None,None
        if r.status_code != 200:
            if VERBOSE: print(f"AirportInfo * ERROR: aviationweather responded with HTTP status {r.status_code}")
            raise ValueError(f"HTTP {r.status_code}")

        data = r.json()
        if not data:
            if VERBOSE: print("AirportInfo * ERROR: aviationweather responded nothing")
            raise ValueError("Empty response")
        metar = data[0]

        temp = metar.get("temp", "UNKNOWN")
        wind_dir = metar.get("wdir", "UNKNOWN")
        wind_speed = metar.get("wspd", "UNKNOWN")
        if VERBOSE: print("AirportInfo * INFO: Received Data. returning it")
        return {
            "temp": temp,
            "wind_dir": wind_dir,
            "wind_speed": wind_speed
        }
    except Exception:
        return None,None,None