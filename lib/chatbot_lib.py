
from lib import weather_lib
#import tracker_lib
from lib import ham


class Chatbot:
    def __init__(self):
        self.active_tracker = {}
        self.weather = weather_lib.Weather()
        #self.tracker = tracker_lib.Tracker()

    async def parse(self, command, params, adv_name, adv_lat, adv_lon):
        command = command.lower()

        if command in ["ping"]:
            return (adv_name, "pong")

        #elif command in ["track"]:
        #    await self.tracker.parse(command, params, contact, adv_name)

        elif command in ["weather"]:
            if len(params) == 0:
                if adv_lat != None and adv_lon != None:
                    weather_info = self.weather.getCurrentWeatherLatlon(adv_lat, adv_lon)
                    return (adv_name, weather_info)
                else:
                    return (adv_name, "No coordinates set for this node")
            elif len(params) == 1:
                p = params[0]
                if ham.isMaidenhead(p):
                    lat, lon = ham.maidenheadToLatLon(p)
                    weather_info = self.weather.getCurrentWeatherLatlon(lat, lon)
                    return (adv_name, weather_info)
                else:  
                    weather_info = self.weather.getCurrentWeatherCity(p)
                    return (adv_name, weather_info)
            
        elif command in ["forecast"]:
            if len(params) == 0:
                if adv_lat != None and adv_lon != None:
                    weather_info = self.weather.getForecastLatLon(adv_lat, adv_lon)
                    return (adv_name, weather_info)
                else:
                    return (adv_name, "No coordinates set for this node")
            elif len(params) == 1:
                p = params[0]
                if ham.isMaidenhead(p):
                    lat, lon = ham.maidenheadToLatLon(p)
                    weather_info = self.weather.getForecastLatLon(lat, lon)
                    return (adv_name, weather_info)
                else:  
                    weather_info = self.weather.getForecastCity(p)
                    return (adv_name, weather_info)