import os
from datetime import datetime 

import requests
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

class Weather:
    def __init__(self):
        self.OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY") 

    def __getEmoji(self, text):
        emojiDict = {"clear sky":"☀️", 
                 "few clouds":"🌤️", 
                 #"scattered clouds":"⛅", 
                 "broken clouds":"☁️",
                 "shower rain":"🌧️",
                 "rain":"🌧️",
                 "thunderstom":"🌩️",
                 "snow":"🌨️",
                 "mist":"🌫️",
                "thunderstorm with light rain":"⛈️", 
                "thunderstorm with rain":"⛈️", 
                "thunderstorm with heavy rain":"⛈️", 
                "light thunderstorm":"⛈️", 
                "thunderstorm":"⛈️", 
                "heavy thunderstorm":"⛈️", 
                "ragged thunderstorm":"⛈️", 
                "thunderstorm with light drizzle":"⛈️", 
                "thunderstorm with drizzle":"⛈️", 
                "thunderstorm with heavy drizzle":"⛈️", 
                "light intensity drizzle":"🌦️",
                "drizzle":"🌦️", 	
                "heavy intensity drizzle":"🌦️", 	
                "light intensity drizzle rain":"🌦️", 	
                "drizzle rain":"🌦️", 	
                "heavy intensity drizzle rain":"🌦️", 	
                "shower rain and drizzle":"🌦️", 	
                "heavy shower rain and drizzle":"🌦️", 	
                "shower drizzle":"🌦️",
                "light rain":"🌧️",
                "moderate rain":"🌧️",
                "heavy intensity rain":"🌧️",
                "very heavy rain":"🌧️",
                "extreme rain":"🌧️",
                "freezing rain":"❄️🌧️",
                "light intensity shower rain":"🌧️",
                "shower rain":"🌧️",
                "heavy intensity shower rain":"🌧️",
                "ragged shower rain":"🌧️",
                "light snow":"🌨️",
                "snow":"🌨️",
                "heavy snow":"🌨️",
                "sleet":"🌨️",
                "light shower sleet":"🌨️",
                "shower sleet":"🌨️",
                "light rain and snow":"🌨️",
                "rain and snow":"🌨️",
                "light shower snow":"🌨️",
                "shower snow":"🌨️",
                "heavy shower snow":"🌨️",
                "mist":"🌫️",
                "smoke":"🌫️",
                "haze":"🌫️",
                "sand/dust whirls":"🌫️",
                "fog":"🌫️",
                "sand":"🌫️",
                "dust":"🌫️",
                "volcanic ash":"🌋",
                "squalls":"⛈️",
                "tornado":"🌪️",
                "clear sky":"☀️",
                "few clouds":"☁️",
                "scattered clouds":"☁️",
                "broken clouds":"☁️",
                "overcast clouds":"☁️",
                 }
        if text in emojiDict:
            return emojiDict[text]
        else:
            return text

    def __formatWeather(self, resp):
        res = ""
        res += self.__getEmoji(resp["weather"][0]["description"]) + " "
        res += resp["name"] + "\n"
        res += "🌡️" + str(resp["main"]["temp"]) + "˚C\n"
        res += "🌫️" + str(resp["main"]["humidity"]) + r"%rh" + "\n"
        res += "🌬️" + str(resp["wind"]["speed"]) + "m/s\n"
        if "rain" in resp:
            res += "💦" + str(resp["rain"]["1h"]) + "mm/h\n"
        sunrise = datetime.fromtimestamp(resp["sys"]["sunrise"]).strftime("%H:%M:%S")
        sunset  = datetime.fromtimestamp(resp["sys"]["sunset"]).strftime("%H:%M:%S")
        res += "🌅" + sunrise + "\n"
        res += "🌄" + sunset + "\n"
        #print(res)
        return res
    
    def __formatForecast(self, resp):
        nr = 0
        res = ""
        res += resp["city"]["name"] + "\n"
        if "list" in resp: 
            for i in resp["list"]:
                if nr <= 7:
                    date_str = datetime.fromtimestamp(i["dt"]).strftime('%H')
                    res += date_str + "h "
                    res += self.__getEmoji(i["weather"][0]["description"]) + " "
                    res += str(round(i["main"]["temp"],1)) + "C \n"
                nr += 1
            
            return res
        return None

    def getCurrentWeatherLatlon(self, lat, lon):
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=en&appid={self.OPENWEATHERMAP_API_KEY}"
        resp = requests.get(url, timeout=5).json()
        return self.__formatWeather(resp)    
    
    def getCurrentWeatherCity(self, city):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=en&appid={self.OPENWEATHERMAP_API_KEY}"
        resp = requests.get(url, timeout=5).json()
        return self.__formatWeather(resp)    

    def getForecastLatLon(self, lat, lon):
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&lang=en&appid={self.OPENWEATHERMAP_API_KEY}"
        resp = requests.get(url, timeout=5).json()

        return self.__formatForecast(resp)

    def getForecastCity(self, city):
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&lang=en&appid={self.OPENWEATHERMAP_API_KEY}"
        resp = requests.get(url, timeout=5).json()

        return self.__formatForecast(resp)