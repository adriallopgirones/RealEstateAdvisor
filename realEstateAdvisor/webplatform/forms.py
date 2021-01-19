from django import forms

class QueryForm(forms.Form):
    timeOnline = forms.IntegerField(max_value=999,
                                    min_value= 1,
                                    label="Max number of days in the webpage")
    price = forms.IntegerField(max_value=2000000,
                               min_value= 100,
                               label="Max price")
    priceDifference = forms.IntegerField(max_value=2000000,
                                         min_value=100,
                                         label="Min difference of price between real and predicted")