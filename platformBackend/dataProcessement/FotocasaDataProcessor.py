from statistics import mean

class FotocasaDataProcessor():

    """
    This class contains all the tools to process the data to the proper format for the DB
    coming from a dictionary pulled by the FotoCasaScrapper
    """

    def __init__(self, houseInfoDict, url, timeonline):

        try:
            if "now" in timeonline:
                _timeonline = 1
            else:
               _timeonline = int(timeonline.split(" ")[0])
        except ValueError as e:
            print(f"Data processement error in timeOnline: string to int: {e}")

        self.houseInfoDict = houseInfoDict
        self.houseInfoDictProcessed = {
            "url":url,
            "sold":0,
            "timeonline":_timeonline,
            "price":-1,
            "zone":"",
            "nbedrooms":"",
            "nbathrooms":"",
            "size":"",
            "floor":-1,
            "typology":"",
            "status":"",
            "antiquity":-1,
            "elevator":-1,
            "orientation":"",
            "parking":"",
            "furnished":"",
            "heating":"",
            "hotwater":"",
            "tags":"",
            "description":""
        }

    def processPrice(self):
        if "Ask" not in self.houseInfoDict["price"]:
            euros = (self.houseInfoDict["price"].split(" ")[0]).replace(".","")
            try:
               self.houseInfoDictProcessed["price"] = int(euros)
            except ValueError as e:
                print(f"Data processement error: string to int: {e}")
        else:
            self.houseInfoDictProcessed["price"] = 0

    def processZone(self):
        self.houseInfoDictProcessed["zone"] = self.houseInfoDict["zone"]

    def processnBedrooms(self):
        self.houseInfoDictProcessed["nbedrooms"] = self.houseInfoDict["nbedrooms"].split(" ")[0]

    def processnBathrooms(self):
        self.houseInfoDictProcessed["nbathrooms"] = self.houseInfoDict["nbathrooms"].split(" ")[0]

    def processSize(self):
        self.houseInfoDictProcessed["size"] = self.houseInfoDict["size"].split(" ")[0]

    def processFloor(self):
        if "Ground" in self.houseInfoDict["floor"]:
            self.houseInfoDictProcessed["floor"] = 0
        elif "st" in self.houseInfoDict["floor"]:
            self.houseInfoDictProcessed["floor"] = 1
        elif "nd" in self.houseInfoDict["floor"]:
            self.houseInfoDictProcessed["floor"] = 2
        elif "rd" in self.houseInfoDict["floor"]:
            self.houseInfoDictProcessed["floor"] = 3
        else:
            if "15" in self.houseInfoDict["floor"]:
                self.houseInfoDictProcessed["floor"] = 15
            else:
                self.houseInfoDictProcessed["floor"] = self.houseInfoDict["floor"].split("th")[0]

    def processTypology(self):
        self.houseInfoDictProcessed["typology"] = self.houseInfoDict["typology"].replace("Typology","")

    def processStatus(self):
        self.houseInfoDictProcessed["status"] = self.houseInfoDict["status"].replace("Status","")

    def processAntiquity(self):
        pre = self.houseInfoDict["antiquity"].replace("Antiquity", "")
        self.houseInfoDictProcessed["antiquity"] = mean([int(a) for a in pre.split() if a.isdigit()])

    def processElevator(self):
        if "Yes" in self.houseInfoDict["elevator"]:
            #Has elevator
            self.houseInfoDictProcessed["elevator"] = 1
        else:
            self.houseInfoDictProcessed["elevator"] = 0

    def processOrientation(self):
        self.houseInfoDictProcessed["orientation"] = self.houseInfoDict["orientation"].replace("Orientation", "")

    def processParking(self):
        self.houseInfoDictProcessed["parking"] = self.houseInfoDict["parking"].replace("Parking", "")

    def processFurnished(self):
        self.houseInfoDictProcessed["furnished"] = self.houseInfoDict["furnished"].replace("Furnished", "")

    def processHeating(self):
        self.houseInfoDictProcessed["heating"] = self.houseInfoDict["heating"].replace("Heating", "")

    def processHotWater(self):
        self.houseInfoDictProcessed["hotwater"] = self.houseInfoDict["hotwater"].replace("Hot water", "")

    def processTags(self):
        #TODO: Separate tags into actual features
        self.houseInfoDictProcessed["tags"] = self.houseInfoDict["tags"]

    def processDescription(self):
        self.houseInfoDictProcessed["description"] = self.houseInfoDict["description"]

    def _processAll(self):
        # It executes all the functions of the class and returns the processed dictionary
        for str in dir(self):
            func = getattr(self, str)
            if str.startswith('process') and hasattr(func, '__call__'):
                # We only exectute the procces function for those attributes that are not "" in the dict
                if self.houseInfoDict[str.lower().replace("process","")] != "":
                    func()

        return self.houseInfoDictProcessed



