# Imports to execute the code inside the Django environment
# import os
# os.environ['DJANGO_SETTINGS_MODULE'] = 'platformBackend.platformBackend.settings'
# import django
# django.setup()

from dblogic.models import House
from scrappersLogic.FotocasaScrapper import FotocasaScrapper
from dataProcessement.FotocasaDataProcessor import FotocasaDataProcessor
import queue
from threading import Thread
import sys

def dictToDB(processedDict, nPage):
    """
    This functions receives the processed dictionary with the information of a house we construct in the Processor
    and stores the info in a DB table
    :param processedDict:
    :return:
    """

    try:
        # Using ** is the same as passing the arguments individually, we can do that because the dict arguments
        # and the model have the same names
        House.objects.create(**processedDict)
    except Exception as e:
        print(f"Problem occurred storing {processedDict} from page {nPage} into the db: {e}")

def stopFetchingTrigger(houseUrlsPrev, houseUrlsNext):
    """
    Fotocasa webapage is dynamic, and it has infinite pages with the same houses, in order to detect
    when we need to stop fetching pages, we need to compare the links from the last page and the new one
    and check if they are the same.
    :param houseUrlsPrev:
    :param houseUrlsNext:
    :return: True or False, meaning if we need to stop fetching pages.
    """

    if houseUrlsPrev[0] != houseUrlsNext[0]:
        return True
    else:
        print("xapant")
        return False


def dbFiller():
    """
    This function is in charge of calling the appropriate classes to scrape all the houses of FotoCasa webpage,
    process them and then storing them into the DB
    :return:
    """
    def fetchHouseInformationThread(q):
        """
        This function will be executed using multithreading, it fetches the information of a house and
        process the data, then adds the processed dictionary to a dict. It does this with every element
        of the queue that contains tuples of urls and timesOnline
        :param q:
        :return:
        """
        while not q.empty():

            sys.stdout.write(f"\r{dynamicprint} {totalUrls - enclosure_queue.qsize()}/{totalUrls}")

            urlTimeTuple = q.get_nowait()
            try:
                dataDict = fs.getHouseInfo(urlTimeTuple[0])
            except Exception as e:
                print(f"Error fetching the house with url: {urlTimeTuple[0]} error: {e}")
            fp = FotocasaDataProcessor(dataDict, urlTimeTuple[0], urlTimeTuple[1])
            # Storing the fetched house into the DB
            dictToDB(fp._processAll(), nPage)

            q.task_done()
        sys.stdout.write(f"\r Page {nPage} complete")

    # Dictionary to keep track if we need to finish fetching, contains dummy values at first
    prevNextUrls = {"prev":["a"], "next":["b"]}
    nPage = 2
    num_fetch_threads = 30
    fs = FotocasaScrapper("https://www.fotocasa.es/en/buy/homes", "barcelona")

    houseUrls, onlineTimes = fs.getHousesListUrlsAndTimes()
    totalUrls = len(houseUrls)

    while stopFetchingTrigger(prevNextUrls["prev"], prevNextUrls["next"]):
        dynamicprint = f"Scrapping Pages in page: {nPage - 1}"
        sys.stdout.write(f"\r{dynamicprint} 0/{totalUrls}")
        # Creating a queue structure with the urls of houses to scrape, so we can pass it to the threaded function
        enclosure_queue = queue.Queue()
        for houseUrl, onlineTime in zip(houseUrls, onlineTimes):
            enclosure_queue.put((houseUrl, onlineTime))

        # Set up some threads to fetch the data of a house
        for _ in range(num_fetch_threads):
            worker = Thread(target=fetchHouseInformationThread, args=(enclosure_queue,))
            worker.start()

        # Wait for the queue to be empty
        enclosure_queue.join()

        prevNextUrls["prev"] = houseUrls
        houseUrls, onlineTimes = fs.getHousesListUrlsAndTimes(nPage)
        prevNextUrls["next"] = houseUrls
        nPage += 1

if __name__ == '__main__':
    dbFiller()