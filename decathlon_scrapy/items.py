# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

# import scrapy

# Django
from scrapy_djangoitem import DjangoItem
from browser.models import ProductDjangoItem, ProductReviewDjangoItem


class ProductItem(DjangoItem):
    django_model = ProductDjangoItem


class ProductReviewItem(DjangoItem):
    django_model = ProductReviewDjangoItem
