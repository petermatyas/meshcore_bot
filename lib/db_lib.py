import time
import json

class Db:
    def __init__(self):
        pass

    def savePosition(self, adv_name:str, latitude:float, longitude:float, altitude:float):
        aa = {"ts":time.time(), "adv_name":adv_name, "latitude":latitude, "longitude":longitude, "altitude":altitude}
        with open('mc_coordinates.csv', 'a', newline='') as csvfile:
            fieldnames = ["ts", "adv_name", "latitude", "longitude", "altitude"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(aa)

    def saveMessage(self, package):
        with open("mc_log.jsonl", mode='a', encoding='utf-8') as file:
            data = {'ts': time.time(), 'package': package}
            file.write(json.dumps(data))
            file.write("\n")

    def saveTelemetry(self, adv_name:str, telemetry:dict):
        with open("mc_telemetry.jsonl", mode='a', encoding='utf-8') as file:
            data = {'ts': time.time(), "adv_name":adv_name, 'package': telemetry}
            file.write(json.dumps(data))
            file.write("\n")