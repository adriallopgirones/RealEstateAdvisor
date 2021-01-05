# Imports to execute the code inside the Django environment
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platformBackend.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from dblogic.models import House
from scrappersLogic.FotocasaScrapper import FotocasaScrapper
from dataProcessement.FotocasaDataProcessor import FotocasaDataProcessor
import queue
from threading import Thread
import sys
import csv
from datetime import date

from dblogic.tasks import add

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


def dbFiller(scrapper, processor, city):
    """
    This function is in charge of calling the appropriate classes to scrape all the houses,
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
                dataDict = sc.getHouseInfo(urlTimeTuple[0])
                if dataDict != None:
                    pr = processor(dataDict, urlTimeTuple[0], urlTimeTuple[1])
                    # Storing the fetched house into the DB
                    dictToDB(pr._processAll(), nPage)
            except Exception as e:
                print(f"Error fetching the house with url: {urlTimeTuple[0]} error: {e}")

            q.task_done()
        sys.stdout.write(f"\r Page {nPage} complete")

    # Dictionary to keep track if we need to finish fetching, contains dummy values at first
    prevNextUrls = {"prev":["a"], "next":["b"]}
    nPage = 2
    num_fetch_threads = 30

    #Creating an instance of whatever scrapper this function receives
    sc = scrapper(city)
    houseUrls, onlineTimes = sc.getHousesListUrlsAndTimes()
    totalUrls = len(houseUrls)

    while sc.stopFetchingTrigger(prevNextUrls["prev"], prevNextUrls["next"]):

        # Wen we cannot retrieve the urls we assign the variable to None
        if houseUrls == None:
            print(f"Skipping page {nPage}")
            continue

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
        houseUrls, onlineTimes = sc.getHousesListUrlsAndTimes(nPage)
        prevNextUrls["next"] = houseUrls
        nPage += 1


def DBmodeltoCSV(model):
    """
    This functions takes a model and exports it as a csv file
    """

    fileName = f"{model.__name__}:{date.today()}.csv"

    with open(f"../csvFiles/{fileName}", "w") as csvFile:
        writer = csv.writer(csvFile)
        # Writing first row with column names
        row = ""
        for field in model._meta.fields:
            # Removing semicolons, since they'll be used as separators
            row += field.name
            row += ";"

        writer.writerow([row])

        # write your header first
        for obj in model.objects.all():
            row = ""
            # We iterate over every field of the objects
            for field in model._meta.fields:
                rowContent = str(getattr(obj, field.name)).replace(";","")
                row += rowContent
                row += ";"

            writer.writerow([row])


if __name__ == '__main__':
    # dbFiller(FotocasaScrapper, FotocasaDataProcessor, "barcelona")

    res = add.delay(2,3)
    print(res.id)