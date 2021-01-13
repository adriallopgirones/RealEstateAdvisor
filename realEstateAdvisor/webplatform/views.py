from django.shortcuts import render
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realEstateAdvisor.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from dblogic.models import FotocasaHouse
from django.core.paginator import Paginator
from django.contrib import messages

from .forms import QueryForm

def queryGoodDeals(timeOnline, priceDifference, price):
    """ Queries the DB with the specified parameters """

    goodDeals = FotocasaHouse.objects.filter(Q(predictedprice__gt=F("price")+priceDifference),
                                             Q(price__lt=price),
                                             Q(sold=0),
                                             Q(timeonline__lt=timeOnline)).order_by("timeonline")

    return goodDeals

def queryToDict(query):
    """ Transforms the queryset into a dict with the proper format to be the context"""

    completeUrls = ["https://www.fotocasa.es" + q.url for q in query]
    priceDifferences = [q.predictedprice - q.price for q in query]
    dict_list = [{"query": i, "url": j, "pricedif": z} for i, j, z in zip(query, completeUrls, priceDifferences)]

    return dict_list

@login_required()
def home(request):

    # We need complete urls, price difference, and the object itself in the context
    query = queryGoodDeals(5, 80000, 1000000)
    dict_list = queryToDict(query)

    # Pagination set up
    paginator = Paginator(dict_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            messages.success(request, "The list has been updated")
            userInterests = form.cleaned_data
            query = queryGoodDeals(userInterests["timeOnline"],
                                   userInterests["priceDifference"],
                                   userInterests["price"])
            dict_list = queryToDict(query)
            paginator = Paginator(dict_list, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {"page_obj": page_obj,
                       "form": form}

            return render(request, "webplatform/home.html", context)
    else:
        form = QueryForm()

    context = {"page_obj": page_obj,
               "form":form}

    return render(request, "webplatform/home.html", context)


if __name__ == '__main__':
    queryGoodDeals()