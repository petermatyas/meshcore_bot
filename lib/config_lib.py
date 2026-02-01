import json
import time

class Config:
    def __init__(self, configPath, logger):
        self.configFilePath = configPath
        self.config = list()
        self.logger = logger

        self.queryIntervals = dict()
        self.discover = dict()

    def __readConfig(self):
        try:
            with open(self.configFilePath, "r") as json_data:
                data = json.load(json_data)
                self.config = data

        except Exception as e:
            self.logger.error(f"Config read error: {e}")

    def getUsbPid(self):
        self.__readConfig()
        return self.config["usb"]["pid"]

    def getUsbVid(self):
        self.__readConfig()
        return self.config["usb"]["vid"]

    def getChannels(self):
        self.__readConfig()
        return self.config["channels"]

    def getContactSaveInterval(self):
        self.__readConfig()
        return self.config["contacts_save"]["interval_s"]

    def getContactSaveFilename(self):
        self.__readConfig()
        return self.config["contacts_save"]["filename"]
    
    def getPathByName(self, adv_name):
        aa = self.getTelemetryList()
        for i in aa:
            if i["adv_name"] == adv_name:
                if not "path" in i:
                    return None
                return i["path"]
        return None

    def getTelemetryList(self):
        self.__readConfig()
        return self.config["save"]
    
    def isQuery(self, adv_name, query):
        for node in self.config["save"]:
            if node["adv_name"] == adv_name:
                for q in node["querys"]:
                    if q["query"] == query and "active" in q and q["active"] == True:
                        return True
        return False
            
    def getQueryInterval(self, adv_name, query):
        for node in self.config["save"]:
            if node["adv_name"] == adv_name:
                for q in node["querys"]:
                    if q["query"] == query:
                        return q["interval"]
        return None
    
    def isQueryTrigger(self, adv_name, query):
        if not adv_name in self.queryIntervals:
            self.queryIntervals[adv_name] = dict()
        if not query in self.queryIntervals[adv_name]:    
            self.queryIntervals[adv_name][query] = 0
        
        if time.time() - self.queryIntervals[adv_name][query] > self.getQueryInterval(adv_name, query):
            return True
        
        return False
        
    def queryTriggered(self, adv_name, query):
        if not adv_name in self.queryIntervals:
            self.queryIntervals[adv_name] = dict()
        self.queryIntervals[adv_name][query] = time.time()

    def isDiscovered(self, adv_name:str):
        if not adv_name in self.discover:
            self.discover[adv_name] = {"discovered":None, "path":""}
        
        return self.discover[adv_name]["discovered"]
        
    def setDiscover(self, adv_name:str, discover:bool):
        self.discover[adv_name]["discovered"] = discover


