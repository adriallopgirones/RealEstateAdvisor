from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
class RealEstateScrapper():

    def __init__(self):
        pass

    def doRequestRequestsHtml(self, webPageToScrape):
        """
        This method does the requests to the specified webpage using requests_html
        :param webPageToScrape:
        :return: String containing the HTML content of the webpage
        """

        try:
            # session = HTMLSession()
            # r = session.get(webPageToScrape)
            # r.html.render()
            # session.close()
            r = requests.get(webPageToScrape)
            return r.content
        except ConnectionError as e:
            print(f"Scrapper error: ConnectionError: {e}")


    def doRequestsSelenium(self):
        """
        This method constructs a driver and returns it
        :param webPageToScrape:
        :return: The driver
        """

        WINDOW_SIZE = "1280,800"
        chrome_options = Options()
        chrome_options.add_argument(f"--window-size={WINDOW_SIZE}")
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        return driver


    def getBeautifulSoup(self, htmlContent):

        return BeautifulSoup(htmlContent, "lxml")

