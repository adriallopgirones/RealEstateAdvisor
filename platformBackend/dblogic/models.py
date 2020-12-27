from django.db import models

class House(models.Model):
    url = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')



"price":"",
            "zone":"",
            "nBedrooms":"",
            "nBathrooms":"",
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
            "hotWater":"",
            "tags":"",
            "description":""