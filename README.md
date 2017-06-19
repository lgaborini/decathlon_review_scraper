# Decathlon review scraper

Easily scrape Decathlon reviews for a given product.

Items are optionally saved to a Django database.   
The Item schema is imported from the Django project [lgaborini/decathlon_review_browser](../../../../lgaborini/decathlon_review_browser).

# Usage:
> scrapy crawl decathlon

## Parameters:
To specify a parameter to a scraper, use the `-a param value` flag:
> -a url="http://example.com"
>   Scrape the given URL (must be a Decathlon base page for a product)
>   
> -a url_list=files.txt
>   Scrape a list of product URLs read from disk.

If `USE_DJANGO = True`, the output is sent to a Django database (specify the path in `settings.py`).   
Otherwise, output is controlled by the `-o` flag (see Scrapy docs).

## Tested under:
* Anaconda Python 4.2.13

## Requirements:
* Python 3.5.2
* Scrapy
* scrapy-djangoitem
* Selenium
* PhantomJS

#### For Django integration:
* Django

## TODO:

- [ ] Avoid scraping same reviews if scraper is rerun
- [ ] Fix page errors
- [x] Add product image display
- [x] Add product image thumbnails in review list
- [ ] Scrape and store images using the `ImagesPipeline`
- [ ] Report parsing errors in separate log
- [ ] Add product statistics
