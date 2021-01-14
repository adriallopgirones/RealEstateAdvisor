from django.shortcuts import render
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realEstateAdvisor.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.contrib.auth.decorators import login_required
from django.db.models import F, Q, Avg
from dblogic.models import FotocasaHouse
from django.core.paginator import Paginator
from django.contrib import messages
from dblogic.dataProcessement.processingConstants import fotoCasaConstants
from .forms import QueryForm

def queryGoodDeals(timeOnline, priceDifference, price):
    """ Queries the DB with the specified parameters """

    goodDeals = FotocasaHouse.objects.filter(Q(predictedprice__gt=F("price")+priceDifference),
                                             Q(price__lt=price),
                                             Q(sold=0),
                                             Q(timeonline__lt=timeOnline)).order_by("timeonline")

    return goodDeals

def queryToDict(query):
    """ Transforms the queryset into a list of dicts with the proper format to be the context"""

    completeUrls = ["https://www.fotocasa.es" + q.url for q in query]
    priceDifferences = [q.predictedprice - q.price for q in query]
    ids = [q.id for q in query]
    prices = [q.price for q in query]
    predictedPrices = [q.predictedprice for q in query]
    timeOnlines = [q.timeonline for q in query]
    dict_list = [{"url": i, "pricedif": j, "id": z, "price":x, "predprice":w, "timeonline":m}
                 for i, j, z, x, w, m in zip(completeUrls,
                                              priceDifferences,
                                              ids,
                                              prices,
                                              predictedPrices,
                                              timeOnlines,)]

    return dict_list

@login_required()
def home(request):

    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            messages.success(request, "The list has been updated")
            userInterests = form.cleaned_data
            query = queryGoodDeals(userInterests["timeOnline"],
                                   userInterests["priceDifference"],
                                   userInterests["price"])
            dict_list = queryToDict(query)

            # Storing user preferences in a Session object
            request.session["dict_list"] = dict_list
            paginator = Paginator(request.session["dict_list"], 3)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {"page_obj": page_obj,
                       "form": form}

            return render(request, "webplatform/home.html", context)
    else:
        if "dict_list" not in request.session:
            print('HEY')
            # We need complete urls, price difference, and the object itself in the context
            query = queryGoodDeals(5, 80000, 1000000)
            dict_list = queryToDict(query)
            form = QueryForm()

            # Pagination set up
            paginator = Paginator(dict_list, 3)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {"page_obj": page_obj,
                       "form": form}
        else:
            # User POST their preferences, we need to use them to show the requested data
            form = QueryForm()
            paginator = Paginator(request.session["dict_list"], 3)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {"page_obj": page_obj,
                       "form": form}

        return render(request, "webplatform/home.html", context)

@login_required()
def cityOverviewView(request):

    allHouses = FotocasaHouse.objects.all()

    prices = [house.price for house in allHouses]
    sizes = [house.size for house in allHouses]
    totalSize = sum(sizes)
    totalPrice = sum(prices)
    totalHouses = len(prices)
    averageHousePrices = totalPrice/totalHouses
    averageHouseSizes = totalSize/totalHouses

    zones = []
    zoneAverages = []
    for k, v in fotoCasaConstants['zonesDict'].items():
        zones.append(k)
        zoneAverages.append(FotocasaHouse.objects.filter(zone=v).values("price").aggregate(Avg(F("price")))['price__avg'])

    zoneAverages, zones = zip(*sorted(zip(zoneAverages, zones)))

    zoneAverages = list(zoneAverages)
    zones = list(zones)

    print(zoneAverages)
    print(zones)
    return render(request, "webplatform/cityOverview.html", {
        "zones": zones[-10:],
        "zoneAverages":zoneAverages[-10:],
        "averageHousePrices":averageHousePrices,
        "averageHouseSizes":averageHouseSizes,
        "averagePriceM": averageHousePrices/averageHouseSizes
    })


if __name__ == '__main__':
    queryGoodDeals()