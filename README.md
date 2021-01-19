# RealEstateAdvisor

RealEstateAdvisor is an intelligent web-platform that helps its users to find good deals in the Real Estate sector. Currently the platform extracts 
the information from www.fotocasa.es for the city of Barcelona, Spain. 

It uses Machine Learning to predict what would be a reasonable price for a specific house, the platform feeds itself automatically with new data every 3 days
and uses it to re-train a model, so that becomes more and more accurate through time.

# How does it work?

The platform can easily be separated in two main parts: 

- The Front-end: Which is essentially a layout where a person can create a user and visualize the deals by filtering accordingly to their preferences.

- The Back-end: The back-end has two main functionalities, the first is acting as a web-server for the front-end, holding all the required logic and 
serving the necessary data when is requested. The second one, which is totally independent from the first one consists of retrieving the data from a specified 
webpage using webscraping techniques, pre-process the data, train a ML model and evaluate it. Then, it assigns a price to each house on the DB.

To decouple these two functionalities the platform uses docker with celery so all the logic related to updating the DB (Scraping new data, 
training a model, and predicting the prices) is a periodic task that happens every three days and has nothing to do with the webpage.

The chosen model was XGBoost, since it is fast and it has been proven to work well with similar regression problems.
(For more insights on the data and the model, you can take a look at the Python Notebook provided.)

The platform has been coded in a very modular way, including new Scrappers and data Processors is pretty straightforward, so the platform
can be easily extended to new webpages and cities.

# WebPlatform Screenshots

Web platform - Home

![](/realEstateAdvisor/Home2.png?raw=true "Optional Title")

Web platform - City Overview Section

![](/CityOverview.png?raw=true "Optional Title")

Web platform - Login

![](/login.png?raw=true "Optional Title")

# Technologies

- Django v=3.1.5: Web page backend
- celery v=5.0.5: Scheduled tasks
- django-celery-beat v=2.1.0: For scheduling tasks on the admin page
- selenium v=3.141.0: Web scraping (Scrolling required)
- requests v=2.24.0: Web scraping (Plain HTML retrieving)
- BeautifulSoup v=4.9.3: Text extraction from HTML file
- pandas v=1.1.5: Datasets management
- scikit-learn v=0.24.0: Machine Learning Tools
- xgboost v=1.3.1: Machine Learning model
- threading: Multithreading used during the webscrapping
- django-crispy-forms v=1.10.0: Nice displayment of forms on the HTML
