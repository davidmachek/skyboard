import requests
import csv
from pathlib import Path
def load_airport(icao_code, csv_file=Path(__file__).resolve().parent / "airports.csv"):
    try:
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (row.get("icao_code") or "").strip().upper() == icao_code.upper():
                    return float(row["latitude_deg"]), float(row["longitude_deg"])
    except:
        return None, None

    return None, None

def make_bbox(lat, lon, size_deg=0.2):
    return {
        "lamin": lat - size_deg,
        "lamax": lat + size_deg,
        "lomin": lon - size_deg,
        "lomax": lon + size_deg
    }

def get_states(bbox):
    try:
        r = requests.get("https://opensky-network.org/api/states/all", params=bbox, timeout=10)
        if r.status_code != 200:
            return None
        return r.json().get("states", None)
    except:
        return None

def get(icao,VERBOSE=False):
    try:
        lat, lon = load_airport(icao)
        if lat is None or lon is None:
            if VERBOSE: print("AicraftTotal * INFO: Unknow")
            if VERBOSE: print("AicraftTotal * INFO: Returning none")
            return
        if VERBOSE: print("AicraftTotal * INFO: Making BBOX")
        bbox = make_bbox(lat, lon)
        if VERBOSE: print("AicraftTotal * INFO: Getting States")
        states = get_states(bbox)

        if states is None:
            if VERBOSE: print("AicraftTotal * INFO: Unknow")
            if VERBOSE: print("AicraftTotal * INFO: Returning none")
            return
        aircraft_count = len(states)
        if VERBOSE: print("AicraftTotal * INFO: Returning aircraft count")
        return {"count":aircraft_count}

    except:
        if VERBOSE: print("AicraftTotal * INFO: Unknow")