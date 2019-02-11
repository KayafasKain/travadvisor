# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TravelScraperItem(scrapy.Item):
    static = scrapy.Field()
    review = scrapy.Field()
    price = scrapy.Field()


class TravelScrapperStatic(scrapy.Item):
    pass


class TravelScrapperReview(scrapy.Item):
    pass


class TravelScrapperPrice(scrapy.Item):
    pass

