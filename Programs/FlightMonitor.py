import requests
import time
import csv
from pathlib import Path
POLL_INTERVAL = 5
def load_airport(icao_code, csv_file=Path(__file__).resolve().parent / "../airports.csv"):
    try:
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (row.get("icao_code") or "").strip().upper() == icao_code.upper():
                    return {
                        "name": row.get("name"),
                        "lat": float(row["latitude_deg"]),
                        "lon": float(row["longitude_deg"])
                    }
    except:
        return None
    return None

def make_bbox(lat, lon, size_deg=0.2):
    return {
        "lamin": lat - size_deg,
        "lamax": lat + size_deg,
        "lomin": lon - size_deg,
        "lomax": lon + size_deg
    }

def fetch_states(bbox):
    try:
        r = requests.get("https://opensky-network.org/api/states/all", params=bbox, timeout=10)
        if r.status_code != 200:
            return None
        return r.json().get("states", None)
    except: return None

def parse(state):
    try:
        return {
            "icao24": state[0],
            "callsign": (state[1] or "").strip(),
            "country": state[2],
            "lon": state[5],
            "lat": state[6],
            "alt": state[7],
            "on_ground": state[8],
            "velocity": state[9]
        }
    except:
        return None
def mps_to_kts(mps):
    try: return mps * 1.94384 if mps else 0
    except: return 0

def detect_event(now, old):
    try:
        if not old:
            return None
        now_g = now["on_ground"]
        old_g = old["on_ground"]

        now_v = mps_to_kts(now["velocity"])
        old_v = mps_to_kts(old["velocity"])
        if old_g and not now_g and now_v > 40:
            return f"TAKEOFF: {now['callsign']} | {now_v:.0f} kts"

        if not old_g and now_g:
            return f"LANDING: {now['callsign']} | {old_v:.0f} → 0 kts"

        return None
    except:
        return None

def run(icao_code):
    try:
        airport = load_airport(icao_code)
        if not airport:
            print("Unknown")
            return
        print(f"Tracking: {airport['name']} ({icao_code})")
        bbox = make_bbox(airport["lat"], airport["lon"])
        prev = {}

        while True:
            states = fetch_states(bbox)
            if not states:
                print("Unknown")
                time.sleep(POLL_INTERVAL)
                continue

            for s in states:
                a = parse(s)
                if not a:
                    continue
                icao = a["icao24"]
                old = prev.get(icao)

                event = detect_event(a, old)
                if event:
                    print(event)
                prev[icao] = a

            time.sleep(POLL_INTERVAL)
    except:
        print("Unknown")