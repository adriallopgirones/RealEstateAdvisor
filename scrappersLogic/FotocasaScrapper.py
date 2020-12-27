from ScrappersLogic.RealEstateScrapper import RealEstateScrapper
from selenium.webdriver.common.keys import Keys
import time

class FotocasaScrapper(RealEstateScrapper):
    def __init__(self, baseUrl, cityToScrape):
        self.baseUrl = baseUrl
        self.cityToScrape = cityToScrape

    def buildUrlForCity(self):
        if self.cityToScrape == "barcelona":
            url = f"{self.baseUrl}/barcelona-capital/all-zones/l"

        return url

    def buildUrlForHouse(self, houseUrl):
        houseUrlFixed = houseUrl.split("home")[1]
        url = f"{self.baseUrl}{houseUrlFixed}"

        return url

    def getHousesListUrls(self):
        """
        This functions scrapes the links for a list of houses in the webpage
        :return: A list with links to houses' info
        """

        housesListUrls  = []

        seleniumDriver = super().doRequestsSelenium()

        try:
            seleniumDriver.get(self.buildUrlForCity())
        except ConnectionError as e:
            print(f"Scrapper error: ConnectionError: {e}")
        # Scrolling to the bottom of the webpage to load Javascript
        totalHeight = int(seleniumDriver.execute_script("return document.body.scrollHeight"))
        for i in range(1, totalHeight, 5):
            seleniumDriver.execute_script("window.scrollTo(0, {});".format(i))

        soup = super().getBeautifulSoup(seleniumDriver.page_source)
        if len(soup.select("div.re-Card-primary a")) > 0:
            for link in soup.select("div.re-Card-primary a"):
                housesListUrls.append(link["href"])
            return housesListUrls
        else:
            raise Exception("There is no links in this page")

    def getHouseInfo(self, houseUrl):
        """
        This functions scrapes all the information of the house specifed in the url
        :param houseUrl:
        :return: A dictionary with the house's features
        """
        url = self.buildUrlForHouse(houseUrl)
        html = super().doRequestRequestsHtml(url)
        soup = super().getBeautifulSoup(html)
        houseInfoDict = {
            "price":"",
            "zone":"",
            "nBedrooms":"",
            "nBathrooms":"",
            "size":"",
            "floor":"",
            "typology":"",
            "status":"",
            "antiquity":"",
            "elevator":"",
            "orientation":"",
            "parking":"",
            "furnished":"",
            "heating":"",
            "hotWater":"",
            "tags":""

        }

        # Getting all the features from the soup
        price = soup.find("span", class_="re-DetailHeader-price")
        if price is not None:
            houseInfoDict["price"] = price.get_text()
        zone = soup.find("span", class_="re-Breadcrumb-text")
        if zone is not None:
            houseInfoDict["zone"] = zone.get_text()
        if len(soup.select("li.re-DetailHeader-featuresItem span")) > 0:
            for span in soup.select("li.re-DetailHeader-featuresItem span"):
                if "bdrm" in span.get_text():
                    houseInfoDict["nBedrooms"] = span.get_text()
                elif "bathroom" in span.get_text():
                    houseInfoDict["nBathrooms"] = span.get_text()
                elif "sqm" in span.get_text():
                    houseInfoDict["size"] = span.get_text()
                elif "floor" in span.get_text():
                    houseInfoDict["floor"] = span.get_text()

        if len(soup.select("div.re-DetailFeaturesList-featureContent")) > 0:
            divsWithFeatures = soup.select("div.re-DetailFeaturesList-featureContent")
            for div in divsWithFeatures:
                if "Typology" in div.get_text():
                    houseInfoDict["typology"] = div.get_text()
                elif "Status" in div.get_text():
                    houseInfoDict["status"] = div.get_text()
                elif "Antiquity" in div.get_text():
                    houseInfoDict["antiquity"] = div.get_text()
                elif "Elevator" in div.get_text():
                    houseInfoDict["elevator"] = div.get_text()
                elif "Orientation" in div.get_text():
                    houseInfoDict["orientation"] = div.get_text()
                elif "Parking" in div.get_text():
                    houseInfoDict["parking"] = div.get_text()
                elif "Furnished" in div.get_text():
                    houseInfoDict["furnished"] = div.get_text()
                elif "Heating" in div.get_text():
                    houseInfoDict["heating"] = div.get_text()
                elif "Hot water" in div.get_text():
                    houseInfoDict["hotWater"] = div.get_text()

        if len(soup.select("li.re-DetailExtras-listItem")) > 0:
            tagStringBuilder = ""
            for tag in soup.select("li.re-DetailExtras-listItem"):
                tagStringBuilder += f"{tag.get_text()},"
            houseInfoDict["tags"] = tagStringBuilder
        print(houseInfoDict)









