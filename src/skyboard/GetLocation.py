import subprocess, json, platform, re, requests

def scan_wifi(VERBOSE):
    aps = []
    sys = platform.system()
    if VERBOSE: print("GetLocation * INFO: Starting NetworkManager(nmcli) to scan Wi-Fi networks")
    out = subprocess.check_output(
        ["nmcli", "-t", "-f", "BSSID,SIGNAL", "dev", "wifi", "list"],
        text=True
    )
    for line in out.strip().splitlines():
        parts = line.split(":")
        m = re.match(r"^((?:[0-9A-Fa-f]{2}\\?:){5}[0-9A-Fa-f]{2}):(-?\d+)$", line)
        if m:
            mac = m.group(1).replace("\\", "")
            signal = int(m.group(2))
            aps.append({"macAddress": mac, "signalStrength": signal})

    return aps

def geolocate(aps,VERBOSE):
    url = "https://api.beacondb.net/v1/geolocate"
    payload = {"wifiAccessPoints": aps}
    headers = {"User-Agent": "my-geoloc-script/1.0"}
    r = requests.post(url, json=payload, headers=headers, timeout=10)
    r.raise_for_status()
    if VERBOSE: print("GetLocation * INFO: Returning Geolocate")
    return r.json()


def get(VERBOSE=False):
    if VERBOSE: print("GetLocation * INFO: Scanning Wi-Fi")
    aps = scan_wifi(VERBOSE)
    if VERBOSE: print(f"GetLocation * INFO: Founded {len(aps)} AP: {[a['macAddress'] for a in aps]}")

    if not aps:
        if VERBOSE: print("GetLocation * INFO: No WiFi networks found. try running as root or enable WiFi scanning")
        exit(1)
    if VERBOSE: print("GetLocation * INFO: Requesting BeaconDB")
    result = geolocate(aps,VERBOSE)

    loc = result.get("location", {})
    acc = result.get("accuracy", "?")
    lat = loc.get("lat", "?")
    lng = loc.get("lng", "?")
    if VERBOSE: print("GetLocation * INFO: Returning Location")
    return {
        "lat": lat,
        "lng": lng
    }