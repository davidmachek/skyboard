from SkyBoard import AircraftInfo,AircraftNearest,AircraftTotal,AirportInfo,AirportNearest,GetLocation

VERBOSE = False
ONLY_LARGE = True

location = GetLocation.get(VERBOSE=VERBOSE)
print("Tvoje Lokalita: ",location)
nearest_airport = AirportNearest.get(location["lat"],location["lng"],VERBOSE=VERBOSE,ONLY_LARGE=ONLY_LARGE)
print("Nejblizsi Letiste: ", nearest_airport)

info_about_airport = AirportInfo.get(nearest_airport["icao_code"],VERBOSE=VERBOSE)
print("Informace o Letisti: ",info_about_airport)

aircraft_count = AircraftTotal.get(nearest_airport["icao_code"],VERBOSE=VERBOSE)
print("Celkem letadel na Letisti: ",aircraft_count)

nearest_plane = AircraftNearest.get(location["lat"],location["lng"],VERBOSE=VERBOSE)
print("Nejblizsi letadlo: ",nearest_plane)

info_about_plane = AircraftInfo.get(nearest_plane["callsign"],VERBOSE=VERBOSE)
print("Informace o letadlu: ",info_about_plane)