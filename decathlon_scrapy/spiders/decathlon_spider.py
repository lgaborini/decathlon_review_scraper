import scrapy
from selenium import webdriver

from decathlon_scrapy.items import ProductItem
from decathlon_scrapy.items import ProductReviewItem

import os
import hashlib

# Django integration
from django.utils import timezone
from decimal import Decimal

# Logging: Scrapy native, Selenium
import logging
from selenium.webdriver.remote.remote_connection import LOGGER as logger_Selenium

from scrapy.utils.project import get_project_settings
from urllib.parse import urlparse, urlunparse, urljoin
from scrapy.shell import inspect_response

# Get your settings from settings.py:
settings = get_project_settings()


# Configure Selenium logging
logger_Selenium.setLevel(logging.INFO)
# Configure Scrapy logging
# Raise loglevel for this spider
logging.getLogger('scrapy').setLevel(logging.INFO)


def null_to_blank(s):
    if s is None:
        return ""
    else:
        return s


class DecathlonSpider(scrapy.Spider):
    name = "decathlon"
    start_urls = []
    start_urls_default = [
        'https://www.decathlon.it/zaino-alpinism-22-blu-id_8360597.html'
    ]
    log_level = 'INFO'

    def __init__(self, url=None, url_list=None):
        self.driver = webdriver.PhantomJS()
        self.save_pages = False
        self.save_pages_dir = 'scraped_pages'

        if (self.save_pages):
            try:
                os.mkdir(self.save_pages_dir)
            except FileExistsError:
                pass

        if url_list:
            with open(url_list, 'r') as f:
                self.start_urls.extend([url.strip() for url in f.readlines()])
        elif url:
            self.start_urls.append(url)
        else:
            self.start_urls = self.start_urls_default

        self.logger.setLevel(self.log_level)
        self.logger.info("Parsing URLs: {0}".format(self.start_urls))

    def parse(self, response):
        """Parse the landing page"""
        self.logger.info('Getting landing page: %s', response.url)
        self.driver.get(response.url)

        # Get the base URL for the page
        url_components = urlparse(response.url)
        baseurl = urlunparse([
            url_components.scheme,
            url_components.netloc,
            '',
            '',
            '',
            ''])

        # Write landing page to disk
        if self.save_pages:
            filename = os.path.join(self.save_pages_dir, 'landing_page.html')

            with open(filename, 'w') as f:
                f.write(self.driver.page_source)
            self.log('Saved file %s' % filename)

        # Grab product variables
        #
        # using Selenium to execute JS code
        self.logger.info('Grabbing product variables')
        self.productId = self.driver.execute_script(
            'return window.oxyCodeProduit;')
        self.productName = response.xpath(
            '//span[@id="productName"]/text()').extract_first()
        self.num_pages = self.driver.execute_script(
            'return window.Osmose.variables.ProductAvis_nbPages;')
        self.productPrice = self.driver.execute_script(
            'return window.tc_vars.product_unitprice_ati;')

        self.logger.info('Product ID: {0}'.format(self.productId))
        self.logger.info('Product name: {0}'.format(self.productName))
        self.logger.info('Number of pages: {0}'.format(self.num_pages))

        # Deal with parsing error_message=''
        if self.num_pages is None:
            raise ValueError("Number of pages is not numeric.")

        # Run the Scrapy shell to capture additional data (debug)
        # inspect_response(response, self)

        productItemDict = {
            'productId': self.productId,
            'productName': self.productName,
            'last_fetched': str(timezone.now()),
            'productUrl': str(response.url),
            'productPrice': Decimal(self.productPrice),
            'productImageUrl': urljoin(baseurl, response.xpath(
                                        '//img[@id = "productMainPicture"]/@src').extract_first())
        }
        if settings.get("USE_DJANGO"):
            productItem = ProductItem(productItemDict)
            # This skips the pipeline, saves to Django DB
            # The saved instance is used as the ForeignKey for all reviews
            p = productItem.save()
        else:
            # We yield a Dict instead of an Item
            #
            # Notice that the obtained Item has no associated schema
            # itemType distinguishes products from reviews
            productItemDict['itemType'] = 'product'
            yield productItemDict

        # Grab all review pages
        for page in range(1, self.num_pages + 1):

            page_url = make_review_page_url(
                productId=self.productId, page=page)

            # Create the Request object for the page
            self.logger.debug('Creating request for url %s', page_url)
            request = scrapy.Request(url=page_url, callback=self.parse_review)
            request.meta['page'] = page

            if settings.get("USE_DJANGO"):
                # ForeignKey to saved Django item
                request.meta['ProductItem'] = p
            else:
                request.meta['ProductItem'] = productItemDict['productId']

            yield request
            # break

    def parse_review(self, response):
        """Extract reviews from a page"""
        page = response.meta['page']

        # ForeignKey (Django), or productId
        productItem = response.meta['ProductItem']

        self.logger.info('(Product {0}) parsing page {1}: {2}'.
            format(self.productId, page, response.url))

        if self.save_pages:
            with open(os.path.join(
                    self.save_pages_dir,
                    'review_page_{0}.html'.format(page)), 'wb') as f:
                f.write(response.body)

        # Got a list of reviews, yield items
        reviews = response.xpath('//div[@itemprop = "review"]')
        for i, review in enumerate(reviews):
            self.logger.info('(Product {0}) page {1}: parsing review {2}/{3}'.format(
                self.productId, page, i + 1, len(reviews)))

            productReviewDict = {
                'productId': productItem,
                'ratingValue': review.xpath(
                    './/meta[@itemprop = "ratingValue"]/@content').extract_first(),
                'datePublished': review.xpath(
                    './/div[@class = "post_by"]/meta[@itemprop = "datePublished"]/../p[@class="text_01"]/b/text()').extract_first(),
                'author': review.xpath(
                    './/div[@class = "post_by"]//span[@itemprop = "author"]/text()').extract_first(),
                'location': review.xpath(
                    './/div[@class = "post_by"]/p/b/span[@itemprop = "author"]/../../text()').extract_first(),
                'review': review.xpath(
                    'normalize-space(.//p[@itemprop = "description"]/span[@class = "comment"])').extract_first(),
                'usedSince': null_to_blank(review.xpath(
                    './/span[@class = "avis_model_used"]/b/text()').extract_first()),
                'reviewBonus': null_to_blank(review.xpath(
                    './/p[contains(@class, "avis_pos")]/text()').extract_first()),
                'reviewMalus': null_to_blank(review.xpath(
                    './/p[contains(@class, "avis_neg")]/text()').extract_first()),
                'fit': null_to_blank(review.xpath(
                    './/p[contains(@class, "avis-taille")]/text()').extract_first()),
                'reviewTitle': review.xpath(
                    './/p[contains(@class, "avis-title")]/text()').extract_first(),
                'reviewReply': "".join(review.xpath(
                    'normalize-space(.//p[@class = "avis_reponse_msg"])').extract_first())
            }

            # Make the primary key from review contents
            reviewHash = make_pkey_from_review_item(productReviewDict)
            productReviewDict['reviewHash'] = reviewHash
            # import ipdb; ipdb.set_trace()

            if settings.get("USE_DJANGO"):
                productReviewItem = ProductReviewItem(productReviewDict)
                # import ipdb; ipdb.set_trace()
                # This goes to the Django pipeline
                yield productReviewItem

                # TODO: ProductReviewItem is no longer JSON serializable
            else:
                # We yield a Dict instead of an Item
                #
                # Notice that the obtained Item has no associated schema
                # To distinguish from the productItem, we add this field
                productReviewDict['itemType'] = 'review'
                yield productReviewDict


def make_review_page_url(productId, page=1, reviews_per_page=5):
    """Make review pagination URL from page and productID"""
    return ("https://www.decathlon.it/it/ProductAvis_loadPaginationPage?"
            "product_id={0}&viewSize={1}&viewIndex={2}&"
            "currentEnvironment=PROD&componentId=ComponentProductAvis&"
            "sortReview=1&ratingFilter=0&pageIndex={3}&collaborator=0".format(
                productId,
                reviews_per_page,
                (page - 1) * reviews_per_page + 1,
                page)
            )


def make_pkey_from_review_item(productReviewDict):
    """Make the primary key for each review."""
    return hashlib.md5(productReviewDict['review'].encode('utf-8')).hexdigest()
