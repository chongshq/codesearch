import scrapy
import re
from scrapySOF.settings import *
from scrapy.http import Request,FormRequest
from scrapySOF.items import *
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

class ApiDocSpider(scrapy.Spider):
    _i = 1
    isCalculated = False
    isTagQuestion = False
    name = "springmvc"
    allowed_domains = ["spring.io"]
    start_urls = [
        # "http://stackoverflow.com/search?page=1&tab=Relevance&q="+LIB_NAME
        "https://spring.io/guides"
    ]
    def __init__(self):
        self.headers = HEADERS

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            yield FormRequest(url, meta = {'cookiejar': i}, \
                              headers = self.headers, \
                              callback = self.parse, \
                              dont_filter = True)
    

    def parse(self, response):
        guideList = response.xpath('//div[@class="guide--container"]')
        print "--------- fetching content ----------"
        print guideList
        for sel in guideList:
            print ">>>>>>>>>>>> get guide block <<<<<<<<<<<<<"
            page = ScrapyApiDocItem()
            title = sel.xpath('.//a[@class="guide--title"]/text()').extract_first()
            url = sel.xpath('.//a[@class="guide--title"]/@href').extract_first()
            next_full_url = "https://spring.io" + url
            yield Request(next_full_url,\
                                callback = self.parse_page)
    
    def parse_page(self, response):         # analyzise each question and the content
        page = ScrapyApiDocItem()
        title = response.xpath('//h1[@class="title"]/text()').extract_first()
        contentList = response.xpath('//div[@class="content"]')
        for content in contentList:
            code = page.getCode_springmvc(content)
            cleanCode = page.getCleanCode(code)
            if code == "":
                continue
            else:    
                page['url'] = response.url
                page['title'] = title
                page['code'] = code
                page['code_clean'] = cleanCode
                print title, response.url, code
                yield page
        # page['question'] = response.xpath('//*[@id="question"]/table/tbody/tr[1]//td[@class="postcell"]//div[@class="post-text"]').extract()
        

        # if(page):
        #     yield page
