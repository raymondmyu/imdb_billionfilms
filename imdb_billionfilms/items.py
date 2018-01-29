# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ImdbBillionfilmsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class MovieImages(scrapy.Item):
    type = scrapy.Field()
    ranking = scrapy.Field()
    title = scrapy.Field()
    year = scrapy.Field()
    gross = scrapy.Field()
    opening = scrapy.Field()
    actors = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_name = scrapy.Field()

class ActorImages(scrapy.Item):
    type = scrapy.Field()
    actor = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_name = scrapy.Field()