from scrappersLogic.RealEstateScrapper import RealEstateScrapper

class FotocasaScrapper(RealEstateScrapper):

    """
    This class contains all the necessary tools to scrape the webpage Fotocasa and fetch information about the listed
    houses there
    """

    def __init__(self, cityToScrape = "barcelona"):
        self.baseUrl = "https://www.fotocasa.es/en/buy/homes"
        self.cityToScrape = cityToScrape

    def buildUrlForCityandPage(self, nPage=1):
        if self.cityToScrape == "barcelona":
            if nPage == 1:
                    url = f"{self.baseUrl}/barcelona-capital/all-zones/l/sortType=publicationDate"
            else:
                url = f"{self.baseUrl}/barcelona-capital/all-zones/l/{nPage}?&sortType=publicationDate"
        return url

    def buildUrlForHouse(self, houseUrl):
        houseUrlFixed = houseUrl.split("home")[1]
        url = f"{self.baseUrl}{houseUrlFixed}"

        return url

    def getHousesListUrlsAndTimes(self, nPage=1):
        """
        This functions scrapes the links for a list of houses in the webpage
        :return: A list with links to houses' info
        """

        housesListUrls  = []
        housesListTimes = []

        seleniumDriver = super().doRequestsSelenium()

        try:
            seleniumDriver.get(self.buildUrlForCityandPage(nPage))
        except ConnectionError as e:
            print(f"Scrapper error: ConnectionError: {e}")

        # Scrolling to the bottom of the webpage to load the Javascript items
        totalHeight = int(seleniumDriver.execute_script("return document.body.scrollHeight"))
        for i in range(1, totalHeight, 5):
            seleniumDriver.execute_script("window.scrollTo(0, {});".format(i))

        # Fetching the links for each house in the link
        soup = super().getBeautifulSoup(seleniumDriver.page_source)
        if len(soup.select("div.re-Card-primary a")) > 0:
            for link in soup.select("div.re-Card-primary a"):
                if "new-home" not in link["href"]:
                    housesListUrls.append(link["href"])
        else:
            print(f"There is no links in this page {self.buildUrlForCityandPage(nPage)}")
            return None, None

        # Fetching the times a house has been in the webpage
        if len(soup.select("span.re-Card-timeago")) > 0:
            for time in soup.select("span.re-Card-timeago"):
                housesListTimes.append(time.get_text())
        else:
            raise Exception("There is no times in this page")

        if len(housesListTimes) > 0 and len(housesListTimes) > 0:
            seleniumDriver.quit()

            return housesListUrls, housesListTimes


    def getHouseInfo(self, houseUrl):
        """
        This functions scrapes all the information of the house specified in the url
        :param houseUrl:
        :return: A dictionary with the house's features
        """

        url = self.buildUrlForHouse(houseUrl)
        html = super().doRequestRequestsHtml(url)
        soup = super().getBeautifulSoup(html)
        # Dictionary to return, only strings at this point
        houseInfoDict = {
            "price":"",
            "zone":"",
            "nbedrooms":"",
            "nbathrooms":"",
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
            "hotwater":"",
            "tags":"",
            "description":""

        }

        # Getting all the features from the soup
        price = soup.find("span", class_="re-DetailHeader-price")
        if price is not None:
            houseInfoDict["price"] = price.get_text()
        else:
            raise Exception("Not able to find the price")
            return None

        zone = soup.find("span", class_="re-Breadcrumb-text")
        if zone is not None:
            houseInfoDict["zone"] = zone.get_text()

        if len(soup.select("li.re-DetailHeader-featuresItem span")) > 0:
            for span in soup.select("li.re-DetailHeader-featuresItem span"):
                if "bdrm" in span.get_text():
                    houseInfoDict["nbedrooms"] = span.get_text()
                elif "bathroom" in span.get_text():
                    houseInfoDict["nbathrooms"] = span.get_text()
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
                    houseInfoDict["hotwater"] = div.get_text()

        if len(soup.select("li.re-DetailExtras-listItem")) > 0:
            tagStringBuilder = ""
            for tag in soup.select("li.re-DetailExtras-listItem"):
                tagStringBuilder += f"{tag.get_text()},"
            houseInfoDict["tags"] = tagStringBuilder

        description = soup.find("p", class_="fc-DetailDescription")
        if description is not None:
            houseInfoDict["description"] = description.get_text()

        return houseInfoDict


    @staticmethod
    def stopFetchingTrigger(houseUrlsPrev, houseUrlsNext):
        """
        Fotocasa webapage is dynamic, and it has infinite pages with the same houses, in order to detect
        when we need to stop fetching pages, we need to compare the links from the last page and the new one
        and check if they are the same.
        :param houseUrlsPrev:
        :param houseUrlsNext:
        :return: True or False, meaning if we need to stop fetching pages.
        """

        if houseUrlsPrev != None:
            if houseUrlsPrev[0] != houseUrlsNext[0]:
                return True
            else:
                print("All the houses have been retrieved")
                return False
        else:
            return True









