from statistics import mean
from dataProcessement.processingConstants import fotoCasaConstants
import random

class FotocasaDataProcessor():

    """
    This class process the data to the proper format for the DB and the modeling the data comes
    from a dictionary constructed by the FotoCasaScrapper pulling data from the Internet
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
            "price":None,
            "predictedprice":None,
            "zone":None,
            "nbedrooms":None,
            "nbathrooms":None,
            "size":None,
            "floor":None,
            "typology":None,
            "status":None,
            "antiquity":None,
            "elevator":None,
            "orientation":None,
            "parking":None,
            "furnished":None,
            "heating":None,
            "hotwater":None,
            "tags":None,
            "description":None,
            "airconditioning":None,
            "terrace":None,
            "kitchen":None,
            "parquet":None
        }

    def processPrice(self):
        self.houseInfoDictProcessed["price"] = int(self.houseInfoDict["price"])

    def processZone(self):
        self.houseInfoDictProcessed["zone"] = fotoCasaConstants["zonesDict"][self.houseInfoDict["zone"]]

    def processnBedrooms(self):
        if self.houseInfoDict["nbedrooms"] != None:
            intNbedrooms = int(self.houseInfoDict["nbedrooms"].split(" ")[0])
        else:
            intNbedrooms = fotoCasaConstants['nBedroomsAverage']

        self.houseInfoDictProcessed["nbedrooms"] = intNbedrooms

    def processnBathrooms(self):
        if self.houseInfoDict["nbathrooms"] != None:
            intNbathrooms = int(self.houseInfoDict["nbathrooms"].split(" ")[0])
        else:
            intNbathrooms = fotoCasaConstants['nBathroomsAverage']

        self.houseInfoDictProcessed["nbathrooms"] = intNbathrooms

    def processSize(self):
        if self.houseInfoDict["size"] != None:
            intSize = int(self.houseInfoDict["size"].split(" ")[0])
        else:
            intSize = fotoCasaConstants['sizeAverage']

        self.houseInfoDictProcessed["size"] = intSize

    def processFloor(self):
        if self.houseInfoDict["floor"] != None:
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
                    self.houseInfoDictProcessed["floor"] = int(self.houseInfoDict["floor"].split("th")[0])
        else:
            self.houseInfoDictProcessed["floor"] = random.randint(2, 6)

    def processTypology(self):
        if self.houseInfoDict["typology"] != None:
            typology = self.houseInfoDict["typology"].replace("Typology", "")
            if typology == "Flat":
                typologyInt = 0
            else:
                typologyInt = 1
        else:
            typologyInt = 0

        self.houseInfoDictProcessed["typology"] = typologyInt

    def processStatus(self):
        if self.houseInfoDict["status"] != None:
            status = self.houseInfoDict["status"].replace("Status","")
            if status == "good":
                self.houseInfoDictProcessed["status"] = 1
            elif status == "Almost new" or status == "Very good":
                self.houseInfoDictProcessed["status"] = 2
            else:
                self.houseInfoDictProcessed["status"] = 0
        else:
            self.houseInfoDictProcessed["status"] = 1

    def processAntiquity(self):
        if self.houseInfoDict["antiquity"] != None:
            pre = self.houseInfoDict["antiquity"].replace("Antiquity", "")
            self.houseInfoDictProcessed["antiquity"] = int(mean([int(a) for a in pre.split() if a.isdigit()]))
        else:
            self.houseInfoDictProcessed["antiquity"] = fotoCasaConstants["antiquityAverage"]

    def processElevator(self):
        if self.houseInfoDict["elevator"] != None:
            if "Yes" in self.houseInfoDict["elevator"]:
                self.houseInfoDictProcessed["elevator"] = 1
            else:
                self.houseInfoDictProcessed["elevator"] = 0
        else:
            self.houseInfoDictProcessed["elevator"] = 0

    def processOrientation(self):
        if self.houseInfoDict["orientation"] != None:
            self.houseInfoDictProcessed["orientation"] = self.houseInfoDict["orientation"].replace("Orientation", "")

    def processParking(self):
        if self.houseInfoDict["parking"] != None:
            parking = self.houseInfoDict["parking"].replace("Parking", "")
            if parking == "Community":
                self.houseInfoDictProcessed["parking"] = 1
            else:
                self.houseInfoDictProcessed["parking"] = 2
        else:
            self.houseInfoDictProcessed["parking"] = 0

    def processFurnished(self):
        if self.houseInfoDict["furnished"] != None:
            self.houseInfoDictProcessed["furnished"] = self.houseInfoDict["furnished"].replace("Furnished", "")

    def processHeating(self):
        if self.houseInfoDict["heating"] != None:
            self.houseInfoDictProcessed["heating"] = self.houseInfoDict["heating"].replace("Heating", "")

    def processHotWater(self):
        if self.houseInfoDict["hotwater"] != None:
            self.houseInfoDictProcessed["hotwater"] = self.houseInfoDict["hotwater"].replace("Hot water", "")

    def processTags(self):
        tags = self.houseInfoDict["tags"]
        self.houseInfoDictProcessed["tags"] = tags

        if tags != None:
            if "Air Conditioning" in tags:
                self.houseInfoDictProcessed['airconditioning'] = 1
            else:
                self.houseInfoDictProcessed['airconditioning'] = 0
            if "Terrace" in tags:
                self.houseInfoDictProcessed['terrace'] = 1
            else:
                self.houseInfoDictProcessed['terrace'] = 0
            if "Fully equipped kitchen" in tags:
                self.houseInfoDictProcessed['kitchen'] = 1
            else:
                self.houseInfoDictProcessed['kitchen'] = 0
            if "Parquet flooring" in tags:
                self.houseInfoDictProcessed['parquet'] = 1
            else:
                self.houseInfoDictProcessed['parquet'] = 0
        else:
            self.houseInfoDictProcessed['airconditioning'] = 0
            self.houseInfoDictProcessed['terrace'] = 0
            self.houseInfoDictProcessed['kitchen'] = 0
            self.houseInfoDictProcessed['parquet'] = 0

    def processDescription(self):
        self.houseInfoDictProcessed["description"] = self.houseInfoDict["description"]

    def _processAll(self):
        # It executes all the "process..." functions of the class and returns the processed dictionary
        for str in dir(self):
            func = getattr(self, str)
            if str.startswith('process') and hasattr(func, '__call__'):
                # We only exectute the procces function for those attributes that are not "" in the dict
                if self.houseInfoDict[str.lower().replace("process","")] != "":
                    func()

        return self.houseInfoDictProcessed



