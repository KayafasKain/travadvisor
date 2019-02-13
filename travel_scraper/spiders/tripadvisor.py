# -*- coding: utf-8 -*-
import scrapy
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
        #print(response.body)
        #secure_token = re.findall('var taSecureToken = "(.*?)"', response.body)[0] # Alsio known as "roybatty"
        # yield scrapy.Request('https://www.tripadvisor.com/hotel_Review-g293916-d12245879-Reviews-The_Salil_hotel_Sukhumvit_57_Thonglor-Bangkok.html', method='GET', callback=self.parse_item, headers={
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

        rqst = scrapy.Request('https://www.tripadvisor.com.au/hotel_Review-g293916-d12937851-Reviews-or10-Holiday_Inn_Express_Bangkok_Soi_Soonvijai-Bangkok.html', method='GET', callback=self.parse_item,
                             headers={
                                'Host': 'www.tripadvisor.com.au',
                                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                                'Connection': 'keep-alive',
                                'Upgrade-Insecure-Requests': '1',
                                'Pragma': 'no-cache',
                                'Cache-Control': 'no-cache',
                                'TE': 'Trailers',
                                'Cookie': response.headers.getlist('Set-Cookie')
                             })
        print(rqst.headers)
        yield rqst

    def parse_item(self, response):
        print('==========================================================')
        # print(response.body)
        secure_token = re.findall('"JS_SECURITY_TOKEN":\s*?"(.*?)"', response.body.decode())[0]  # Alsio known as "roybatty"
        print(secure_token)
        print(response.selector.xpath('//div[@class="bb_price_text "]/text()').extract())
        scr = scrapy.Request(self.graph_ql_url, method='POST', callback=self.parse_review,
                             headers={
                                 'Host': 'www.tripadvisor.com.au',
                                 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0',
                                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                                 'Connection': 'keep-alive',
                                 'Upgrade-Insecure-Requests': '1',
                                 'Pragma': 'no-cache',
                                 'Cache-Control': 'no-cache',
                                 'TE': 'Trailers',
                                 'Content-Type': 'application/json',
                                 'Origin': 'https://www.tripadvisor.com.au',
                                 'x-requested-by': secure_token
                             },
                             body='[{"operationName":"ReviewListQuery","variables":{"locationId":12937851,"offset":10,"filters":[{"axis":"LANGUAGE","selections":["en"]}],"prefs":null,"initialPrefs":{},"limit":5,"filterCacheKey":"hotelReviewFilters_12937851","prefsCacheKey":"hotelReviewPrefs","needKeywords":false,"keywordVariant":"location_keywords_v2_llr_order_30_en"},"query":"query ReviewListQuery($locationId: Int!, $offset: Int, $limit: Int, $filters: [FilterConditionInput!], $prefs: ReviewListPrefsInput, $initialPrefs: ReviewListPrefsInput, $filterCacheKey: String, $prefsCacheKey: String, $keywordVariant: String!, $needKeywords: Boolean = true, $ownerPreferredReviewId: Int) {\n  cachedFilters: personalCache(key: $filterCacheKey)\n  cachedPrefs: personalCache(key: $prefsCacheKey)\n  locations(locationIds: [$locationId]) {\n    locationId\n    parentGeoId\n    name\n    reviewSummary {\n      rating\n      count\n      __typename\n    }\n    keywords(variant: $keywordVariant) @include(if: $needKeywords) {\n      keywords {\n        keyword\n        __typename\n      }\n      __typename\n    }\n    ... on LocationInformation {\n      parentGeoId\n      __typename\n    }\n    ... on LocationInformation {\n      parentGeoId\n      __typename\n    }\n    ... on LocationInformation {\n      name\n      __typename\n    }\n    ... on LocationInformation {\n      locationId\n      parentGeoId\n      accommodationCategory\n      currentUserOwnerStatus {\n        isValid\n        __typename\n      }\n      __typename\n    }\n    reviewList(page: {offset: $offset, limit: $limit}, filters: $filters, prefs: $prefs, initialPrefs: $initialPrefs, filterCacheKey: $filterCacheKey, prefsCacheKey: $prefsCacheKey, ownerPreferredReviewId: $ownerPreferredReviewId) {\n      totalCount\n      ratingCounts\n      languageCounts\n      preferredReviewIds\n      reviews {\n        ... on Review {\n          id\n          url\n          location {\n            locationId\n            name\n            __typename\n          }\n          createdDate\n          publishedDate\n          userProfile {\n            id\n            userId: id\n            isMe\n            isVerified\n            displayName\n            username\n            avatar {\n              id\n              photoSizes {\n                url\n                width\n                height\n                __typename\n              }\n              __typename\n            }\n            route {\n              url\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        ... on Review {\n          rating\n          publishedDate\n          publishPlatform\n          __typename\n        }\n        ... on Review {\n          title\n          language\n          url\n          __typename\n        }\n        ... on Review {\n          language\n          translationType\n          __typename\n        }\n        ... on Review {\n          roomTip\n          __typename\n        }\n        ... on Review {\n          tripInfo {\n            stayDate\n            __typename\n          }\n          location {\n            placeType\n            __typename\n          }\n          __typename\n        }\n        ... on Review {\n          additionalRatings {\n            rating\n            ratingLabel\n            __typename\n          }\n          __typename\n        }\n        ... on Review {\n          tripInfo {\n            tripType\n            __typename\n          }\n          __typename\n        }\n        ... on Review {\n          language\n          translationType\n          mgmtResponse {\n            id\n            language\n            translationType\n            __typename\n          }\n          __typename\n        }\n        ... on Review {\n          text\n          publishedDate\n          username\n          connectionToSubject\n          language\n          mgmtResponse {\n            id\n            text\n            language\n            publishedDate\n            username\n            connectionToSubject\n            __typename\n          }\n          __typename\n        }\n        ... on Review {\n          id\n          locationId\n          title\n          text\n          rating\n          absoluteUrl\n          mcid\n          translationType\n          mtProviderId\n          photos {\n            id\n            photoSizes {\n              url\n              width\n              height\n              __typename\n            }\n            __typename\n          }\n          userProfile {\n            id\n            displayName\n            username\n            __typename\n          }\n          __typename\n        }\n        ... on Review {\n          mgmtResponse {\n            id\n            __typename\n          }\n          provider {\n            isLocalProvider\n            __typename\n          }\n          __typename\n        }\n        ... on Review {\n          translationType\n          location {\n            locationId\n            parentGeoId\n            __typename\n          }\n          provider {\n            isLocalProvider\n            isToolsProvider\n            __typename\n          }\n          original {\n            id\n            url\n            locationId\n            userId\n            language\n            submissionDomain\n            __typename\n          }\n          __typename\n        }\n        ... on Review {\n          locationId\n          mcid\n          attribution\n          __typename\n        }\n        ... on Review {\n          locationId\n          helpfulVotes\n          photoIds\n          route {\n            url\n            __typename\n          }\n          socialStatistics {\n            followCount\n            isFollowing\n            isLiked\n            isReposted\n            isSaved\n            likeCount\n            repostCount\n            tripCount\n            __typename\n          }\n          status\n          userId\n          userProfile {\n            id\n            displayName\n            __typename\n          }\n          location {\n            additionalNames {\n              normal\n              long\n              longOnlyParent\n              longParentAbbreviated\n              longOnlyParentAbbreviated\n              longParentStateAbbreviated\n              longOnlyParentStateAbbreviated\n              geo\n              abbreviated\n              abbreviatedRaw\n              abbreviatedStateTerritory\n              abbreviatedStateTerritoryRaw\n              __typename\n            }\n            parent {\n              additionalNames {\n                normal\n                long\n                longOnlyParent\n                longParentAbbreviated\n                longOnlyParentAbbreviated\n                longParentStateAbbreviated\n                longOnlyParentStateAbbreviated\n                geo\n                abbreviated\n                abbreviatedRaw\n                abbreviatedStateTerritory\n                abbreviatedStateTerritoryRaw\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        ... on Review {\n          text\n          language\n          __typename\n        }\n        ... on Review {\n          locationId\n          absoluteUrl\n          mcid\n          translationType\n          mtProviderId\n          originalLanguage\n          rating\n          __typename\n        }\n        ... on Review {\n          id\n          locationId\n          title\n          rating\n          absoluteUrl\n          mcid\n          translationType\n          mtProviderId\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}]')
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
