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

def plotTemperatureData(grid_data):
    min_temperature_data = grid_data["minTemperature"]["values"]
    max_temperature_data = grid_data["maxTemperature"]["values"]

    ## Calculate Mean Temperature Data
    mean_temperature_data = list(map(
        lambda zip_temp_data : 
            {
                "validTime":zip_temp_data[0]["validTime"], 
                "value":(zip_temp_data[0]["value"] + zip_temp_data[1]["value"]) / 2
            }, 
        zip(min_temperature_data, max_temperature_data)
        )
    )
    
    def apiToDateTime(api_date : str) -> datetime:
        iso_date = api_date.split("/")[0]
        return datetime.fromisoformat(iso_date)

    def getDaysAhead(date : datetime) -> int:
        return date.toordinal() - datetime.now().toordinal()

    def convertTime(api_date : str) -> float:
        datetime_date = apiToDateTime(api_date)
        days_ahead = getDaysAhead(datetime_date)
        hour_percent = datetime_date.time().hour / 24
        value = float(days_ahead)  + hour_percent
        return value

    fig, temperature_ax = plt.subplots()

    def mapTemperatureData(label : str, temperature_data : list) -> None:
        temp_values = np.array(list(map(lambda x : float(x["value"]), temperature_data)))
        temp_time_values = np.array(list(map(lambda x : convertTime(x["validTime"]), temperature_data)))
        temperature_ax.plot(temp_time_values, temp_values, label=label)

    mapTemperatureData("Maximum Daily Temperature", max_temperature_data)
    mapTemperatureData("Mean Temperature", mean_temperature_data)
    mapTemperatureData("Minimum Daily Temperature", min_temperature_data)

    temperature_ax.set_xlabel('Forecast Ahead (no. Days)')
    temperature_ax.set_ylabel('Temperature (degrees C)')
    temperature_ax.set_title('Min and Max Temperatures')

    plt.legend()
    plt.show()

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
    
    # Get Data
    grid_data = forecast_grid_response.json()["properties"]
    
    # Plot
    plotTemperatureData(grid_data)
    


main()

# example coords : 38.8894, -77.0352
# example call : python weather_api_task.py 38.8894 -77.0352

# Statue of Liberty Coords : 40.4121 -74.0240
# python weather_api_task.py 40.4121 -74.0240