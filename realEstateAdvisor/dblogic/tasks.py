from celery.utils.log import get_task_logger
from celery import Celery, shared_task

from dblogic.dbOperator import dbOperator
from dblogic.models import FotocasaHouse
from dblogic.scrappersLogic.FotocasaScrapper import FotocasaScrapper
from dblogic.dataProcessement.FotocasaDataProcessor import FotocasaDataProcessor
logger = get_task_logger(__name__)

app = Celery()


@shared_task
def dbUpdateTask():
    """
    This function will be executed periodically using Celery and Redis. The schedules can be changed
    from the admin panel.
    """

    do = dbOperator(FotocasaHouse, FotocasaScrapper, FotocasaDataProcessor)
    do.dbUpdate("barcelona")




