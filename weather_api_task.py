import requests
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


## CMD Arguments

argc = len(sys.argv)

if argc > 3:
    print("Too many arguments\n")
    exit(1)
if argc < 3:
    print("Not enough arguments\n")
    exit(1)

try:
    latitude = float(sys.argv[1])
    longitude = float(sys.argv[2])
except:
    print("Must be decimal Latitude and Longitude")
    exit(1)


## METADATA

BASE_URL = "https://api.weather.gov/"
# 4 dp maximum !
metadata_url = BASE_URL + f"points/{latitude:.4f},{longitude:.4f}"
metadata_response = requests.get(metadata_url)

if not metadata_response:
    print("metadata problem!")
    exit(1)

forecast_grid_url = metadata_response.json()["properties"]["forecastGridData"]
forecast_grid_response = requests.get(forecast_grid_url)

if not forecast_grid_response:
    # print(forecast_grid_url)
    # print(forecast_grid_response)
    print("forecast problem")
    exit(1)


grid_data = forecast_grid_response.json()["properties"]

min_temperature_data = grid_data["minTemperature"]["values"]
max_temperature_data = grid_data["maxTemperature"]["values"]

def convertTime(api_date):
    iso_date = api_date.split("/")[0]
    datetime_date = datetime.fromisoformat(iso_date)
    res = datetime_date.toordinal()
    return res

min_temp_values = np.array(list(map(lambda x : float(x["value"]), min_temperature_data)))
min_temp_time_values = np.array(list(map(lambda x : convertTime(x["validTime"]), min_temperature_data)))

max_temp_values = np.array(list(map(lambda x : float(x["value"]), max_temperature_data)))
max_temp_time_values = np.array(list(map(lambda x : convertTime(x["validTime"]), max_temperature_data)))

fig, temp_ax = plt.subplots()
temp_ax.plot(max_temp_time_values, max_temp_values)
temp_ax.plot(min_temp_time_values, min_temp_values)

temp_ax.set_xlabel('Ordinal Day (?)')
temp_ax.set_ylabel('Temperature (degrees C)')
temp_ax.set_title('Min and Max Temperatures')

plt.show()
