import scrapy
import re
from scrapySOF.settings import *
from scrapy.http import Request,FormRequest
from scrapySOF.items import ScrapysofItem
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

class SOFSpider(scrapy.Spider):
    _i = 1
    isCalculated = False
    name = "SOFTest"
    allowed_domains = ["stackoverflow.com"]
    start_urls = [
        "http://stackoverflow.com/search?page=1&tab=Relevance&q=jersey"
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
        if(self.isCalculated == False):
            s = response.xpath('//*[@id="mainbar"]//div[@class="subheader results-header"]/h2/text()').extract_first()
            p = response.xpath('//*[@id="mainbar"]//div[@class="page-sizer fr"]//a[@class="page-numbers current"]/text()').extract_first()
            patternCode = re.compile(r',| ', re.S)
            sum_result = re.sub(patternCode, '', s)
            page = int(sum_result)/int(p) -1
            self._page = page
            self.isCalculated = True
            print "--------- page calculated ----------"
        
        questionList = response.xpath('//div[@class="question-summary search-result"]')
        print "--------- fetching content ----------"
        print questionList
        for sel in questionList:
            print ">>>>>>>>>>>> Q & A <<<<<<<<<<<<<"
            stars = sel.xpath('.//div[@class="status answered-accepted"]/strong/text()').extract_first()
            if(stars):
                url = sel.xpath('.//div[@class="result-link"]/span/a/@href').extract_first()
                next_full_url = "http://stackoverflow.com"+url
                yield Request(next_full_url,\
                              callback = self.parse_page)
                print "content url =======>" + response.urljoin(url)

       # if have next page ?

        if(self._i < self._page):
            next_url = "http://stackoverflow.com/search?page=" + str(self._i) + "&tab=Relevance&q=jersey"
            self._i = self._i + 1
            print "next page url =======> " + next_url
            yield Request(next_url, \
                                callback = self.parse,\
                                headers = self.headers)
            
    
    def parse_page(self, response):         # analyzise each question and the content
        page = ScrapysofItem()
        page['title'] = response.xpath('//*[@id="question-header"]/h1/a/text()').extract_first()
        # page['question'] = response.xpath('//*[@id="question"]/table/tbody/tr[1]//td[@class="postcell"]//div[@class="post-text"]').extract()
        page['url'] = response.url
        page = page.getStackItem(response, page)
        if(page):
            yield page