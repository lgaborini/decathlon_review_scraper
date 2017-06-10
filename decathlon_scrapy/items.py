# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

# import scrapy

# Django
from scrapy_djangoitem import DjangoItem
from browser.models import Product, ProductReview


class ProductItem(DjangoItem):
    # define the fields for your item here like:
    # name = scrapy.Field()
    django_model = Product


class ProductReviewItem(DjangoItem):
    django_model = ProductReview
