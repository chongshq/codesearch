import scrapy
import re
from scrapySOF.settings import *
from scrapy.http import Request,FormRequest
from scrapySOF.items import ScrapysofItem
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

class SOFSpider(CrawlSpider):
    _i = 1
    isCalculated = False
    name = "SOF"
    allowed_domains = ["stackoverflow.com"]
    start_urls = [
        "http://stackoverflow.com/search?page=1&tab=Relevance&q=jersey"
    ]
    rules = [
		Rule(SgmlLinkExtractor(allow=(r'/search\?page=.*'), restrict_xpaths=('//*[@id="mainbar"]//div[@class="pager fl"]/a/@href')),callback='parse_next_url'),
        Rule(SgmlLinkExtractor(allow=(r'/questions/.*'), restrict_xpaths=('//div[@class="question-summary search-result"]'), deny=(r'/questions/tagged/.*')), callback='parse_page', follow=True)
	]
    link_extractor = {
        'next_page':  SgmlLinkExtractor(allow=(r'/search\?page=.*')),
        'pro_link': SgmlLinkExtractor(allow=(r'/questions/.*'), restrict_xpaths=('//div[@class="question-summary search-result"]'), deny=(r'/questions/tagged/.*')),
    }
     

    # def __init__(self):
    #     self.headers = HEADERS

    # def start_requests(self):
    #     for i, url in enumerate(self.start_urls):
    #         yield FormRequest(url, meta = {'cookiejar': i}, \
    #                           headers = self.headers, \
    #                           callback = self.parse, \
    #                           dont_filter = True)

    # def parse(self, response):
        
    #     questionList = response.xpath('//div[@class="question-summary search-result"]')
    #     # for sel in questionList:
    #     #     stars = sel.xpath('.//div[@class="status answered-accepted"]/strong/text()').extract_first()
    #     #     if(stars):
    #     #         url = sel.xpath('.//div[@class="result-link"]/span/a/@href').extract_first()
    #     #         next_full_url = "http://stackoverflow.com"+url
    #     #         yield scrapy.Request(next_full_url, callback=self.parse_page)
    #     #         print stars, url
        
    #     nextlink = response.xpath('//*[@id="mainbar"]//div[@class="pager fl"]/a/@href').extract();
    #     print "next page is "+nextlink[-1]
        # yield scrapy.Request("http://stackoverflow.com"+nextlink[-1], callback=self.parse)
    
    # def parse(self, response):
    #     s = response.xpath('//*[@id="mainbar"]//div[@class="subheader results-header"]/h2/text()').extract_first()
    #     p = response.xpath('//*[@id="mainbar"]//div[@class="page-sizer fr"]//a[@class="page-numbers current"]/text()').extract_first()
    #     patternCode = re.compile(r',| ', re.S)
    #     sum_result = re.sub(patternCode, '', s)
    #     page = int(sum_result)/int(p) -1
    #     self._page = page
        
    #     next_url = "http://stackoverflow.com/search?page=" + str(self._i) + "&tab=Relevance&q=jersey"
            
    #     yield FormRequest(next_url, \
    #                           headers = self.headers, \
    #                           callback = self.parse_next_url,\
    #                           dont_filter = True)
        # for link in self.link_extractor['next_page'].extract_links(response):
        #     print "---------"+link.url
        #     yield Request(url = link.url, callback=self.parse_next_url)
        # for link in self.link_extractor['pro_link'].extract_links(response):
        #     yield Request(url = link.url, callback=self.parse_page)

    def parse_next_url(self, response):     # analyise current n page and the question list inside it
        # questionList = response.xpath('//div[@class="question-summary search-result"]')
        # for sel in questionList:
        #     stars = sel.xpath('.//div[@class="status answered-accepted"]/strong/text()').extract_first()
        #     if(stars):
        #         url = sel.xpath('.//div[@class="result-link"]/span/a/@href').extract_first()
        #         next_full_url = "http://stackoverflow.com"+url
        #         yield Request(next_full_url,\
        #                       callback = self.parse_page, \
        #                       dont_filter = True)
        
        if(self.isCalculated == False):
            s = response.xpath('//*[@id="mainbar"]//div[@class="subheader results-header"]/h2/text()').extract_first()
            p = response.xpath('//*[@id="mainbar"]//div[@class="page-sizer fr"]//a[@class="page-numbers current"]/text()').extract_first()
            patternCode = re.compile(r',| ', re.S)
            sum_result = re.sub(patternCode, '', s)
            page = int(sum_result)/int(p) -1
            self._page = page
            self.isCalculated = True
        
        if(self._i < self._page):
            next_url = "http://stackoverflow.com/search?page=" + str(self._i) + "&tab=Relevance&q=jersey"
            self._i = self._i + 1
            yield Request(next_url, \
                                    callback = self.parse_next_url,\
                                    dont_filter = True)

        # for url in nextlink:
        #     yield scrapy.Request("http://stackoverflow.com"+url, callback=self.parse_next_url)

    
    def parse_page(self, response):         # analyzise each question and the content
        page = ScrapysofItem()
        page['title'] = response.xpath('//*[@id="question-header"]/h1/a/text()').extract_first()
        # page['question'] = response.xpath('//*[@id="question"]/table/tbody/tr[1]//td[@class="postcell"]//div[@class="post-text"]').extract()
        page['url'] = response.url
        page = page.getStackItem(response, page)
        if(page):
            yield page