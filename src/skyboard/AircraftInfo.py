import requests


def get(callsign: str, VERBOSE=False):
    callsign = callsign.strip().upper()
    try:
        if VERBOSE: print("AircraftInfo * INFO: Requesting Data")
        data = requests.get("https://opensky-network.org/api/states/all", timeout=10).json()
    except Exception as e:
        if VERBOSE: print("AircraftInfo * ERROR: API: ",e)
        if VERBOSE: print("AircraftInfo * INFO: Returning none")
        return None

    for s in data.get("states", []):

        if s[1] and s[1].strip() == callsign:

            if VERBOSE: print("AircraftInfo * INFO: Returning data")
            return {
                "callsign": s[1].strip(),
                "country": s[2],
                "lat": s[6],
                "lon": s[5],
                "speed": s[9],
                "heading": s[10],
            }

    return None