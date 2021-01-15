# Imports to execute the code inside the Django environment
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realEstateAdvisor.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from dblogic.models import FotocasaHouse
from dblogic.models import CurrentBestMLModel
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor
from datetime import date

class mlOperator():

    """
    This class receives instances of the desired model, retrieves the best known ML model for it
    and performs different Machine Learning-related operations
    """

    def __init__(self, model):

        self.model = model
        mlModelDBObject = CurrentBestMLModel.objects.get(djangoModelName=model.__name__)
        with (open(mlModelDBObject.modelPath, "rb")) as file:
            try:
                self.mlModel = pickle.load(file)
                self.mlModelMAE = mlModelDBObject.mae
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
        :returns: A pandas DataFrame
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


    def trainGetMAEandmlModel(self):
        """
        This method receives a django model, queries all its objects, us them to train a model
        and returns the Mean Absolute Error and the model itself
        """

        queryset = self.model.objects.all()
        df = self.querySetToPDdataframe(queryset)

        y_var = list(FotocasaHouse.objects.values_list('price', flat=True))
        X_var = df
        X_train, X_test, y_train, y_test = train_test_split(X_var, y_var, test_size=0.2, random_state=0)
        mlmodel = XGBRegressor(n_estimators=500)
        mlmodel.fit(X_train, y_train, verbose=False, early_stopping_rounds=5,
                  eval_set=[(X_test, y_test)])

        predictions = mlmodel.predict(X_test)

        mae = mean_absolute_error(predictions, y_test)

        return mae, mlmodel

    def updateBestMLModel(self):

        """
        This functions trains a Machine Learning model with all the objects of the Django Model specified
        in the class and if the Mean Absolute Error (MAE) is better than the previous,
        it updates the Django Model CurrentBestMLModel with the new one,
        and recalculates the attribute predicted price for the Django Model.
        """

        pathTomlModelsFolder = "/Users/adriallopgirones/PycharmProjects/RealEstateAdvisor/" \
                               "realEstateAdvisor/dblogic/mlModels/"
        candidateMae, candidateModel = self.trainGetMAEandmlModel()

        # If new MAE is 1000 euros better we swap the best ML model in the DB for the linked Django Model
        if candidateMae - self.mlModelMAE > 1000:
            print("Model Improved, let's update the model and the predictions")
            mlModelName = f"MLmodel_{self.model.__name__}_{date.today()}"
            with(open(f"{pathTomlModelsFolder}{mlModelName}.pkl", "wb")) as file:
                pickle.dump(candidateModel, file)

            CurrentBestMLModel.objects.filter(djangoModelName=self.model.__name__).update(mae=candidateMae,
                                                                    modelPath=f"{pathTomlModelsFolder}"+
                                                                              f"{mlModelName}.pkl",
                                                                    djangoModelName=self.model.__name__)

            # Change predictedPrice field for all objects to None
            # and calculate it again with the new (and better) ml model
            self.model.objects.all().update(predictedprice=None)
            self.predictedPricesFiller()

if __name__ == '__main__':
    obj = mlOperator(FotocasaHouse)
    obj.updateBestMLModel()

