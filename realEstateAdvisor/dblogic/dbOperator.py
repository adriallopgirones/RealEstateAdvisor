# Imports to execute the code inside the Django environment
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realEstateAdvisor.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.db.models import F

import queue
from threading import Thread
import sys
from datetime import date
import pandas as pd

from dblogic.dataProcessement.FotocasaDataProcessor import FotocasaDataProcessor
from dblogic.scrappersLogic.FotocasaScrapper import FotocasaScrapper
from dblogic.models import FotocasaHouse
from dblogic.mlOperator import mlOperator

class dbOperator():

    """
    This class receives instances of the desired model, scrapper and processor and perform different
    db-related operations
    """
    def __init__(self, model, scrapper, processor):
        self.model = model
        self.scrapper = scrapper
        self.processor = processor
        self.mlOperator = mlOperator(self.model)

    def dictToDB(self, processedDict):
        """
        This functions receives the processed dictionary with the information of a house we construct in the Processor
        and stores the info in a DB table
        :param processedDict:
        :return:
        """

        try:
            # Using ** is the same as passing the arguments individually, we can do that because the dict arguments
            # and the model have the same names
            self.model.objects.create(**processedDict)
        except Exception as e:
            print(f"Problem occurred storing {processedDict} into the db: {e}")


    def getHousesUrls(self, city="barcelona", firstPage=2, lastPage=4):
        """
        This function returns a list of URL's of the houses between the specified firstPage and lastPage
        for the passed city using the passed scrapper, default values will get all the urls.
        """

        # Dictionary to keep track if we need to finish fetching, contains dummy values at first
        prevNextUrls = {"prev": ["a"], "next": ["b"]}
        nPage = firstPage
        sc = self.scrapper(city)
        houseUrlsList = []
        onlineTimesList = []

        houseUrls, onlineTimes = sc.getHousesListUrlsAndTimes()

        while sc.stopFetchingTrigger(prevNextUrls["prev"], prevNextUrls["next"]) and nPage < lastPage:

            sys.stdout.write(f"\rScrapping houseUrls and onlineTimes in page: {nPage}/{lastPage}")

            prevNextUrls["prev"] = houseUrls
            houseUrls, onlineTimes = sc.getHousesListUrlsAndTimes(nPage)

            # When we cannot retrieve the urls we assign the variable to None
            if houseUrls == None:
                print(f"Skipping page {nPage}")
                prevNextUrls = {"prev": ["a"], "next": ["b"]}
                nPage += 1
                continue

            prevNextUrls["next"] = houseUrls

            houseUrlsList += houseUrls
            onlineTimesList += onlineTimes
            nPage += 1

        return houseUrlsList, onlineTimesList

    def dbFiller(self, city, houseUrlsList, onlineTimesList):
        """
        This function is in charge of calling the appropriate classes to scrape the houses indicated
        in the url list that receives, process them and then storing them into the DB
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

                sys.stdout.write(f"\r{dynamicprint} {totalHouses - enclosure_queue.qsize()}/{totalHouses}")

                urlTimeTuple = q.get_nowait()
                dataDict = sc.getHouseInfo(urlTimeTuple[0])
                if dataDict != None:
                    pr = self.processor(dataDict, urlTimeTuple[0], urlTimeTuple[1])
                    # Storing the fetched house into the DB
                    self.dictToDB(pr._processAll())

                q.task_done()

        num_fetch_threads = 30
        totalHouses = len(houseUrlsList)
        dynamicprint = f"Scrapping houses, house:"
        sys.stdout.write(f"\r{dynamicprint} 0/{totalHouses}")

        # Creating an instance of whatever scrapper this function receives
        sc = self.scrapper(city)

        # Creating a queue structure with the urls of houses to scrape, so we can pass it to the threaded function
        enclosure_queue = queue.Queue()
        for houseUrl, onlineTime in zip(houseUrlsList, onlineTimesList):
            enclosure_queue.put((houseUrl, onlineTime))

        # Set up some threads to fetch the data of a house
        for _ in range(num_fetch_threads):
            worker = Thread(target=fetchHouseInformationThread, args=(enclosure_queue,))
            worker.start()

        # Wait for the queue to be empty
        enclosure_queue.join()


    def dbUpdate(self, city):
        # Retrieving the field "urls" for all objects of the specified model
        houseUrlsListDB = self.model.objects.all().values_list('url', flat=True)

        houseUrlsList, onlineTimesList = self.getHousesUrls("barcelona")

        # Symmetric difference of the two lists to get the recent added urls indices
        newUrlsIndices = [i for i, value in enumerate(houseUrlsList) if value not in houseUrlsListDB]
        # Symmetric difference of the two lists to get the sold houses urls indices
        soldUrlsIndices = [i for i, value in enumerate(houseUrlsListDB) if value not in houseUrlsList]
        print("newUrlsIndices")
        print(newUrlsIndices)
        print("soldUrlsIndices")
        print(soldUrlsIndices)

        # Adding the new houses to the DB
        self.dbFiller(city, [houseUrlsList[i] for i in newUrlsIndices],
                      [onlineTimesList[i] for i in newUrlsIndices])

        # Setting sold houses to "yes" in the DB
        # Since sqlite does not accept a list larger than 999 for the query, we need to
        # make chunks of it, we use a generator
        def chunks(lst, n):
            # Yield successive n-sized chunks from lst
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        for chunk in chunks(soldUrlsIndices, 998):
            soldHouses = self.model.objects.filter(url__in=[houseUrlsListDB[i] for i in chunk])
            soldHouses.update(sold=1)

        # Updating the timeOnline for all not sold houses (+7), because the db is updated every 7 days
        notSoldHouses = self.model.objects.filter(sold=0)
        notSoldHouses.update(timeonline=F('timeonline') + 5)

        print('updated')
        # Predicting the price for the new houses
        # We check if we can improve the ML Model with the new houses, if so, we change the best MLModel
        # And update the predictedPrice
        self.mlOperator.predictedPricesFiller()
        self.mlOperator.updateBestMLModel()

        print('predicted price calculated')

    def DBmodeltoCSV(self):
        """
        This functions takes a model and exports it as a csv file
        """
        df = {}
        fileName = f"{self.model.__name__}_{date.today()}.csv"

        for i, field in enumerate(self.model._meta.fields):
            df[field.name]=[]

        for obj in self.model.objects.all():
            # We iterate over every field of the objects
            for i, field in enumerate(self.model._meta.fields):
                df[field.name].append(str(getattr(obj, field.name)))

        pd.DataFrame(df).to_csv(f"../csvFiles/{fileName}")

if __name__ == '__main__':
    pass