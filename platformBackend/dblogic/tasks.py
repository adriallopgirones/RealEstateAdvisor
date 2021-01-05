from celery.utils.log import get_task_logger
from celery import Celery, shared_task
from selenium import webdriver
from celery.schedules import crontab

logger = get_task_logger(__name__)

app = Celery()


@shared_task
def test():
    logger.info('hola')

def dbUpdate(scrapper, processor, model, city):
    logger.info("Updating the DB")

    # Retrieving the field "urls" for all objects of the specified model
    houseUrlsListDB = model.objects.all().values_list('url', flat=True)

    # Creating an instance of whatever scrapper this function receives
    sc = scrapper(city)
    houseUrlsList = []
    prevNextUrls = {"prev": ["a"], "next": ["b"]}
    nPage = 2

    houseUrls, onlineTimes = sc.getHousesListUrlsAndTimes()

    while sc.stopFetchingTrigger(prevNextUrls["prev"], prevNextUrls["next"]):

        # Wen we cannot retrieve the urls we assign the variable to None
        if houseUrls == None:
            continue

        # Concatenating lists
        houseUrlsList += houseUrls
        prevNextUrls["prev"] = houseUrls
        houseUrls, onlineTimes = sc.getHousesListUrlsAndTimes(nPage)
        prevNextUrls["next"] = houseUrls
        nPage += 1

    # Symmetric difference of the two lists to get the recent added urls
    newUrls = list(set(houseUrlsListDB) - set(houseUrlsList))

