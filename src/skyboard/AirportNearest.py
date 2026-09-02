import csv
import math
from pathlib import Path

def haversine(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * 6371 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def is_valid_airport(row):
    return (
        row["icao_code"].strip() != "" and
        row["type"] not in {"heliport", "closed"}
    )

def load_airports(csv_file, user_lat, user_lon):
    airports = []
    with open(csv_file, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row["latitude_deg"])
                lon = float(row["longitude_deg"])

                distance = haversine(user_lat, user_lon, lat, lon)
                row["distance_km"] = distance
                airports.append(row)
            except:
                continue
    return airports

def pick_nearest(airports):
    valid = [a for a in airports if is_valid_airport(a)]
    if not valid:
        return None
    return sorted(valid, key=lambda x: x["distance_km"])[0]

def pick_nearest_large(airports):
    valid = [
        a for a in airports
        if is_valid_airport(a) and a["type"] == "large_airport"
    ]
    if not valid:
        return None
    return sorted(valid, key=lambda x: x["distance_km"])[0]
def get(lat,lon,VERBOSE=False,ONLY_LARGE=False):
    if VERBOSE: print("AirportNearest * INFO: Loading airports")
    airports = load_airports(Path(__file__).resolve().parent / "airports.csv", lat, lon)
    if ONLY_LARGE == False:
        if VERBOSE: print("AirportNearest * INFO: Picking a nearest airport")
        nearest = pick_nearest(airports)
        if nearest is None:
            if VERBOSE: print("AirportNearest * INFO: Couldnt found nearest airport")
            if VERBOSE: print("AirportNearest * INFO: Returning none")
            return None
        else:
            if VERBOSE: print("AirportNearest * INFO: Returnig nearest airport")
            return {
                "distance_km": nearest["distance_km"],
                "name": nearest.get("name"),
                "icao_code": nearest.get("icao_code"),
                "municipality": nearest.get("municipality")
            }
    if ONLY_LARGE:
        if VERBOSE: print("AirportNearest * INFO: Picking a nearest large airport")
        nearest_large = pick_nearest_large(airports)
        if nearest_large is None:
            if VERBOSE: print("AirportNearest * INFO: Couldnt found nearest large airport")
            if VERBOSE: print("AirportNearest * INFO: Returning none")
            return None
        else:
            if VERBOSE: print("AirportNearest * INFO: Returnig nearest large airport")
            return {
                "distance_km": nearest_large["distance_km"],
                "name": nearest_large.get("name"),
                "icao_code": nearest_large.get("icao_code"),
                "municipality": nearest_large.get("municipality")
            }