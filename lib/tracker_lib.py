


class Tracker:
    def __init__(self):
        self.active_tracker = {}

    def setTracker(self, name, interval=10):
        self.active_tracker[name] = {"interval":interval, "last_time":0, "last_lat":0, "last_lon":0}

    def activeTracker(self, name):
        return name in self.active_tracker.keys()

    def getTracker(self, name):
        return self.active_tracker[name]
    
    def getTrackers(self):
        return self.active_tracker

    def delTracker(self, name):
        self.active_tracker.pop(name)

    async def parse(self, command, params, contact, adv_name):
        answer = ""
        if len(params) == 0:
            answer = "tracking: " + "active" if self.activeTracker(adv_name) else "inactive"
        elif len(params) == 1 or len(params) == 2:
            if len(params) == 1:
                interval = 10
            else:
                interval = params[1]

            if params[0] == "on":
                self.setTracker(adv_name, interval)
            elif params[0] == "off":
                self.delTracker(adv_name)
            else:
                answer = "wrong parameter"
        else:
            answer = "parameter error"
    
        if answer != "":
            await sendMessage(contact, answer)