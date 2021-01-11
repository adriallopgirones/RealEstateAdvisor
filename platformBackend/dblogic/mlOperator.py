import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platformBackend.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from dblogic.models import FotocasaHouse
import pandas as pd
import pickle


class mlOperator():

    """
    This class receives instances of the desired model and the name of the file containing a trained
    model and perform different Machine Learning-related operations
    """

    def __init__(self, model, mlModelName):
        self.model = model

        with (open(f"../mlModels/{mlModelName}", "rb")) as file:
            try:
                self.mlModel = pickle.load(file)
            except EOFError as e:
                raise(f"An error ocurred trying to open the ML model: {e}")

    def getPredictedPrices(self, housesQuerySet):
        """
        This function receives a querySet of houses and applies the trained Machine Learning model stored
        in the class as an attribute to get the predicted prices
        :returns: A list of the predicted prices
        """

        df = self.querySetToPDdataframe(housesQuerySet)

        return self.mlModel.predict(df)

    def predictedPricesFiller(self):
        """
        This functions queries all the objects of the model without a predicted price,
        calculates it using the ML model and stores it
        """

        queryset = self.model.objects.filter(predictedprice = None)
        predictions = self.getPredictedPrices(queryset)

        for obj, prediction in zip(queryset, predictions):
            obj.predictedprice = prediction
            obj.save()



    def querySetToPDdataframe(self, housesQuerySet):
        """
        This functions transforms a querySet to the proper format to run a model, a pandas DataFrame
        """
        dfDict = {}

        # Getting the features used to train the model, they should have the same name as the model fields
        features = self.mlModel.get_booster().feature_names

        for feature in features:
            dfDict[feature] = []

        for house in housesQuerySet:
            for feature in features:
                dfDict[feature].append(getattr(house,feature))

        return pd.DataFrame(dfDict)






if __name__ == '__main__':
    obj = mlOperator(FotocasaHouse, "fotocasa_xgb_reg.pkl")
    obj.predictedPricesFiller()