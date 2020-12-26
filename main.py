# This import is just a work around for a bug in urlLib trying to install chromium for requests_html
import pyppdf.patch_pyppeteer
from requests_html import HTMLSession

from ScrappersLogic.FotocasaScrapper import FotocasaScrapper

if __name__ == '__main__':

    fs = FotocasaScrapper("https://www.fotocasa.es/en/buy/homes","barcelona")

    l = fs.getHousesListUrls()
    fs.getHouseInfo(l[3])