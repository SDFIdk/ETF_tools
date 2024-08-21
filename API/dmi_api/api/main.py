from datetime import datetime
import os
import sys
import netrc

from dmi_open_data import DMIOpenDataClient, Parameter, ClimateDataParameter


# Get 10 stations
_, _, api_key = netrc.netrc().authenticators('dmi_climate_data_api')

client = DMIOpenDataClient(api_key=api_key)
stations = client.get_stations(limit=10)

# Get all stations
stations = client.get_stations()

print(stations)

sys.exit()

# Get DMI station
dmi_station = next(
    station
    for station in stations
    if station['properties']['name'].lower() == 'dmi')

# Get closest station
closest_station = client.get_closest_station(
    latitude=55.707722,
    longitude=12.562119)

# Get available parameters
parameters = client.list_parameters()

# Get temperature observations from DMI station in given time period
observations = client.get_observations(
    parameter=Parameter.TempDry,
    station_id=dmi_station['properties']['stationId'],
    from_time=datetime(2021, 7, 20),
    to_time=datetime(2021, 7, 24),
    limit=1000)

# Init climate data client
climate_data_client = DMIOpenDataClient(api_key=os.getenv('DMI_CLIMATE_DATA_API_KEY'))

# Get climate data
climate_data = climate_data_client.get_climate_data(
    parameter=ClimateDataParameter.MeanTemp,
    station_id=dmi_station['properties']['stationId'],
    from_time=datetime(2021, 7, 20),
    to_time=datetime(2021, 7, 24),
    time_resolution='day',
    limit=1000)