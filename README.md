# Decathlon review scraper

Easily scrape Decathlon reviews for a given product.

Items are optionally saved to a Django database.   
The Item schema is imported from the Django project [lgaborini/decathlon_review_browser](../../../../lgaborini/decathlon_review_browser).

## Tested under:
* Anaconda Python 4.2.13

## Requirements:
* Python 3.5.2
* Scrapy
* scrapy-djangoitem
* Selenium
* PhantomJS
### For Django integration:
* Django
