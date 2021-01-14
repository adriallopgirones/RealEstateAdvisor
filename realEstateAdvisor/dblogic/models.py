from django.db import models

class FotocasaHouse(models.Model):
    url = models.CharField(unique=True, max_length=2000) # Not used in the model
    sold = models.IntegerField(default=0)
    timeonline = models.IntegerField()
    price = models.IntegerField(blank=False)
    predictedprice = models.IntegerField(default=None, null=True)
    zone = models.IntegerField()
    nbedrooms = models.IntegerField(default=None)
    nbathrooms = models.IntegerField(default=None)
    size = models.IntegerField(default=None)
    floor = models.IntegerField(default=None)
    typology = models.IntegerField(default=None)
    status = models.IntegerField(default=None, null=True)
    antiquity = models.IntegerField(default=None)
    elevator = models.IntegerField(default=None)
    orientation = models.CharField(default=None, max_length=50, null=True) # Not used in the model
    parking = models.IntegerField(default=None)
    furnished = models.CharField(default=None, max_length=50, null=True) # Not used in the model
    heating = models.CharField(default=None, max_length=50, null=True) # Not used in the model
    hotwater = models.CharField(default=None, max_length=50, null=True) # Not used in the model
    tags = models.CharField(default=None, max_length=50, null=True) # Not used in the model
    description = models.CharField(default=None, max_length=2000, null=True) # Not used in the model
    airconditioning = models.IntegerField(default=None)
    terrace = models.IntegerField(default=None)
    kitchen = models.IntegerField(default=None)
    parquet = models.IntegerField(default=None)

class CurrentBestMLModel(models.Model):
    mae = models.FloatField(default=0)
    modelname = models.CharField(max_length=500, default="test")

