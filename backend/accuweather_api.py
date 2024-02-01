import json
import time
import urllib.request
import os
from dotenv import load_dotenv

## Get Env variables
load_dotenv()

accuweather_api_key = os.getenv("ACCUWEATHER_API_KEY")
city_seacrh_endpoint = "http://dataservice.accuweather.com/locations/v1/cities/search"


cityKey = ""

def getLocation(location):

    global cityKey

    location_endpoint = city_seacrh_endpoint + f"?apikey={accuweather_api_key}&q={location}&details=true"

    with urllib.request.urlopen(location_endpoint) as location_endpoint:
        data = json.loads(location_endpoint.read().decode())
        ## print("data : ",data)

    cityKey = data[0]['Key']
    print("cityKey is ",cityKey)

    return(cityKey)

def currentConditions(cityKey):

    currentConditions_endpoint = f"http://dataservice.accuweather.com/currentconditions/v1/{cityKey}?apikey={accuweather_api_key}&details=true"

    with urllib.request.urlopen(currentConditions_endpoint) as currentConditions_endpoint:
        data = json.loads(currentConditions_endpoint.read().decode())
        #print("Current Conditions are :", data)

    ## Extracting Necessary details

    # Ensure that the data is not empty and contains the expected structure
    if data and isinstance(data, list) and len(data) > 0:
        data = data[0]  # Assuming we're interested in the first item of the list

        # Extracting the required details
        localObservationDateTime = data.get("LocalObservationDateTime", "")
        weatherText = data.get("WeatherText", "")
        temperatureC = data.get("Temperature", {}).get("Metric", {}).get("Value", None)
        realFeelTemperatureC = data.get("RealFeelTemperature", {}).get("Metric", {}).get("Value", None)
        realFeelTemperaturePhrase = data.get("RealFeelTemperature", {}).get("Metric", {}).get("Phrase", "")
        windSpeedKmh = data.get("Wind", {}).get("Speed", {}).get("Metric", {}).get("Value", None)

        # Constructing a summary dictionary
        weather_summary = {
            "LocalObservationDateTime": localObservationDateTime,
            "WeatherText": weatherText,
            "TemperatureC": temperatureC,
            "RealFeelTemperatureC": realFeelTemperatureC,
            "RealFeelTemperaturePhrase": realFeelTemperaturePhrase,
            "WindSpeedKmh": windSpeedKmh
        }

        return weather_summary
    else:
        print("Data is empty or has an unexpected structure.")
        return {}


## def forecasts(timeFrame):
    ## timeFrame is a string object e.g '5 hours' or '3 days'.
    ## Extract number of hours or days to be forecasted

# if __name__ == '__main__' :
#     getLocation("Schweinfurt")
#     print(cityKey)
#     weather_summary = currentConditions(cityKey)
#     print(weather_summary)



