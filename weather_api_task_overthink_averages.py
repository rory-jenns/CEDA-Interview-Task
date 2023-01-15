import requests
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


WEATHER_ENDPOINT = "https://api.weather.gov/"

def verifyArguments(argc : int, argv : list) -> bool:
    # Check number of arguments
    if argc != 3:
        print("ERROR:",end=" ")
        if argc > 3:
            print("Too many arguments", end=" ")
        elif argc < 3:
            print("Not enough arguments",end=" ")
        print(f"(expected 2, got {argc-1})")

        return False
    
    # Check coords can be decimal types
    try:
        latitude = float(argv[1])
        longitude = float(argv[2])
    except:
        print("ERROR: Must be float Latitude and Longitude")
        return False

    # TODO different coordinate formats?
    
    return True

def getCoords(latitude : str, longitude : str) -> tuple[float]:
    return (float(latitude), float(longitude))

def validateResponse(response : requests.Response) -> bool:
    # check recieved good args
    if not response:
        print(response.text)
        return False

    return True

def main():

    valid_args = verifyArguments(len(sys.argv), sys.argv)
    if not valid_args:
        exit(1)

    latitude, longitude = getCoords(sys.argv[1], sys.argv[2])

    # Check Endpoint is up
    endpoint_response = requests.get(WEATHER_ENDPOINT)
    if not validateResponse(endpoint_response):
        print("Endpoint call problem")
        exit(1)

    # Construct the URL for API call to metadata
    # {x:.4f} takes the coordinate to 4 dp, rounded
    url_coords_extension = f"points/{latitude:.4f},{longitude:.4f}"
    metadata_url = WEATHER_ENDPOINT + url_coords_extension

    # API call and validation
    metadata_response = requests.get(metadata_url)
    if not validateResponse(metadata_response):
        print("Metadata call problem")
        exit(1)


    # Get URL for API call to forecast Grid from Metadata
    forecast_grid_url = metadata_response.json()["properties"]["forecastGridData"]

    # API call and validation
    forecast_grid_response = requests.get(forecast_grid_url)
    if not validateResponse(forecast_grid_response):
        print("Forecast call problem")
        exit(1)

    
    grid_data = forecast_grid_response.json()["properties"]
    min_temperature_data = grid_data["minTemperature"]["values"]
    max_temperature_data = grid_data["maxTemperature"]["values"]

    hourly_temperature_data = grid_data["temperature"]["values"]

    totals = {}
    means = []

    today = datetime.now()

    for record in hourly_temperature_data:
        # YYYY-MM-DD is 10 characters
        iso_date, time_valid_code = record["validTime"].split("/")
        days_ahead = datetime.fromisoformat(iso_date).toordinal() - today.toordinal()
        time_valid = int(time_valid_code[2:-1])

        temperature_value = record["value"]

        if days_ahead not in totals:
            totals[days_ahead] = {"time_recorded" : 0, "total_temperature" : 0 }
        totals[days_ahead]["time_recorded"] += time_valid
        totals[days_ahead]["total_temperature"] += temperature_value
    
    for days_ahead in totals.keys():
        means.append( 
            {
                "value" : totals[days_ahead]["total_temperature"]/
                    totals[days_ahead]["time_recorded"] , 
                "validTime" : days_ahead
            }
        )

    def convertTime(api_date):
        iso_date = api_date.split("/")[0]
        datetime_date = datetime.fromisoformat(iso_date)
        days_ahead = datetime_date.toordinal() - today.toordinal()
        hour_percent = datetime_date.time().hour / 24
        value = days_ahead + hour_percent
        return value

    def getTimePercent(api_date):
        print(api_date)
        return 0

    fig, temperature_ax = plt.subplots()

    def mapTemperatureData(label, temperature_data):
        temp_values = np.array(list(map(lambda x : float(x["value"]), temperature_data)))
        temp_time_values = np.array(list(map(lambda x : convertTime(x["validTime"]), temperature_data)))
        temperature_ax.plot(temp_time_values, temp_values, label=label)

    
    mapTemperatureData("Minimum Daily Temperature", min_temperature_data)
    mapTemperatureData("Maximum Daily Temperature", max_temperature_data)
    mapTemperatureData("Hourly Temperature", hourly_temperature_data)

    temperature_ax.plot(list(map(lambda x : x["validTime"], means)), list(map(lambda x : x["value"], means)), label="Mean Temperature")


    temperature_ax.set_xlabel('Days Ahead')
    temperature_ax.set_ylabel('Temperature (degrees C)')
    temperature_ax.set_title('Min and Max Temperatures')

    plt.show()


main()

# example coords : 38.8894, -77.0352
# example call : python weather_api_task.py 38.8894 -77.0352