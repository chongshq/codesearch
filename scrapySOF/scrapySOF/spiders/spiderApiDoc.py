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
    name = "apidoc"
    allowed_domains = ["jboss.org"]
    start_urls = [
        # "http://stackoverflow.com/search?page=1&tab=Relevance&q="+LIB_NAME
        "http://docs.jboss.org/hibernate/orm/5.2/userguide/html_single/Hibernate_User_Guide.html"
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
        codeList = response.xpath('//div[@class="exampleblock"]')
        print "--------- fetching content ----------"
        print codeList
        for sel in codeList:
            print ">>>>>>>>>>>> get example block <<<<<<<<<<<<<"
            page = ScrapyApiDocItem()
            content = sel
            title = page.getTitle(content)
            code = page.getCode(content)
            url = response.url
            if title:
                page['title'] = title
            else:
                page['title'] = 'No title'
            page['url'] = url
            page['code'] = code
            yield page
