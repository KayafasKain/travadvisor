# -*- coding: utf-8 -*-
import scrapy
from ..items import TravelScrapperStaticItem
import re

class TripadivsorStaticSpider(scrapy.Spider):
    name = 'tripadvisor_static'
    allowed_domains = ['www.tripadvisor.com', 'www.tripadvisor.com.au']
    start_urls = ['http://www.tripadvisor.com/']

    # XPATHs used to access top-level data
    page_count_xpath = '//div[@class="pageNumbers"]/a[@class="pageNum last taLnk "]'
    hotel_url_xpath = '//div[@class="listing_title"]/a[contains(@class, property_title)]'

    # XPATHs used to access static data
    asset_name_xpath = '//h1[@id="HEADING"]'
    asset_address_xpath = '//span[@class="detail"]/span'
    asset_class_xpath = '//span[contains(@class,"ui_bubble_rating")]'
    asset_website_xpath = '' # Website url is badly encoded, need extra time at least to decode
    asset_rooms_num_xpath = '//div[contains(@id, component_17)]//*[text()="NUMBER OF ROOMS"]/../'
    asset_also_known_xpath = '//div[contains(@id, component_17)]//*[text()="ALSO KNOWN AS"]/../'
    asset_location_xpath = '//div[contains(@id, component_17)]//*[text()="LOCATION"]/../'

    def __init__(self, city, city_url, currency='USD', max_pages_to_parse=1, *args, **kwargs):
        """
        Initiating necessery variables
        :param city:  name of city, where crawler will search for hotels (Not in use yet)
        :param city_url: link to catalogue-like page, which contains info about local hotels
        :param currency: "USD" - format of currency, "USD" set as default (Not in use yet)
        :param max_pages_to_parse: specifies amount of "catalogue" pages which weill be parsed
        """
        super(TripadivsorStaticSpider, self).__init__(*args, **kwargs)
        if not city or not city_url:
            raise ValueError('Please, provide city and city_url')
        self.city = city
        self.city_url = city_url
        self.start_urls = [city_url]
        self.max_pages_to_parse = max_pages_to_parse

    def parse(self, response):
        """
        Starting parse process. Calculating pages to parse etc.
        :param response: response object from accessing the catalogue page
        :return: yields request in order to parse each page in particular
        """
        page_count = self.parse_page_count(response)
        url_split_re = re.compile("-*([0-9]+)-")

        if self.max_pages_to_parse is not None and self.max_pages_to_parse <= page_count:
            page_count = int(self.max_pages_to_parse)

        for page in range(page_count):
            # augmenting catalogue-page url in order to iterate
            catalogue_url = url_split_re.split(response.request.url)
            catalogue_url.insert(2, '-oa{}-'.format(page * 30))
            catalogue_url = ''.join(catalogue_url)
            yield scrapy.Request(catalogue_url, method='GET', callback=self.parse_page)

    def parse_page(self, response):
        """
        Parsing particular catalogue page, taking asset URLs  in order to parse ach asset
        :param response: response object from accessing the catalogue page
        :return: yields request in order to parse asset (hotel) page
        """
        item_urls = self.create_item_urls(self.parse_item_urls(response))
        for url in item_urls:
            yield scrapy.Request(url, method='GET', callback=self.parse_asset)

    def parse_asset(self, response):
        """
        Parsing asset (hotel page)
        :param response: response object from accessing the asset (hotel) page
        :return: yields item - dictionary, which is consist parsed data
        """
        item = TravelScrapperStaticItem()
        item['asset_name'] = self.parse_asset_name(response)
        item['address'] = self.parse_asset_address(response)
        item['asset_class'] = self.parse_asset_class(response)
        item['website'] = None # hotel website`s URL, no way to retrieve for now
        item['rooms_num'] = self.parse_asset_rooms_num(response)
        item['also_known'] = self.parse_asset_aslo_known(response)
        item['location'] = self.parse_asset_location(response)
        item['asset_url'] = response.request.url
        item['agoda_url'] = None # hotel`s page on Agoda URL, no way to retrieve for now

        yield item

    def parse_asset_location(self, response):
        """
        Parsing location of asset (hotel)
        :param response: response object from accessing the asset (hotel) page
        :return: returns list of locations (from more to less) example: ['Country', 'State', 'Town', ...]
        """
        location_list = (response.selector.xpath(self.asset_location_xpath + '/text()').extract())
        return location_list[1:] # cutting off first element which is "LOCATION" label, change if made better XPATH

    def parse_asset_aslo_known(self, response):
        """
        Parsing another names of current asset (hotel)
        :param response: response object from accessing the asset (hotel) page
        :return: returns list of another names
        """
        try:
            also_known_list = (response.selector.xpath(self.asset_also_known_xpath + '/text()').extract())[1:]
        except:
            also_known_list = []
        return also_known_list

    def parse_asset_rooms_num(self, response):
        """
        Retrieving number of rooms, for each hotel
        :param response:
        :return: returns Int, which is represents number of rooms in a hotel
        """
        try:
            room_num_raw = response.selector.xpath(self.asset_rooms_num_xpath + '/text()').extract()
            room_num = int(room_num_raw[1]) # taking second element, change, if made better XPATH
        except:
            room_num = None
        return room_num

    def parse_asset_website(self, response):
        """
        Parsing asset (hotel) website`s URL (WIP, not functional yet)
        :param response: response object from accessing the asset (hotel) page
        :return: returns hotel website`s url
        """
        return response.selector.xpath(self.asset_website_xpath + '@href').extract_first()

    def parse_asset_class(self, response):
        """
        Parsing asset (hotel) class
        :param response: response object from accessing the asset (hotel) page
        :return: returns string which is contains hotel`s class, might be changed, after consultations with client
        """
        return response.selector.xpath(self.asset_class_xpath + '/@alt').extract_first()

    def parse_asset_address(self, response):
        """
        Parsing asset (hotel) address
        :param response: response object from accessing the asset (hotel) page
        :return: returns list which is consist of different address levels in ascending order ex: ['street', 'district']
        """
        return response.selector.xpath(self.asset_address_xpath + '/text()').extract()

    def parse_asset_name(self, response):
        """
        Parsing asset (hotel) name
        :param response: response object from accessing the asset (hotel) page
        :return: returns String, which is contain asset`s name
        """
        return response.selector.xpath(self.asset_name_xpath + '/text()').extract_first()

    def parse_page_count(self, response):
        """
        Parsing total amount of pages in catalogue
        :param response: response object from accessing the catalogue page
        :return: returns Int, amount of pages
        """
        return int(response.selector.xpath(self.page_count_xpath + '/text()').extract_first())

    def parse_item_urls(self, response):
        """
        Parsing assert`s (hotel) URLs
        :param response: response object from accessing the catalogue page
        :return: returns list of strings (assert`s URLs)
        """
        return response.selector.xpath(self.hotel_url_xpath + '/@href').extract()

    def create_item_urls(self, item_urls):
        """
        Modifying basic relative asset`s URLs
        :param item_urls: response object from accessing the catalogue page
        :return: returns list of fully functional asset URLs
        """
        return ['http://' + self.allowed_domains[0] + item for item in item_urls]
