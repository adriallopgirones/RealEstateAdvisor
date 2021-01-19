# RealEstateAdvisor

RealEstateAdvisor is an intelligent web-platform that helps its users to find good deals in the Real Estate sector. Currently the platform extracts 
the information from www.fotocasa.es for the city of Barcelona, Spain. 

It uses Machine Learning to predict what would be a reasonable price for a specific house, the platform feeds itself automatically with new data every 3 days
and uses it to re-train a model, so that becomes more and more accurate through time.

# How does it work?

The platform can easily be separated in two main parts: 

- The Front-end: which is basically a layout where a person can register and visualize the deals by filtering accordingly to their preferences.

- The Back-end: The back-end has two main functionalities, the first is acting as a web-server for the front-end, holding all the required logic and 
serving the necessary data. The second one, which is totally independent from the first one consists of retrieving the data from a specified 
webpage using webscrape, pre-process it, train a ML model, establish it as the main model if certain metrics are better than the predecessors' and predict
a price for each house on the DB.

To decouple both back-end functionalities the platform uses docker with celery so all the logic related to update the DB (Scraping new data, 
train a model, and predict the prices) is a periodic task that happens every three days and has nothing to do with the webpage.

The chosen model was XGBoost, since it fast and it has been proven to work well with similar regression problems.
(For more insights on the data and the model, you can take a look at the Python Notebook.)

The platform has been coded in a very modular way, to make it easy to include new Scrappers, data Processors, so it can be easily extended to new
webpages and cities.
