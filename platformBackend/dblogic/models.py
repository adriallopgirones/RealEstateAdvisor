from django.db import models

class FotocasaHouse(models.Model):
    url = models.CharField(unique=True, max_length=2000)
    sold = models.IntegerField(default=0)
    timeonline = models.IntegerField()
    price = models.IntegerField()
    zone = models.CharField(default="", max_length=1000)
    nbedrooms = models.CharField(default="", max_length=50)
    nbathrooms = models.CharField(default="", max_length=50)
    size = models.CharField(default="", max_length=50)
    floor = models.IntegerField(default=-1)
    typology = models.CharField(default="", max_length=50)
    status = models.CharField(default="", max_length=50)
    antiquity = models.IntegerField(default=-1)
    elevator = models.IntegerField(default=-1)
    orientation = models.CharField(default="", max_length=50)
    parking = models.CharField(default="", max_length=50)
    furnished = models.CharField(default="", max_length=50)
    heating = models.CharField(default="", max_length=50)
    hotwater = models.CharField(default="", max_length=50)
    tags = models.CharField(default="", max_length=50)
    description = models.CharField(default="", max_length=2000)


