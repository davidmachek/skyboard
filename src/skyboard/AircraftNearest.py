import requests
import math

def distance_km(lat1, lon1, lat2, lon2,VERBOSE):
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    )
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get(LAT,LON,VERBOSE=False):
    if VERBOSE: print("AircraftNearest * INFO: Requesting nearest aircraft")
    response = requests.get("https://opensky-network.org/api/states/all", timeout=10)
    response.raise_for_status()
    if VERBOSE: print("AircraftNearest * INFO: Responded")
    data = response.json()
    aircraft = []
    for state in data.get("states", []):
        callsign = (state[1] or "").strip()
        longitude = state[5]
        latitude = state[6]
        if latitude is None or longitude is None:
            continue
        distance = distance_km(
            LAT,
            LON,
            latitude,
            longitude,
            VERBOSE
        )
        aircraft.append({
            "callsign": callsign or "UNKNOWN",
            "icao24": state[0],
            "lat": latitude,
            "lon": longitude,
            "distance": distance,
            "altitude": state[7],
            "velocity": state[9],
            "heading": state[10],
        })
    if not aircraft:
        if VERBOSE: print("AircraftNearest * INFO: Aircraft not founded. returning none")
        return False, False
    else:
        nearest = min(aircraft, key=lambda x: x["distance"])
        if VERBOSE: print("AircraftNearest * INFO: Returning nearest aircraft")
        return {
            "callsign": nearest['callsign'],
            "distance": f"{nearest['distance']:.2f}"
        }