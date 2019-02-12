# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re

class TripadvisorSpider(CrawlSpider):
    name = 'tripadvisor'
    allowed_domains = ['www.tripadvisor.com.au', 'www.tripadvisor.com', ]
    start_urls = ['http://www.tripadvisor.com/']

    #XPATHs defined as:
    page_count_xpath = '//div[@class="pageNumbers"]/a[@class="pageNum last taLnk "]/text()'
    hotel_url_xpath = '//div[@class="listing_title"]/a[contains(@class, property_title)]/@href'
    hotel_price_xpath = ''

    #GraphQL link
    graph_ql_url = 'https://www.tripadvisor.com.au/data/graphql/batched'

    def __init__(self, city, city_url, currency='USD', *args, **kwargs):
        super(TripadvisorSpider, self).__init__(*args, **kwargs)
        if not city or not city_url:
            raise ValueError('Please, provide city and city_url')
        self.city = city
        self.city_url = city_url
        self.start_urls = [city_url]

    def parse(self, response):
        item_urls = self.create_item_urls(self.parse_item_urls(response))
        print('==========================================================')
        # print(response.headers)
        # print(response.headers.getlist('Set-Cookie'))
        # for url in item_urls:
        #     yield scrapy.Request(url, method='GET', callback=self.parse_item)
        secure_token = re.findall('var taSecureToken = "(.*?)"', response.body.decode())[0] # Alsio known as "roybatty"
        # yield scrapy.Request('https://www.tripadvisor.com/Hotel_Review-g293916-d12245879-Reviews-The_Salil_Hotel_Sukhumvit_57_Thonglor-Bangkok.html', method='GET', callback=self.parse_item, headers={
        #     'Host': 'www.tripadvisor.com',
        #     'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0',
        #     'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        #     'X-Requested-With': 'XMLHttpRequest'
        # },
        # cookies={
        #     'SetCurrency': 'GBP'
        # },
        # meta={
        #     'secure_token': secure_token
        # })

        yield scrapy.Request('https://www.tripadvisor.com/Hotel_Review-g293916-d12245879-Reviews-The_Salil_Hotel_Sukhumvit_57_Thonglor-Bangkok.html', method='GET', callback=self.parse_item,
                             headers={
                                 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0',
                                 'Keep-Alive': 'timeout=5, max=1000'
                             })

    def parse_item(self, response):
        print('==========================================================')
        # print(response.body)
        secure_token = re.findall('"csrfToken":\s*?"(.*?)"', response.body.decode())[0]  # Alsio known as "roybatty"
        print(secure_token)
        print(response.selector.xpath('//div[@class="bb_price_text "]/text()').extract())
        scr = scrapy.Request(self.graph_ql_url, method='POST', callback=self.parse_review,
                             headers={
                                 'Content-Type': 'application/json',
                                 'x-requested-by': secure_token
                             })
        print('---------------------------------------------------------------')
        print(scr.headers)
        yield scr

    def parse_review(self, response):
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(response.body.decode())

    def parse_static(self):
        pass

    def parse_page_count(self, response):
        return response.selector.xpath(self.page_count_xpath).extract_first()

    def parse_item_urls(self, response):
        return response.selector.xpath(self.hotel_url_xpath).extract()

    def create_item_urls(self, item_urls):
        return ['http://' + self.allowed_domains[0] + item for item in item_urls]
