# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class TripadvisorSpider(CrawlSpider):
    name = 'tripadvisor'
    allowed_domains = ['www.tripadvisor.com.au']
    start_urls = ['http://www.tripadvisor.com.au/']

    #XPATHs defined as:
    page_count_xpath = '//div[@class="pageNumbers"]/a[@class="pageNum last taLnk "]/text()'
    item_url_xpath = '//div[@class="listing_title"]/a[contains(@class, property_title)]/@href'


    def __init__(self, city, city_url, currency='USD', *args, **kwargs):
        super(TripadvisorSpider, self).__init__(*args, **kwargs)
        if not city or not city_url:
            raise ValueError('Please, provide city and city_url')
        self.city = city
        self.city_url = city_url
        self.start_urls = [city_url]

    def parse(self, response):
        item_urls = self.create_item_urls(self.parse_item_urls(response))
        print(item_urls)
        for url in item_urls:
            yield scrapy.Request(url, callback=self.parse_item)

    def parse_item(self, response):

        print('item=============================')
        print()


    def parse_page_count(self, response):
        return response.selector.xpath(self.page_count_xpath).extract_first()

    def parse_item_urls(self, response):
        return response.selector.xpath(self.item_url_xpath).extract()

    def parse_item_price(self):
        pass

    def create_item_urls(self, item_urls):
        return ['http://' + self.allowed_domains[0] + item for item in item_urls]
