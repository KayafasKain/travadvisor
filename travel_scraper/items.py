# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TravelScraperhotelItem(scrapy.Item):
    static = scrapy.Field()
    review = scrapy.Field()
    price = scrapy.Field()


class TravelScrapperStaticItem(scrapy.Item):
    asset_name = scrapy.Field()
    address = scrapy.Field()
    asset_class = scrapy.Field()
    website = scrapy.Field()
    rooms_num = scrapy.Field()
    also_known = scrapy.Field()
    location = scrapy.Field()
    asset_url = scrapy.Field()
    agoda_url = scrapy.Field()

class TravelScrapperReviewItem(scrapy.Item):
    pass


class TravelScrapperPriceItem(scrapy.Item):
    hotel_url = scrapy.Field()
    best_price = scrapy.Field()
    provider = scrapy.Field()
    provider_url = scrapy.Field()
