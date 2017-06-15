# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class DecathlonScrapyPipeline(object):
    """Pipeline for non-Django objects."""

    def process_item(self, item, spider):
        return item


class ToDjangoPipeline(object):
    """Pipeline for Django objects."""
    # See ITEM_PIPELINES

    def process_item(self, item, spider):
        # Save the item to the Django database
        item.save()
        return item
