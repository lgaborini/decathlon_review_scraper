# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy_djangoitem import DjangoItem

# To get your settings from (settings.py):
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


# Django integration

if settings.get("USE_DJANGO"):
    from browser.models import ProductDjangoItem, ProductReviewDjangoItem

# Notice that DjangoItems are scrapy.Items


class ProductItem(DjangoItem):
    if settings.get("USE_DJANGO"):
        django_model = ProductDjangoItem


class ProductReviewItem(DjangoItem):
    if settings.get("USE_DJANGO"):
        django_model = ProductReviewDjangoItem
