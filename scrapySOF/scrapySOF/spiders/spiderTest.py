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
    isTagQuestion = False
    name = "SOFTest"
    allowed_domains = ["stackoverflow.com"]
    start_urls = [
        # "http://stackoverflow.com/search?page=1&tab=Relevance&q="+LIB_NAME
        "http://stackoverflow.com/questions/tagged/"+LIB_NAME+"?sort=votes&pageSize=15"
    ]
    def __init__(self):
        self.headers = HEADERS

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            yield FormRequest(url, meta = {'cookiejar': i}, \
                              headers = self.headers, \
                              callback = self.parse, \
                              dont_filter = True)
    
    def calculatePageNum(self, response):
        if(self.isCalculated == False):
            s = response.xpath('//*[@id="questions-count"]//div[@class="summarycount al"]/text()').extract_first()
            p = response.xpath('//*[@id="mainbar"]//div[@class="page-sizer fr"]//a[@class="page-numbers current"]/text()').extract_first()
            print s,p
            patternCode = re.compile(r',| ', re.S)
            sum_result = re.sub(patternCode, '', s)
            page = int(sum_result)/int(p) -1
            self._page = page
            self.isCalculated = True
            print "--------- page calculated ----------"

    def parse(self, response):
        if(not self.isCalculated):
            tag = response.xpath('//*[@id="mainbar"]//div[@class="subheader"]/h1/text()').extract_first()
            print tag
            if(tag == "Tagged Questions"):
                self.isCalculated = True
                self.isTagQuestion = True
            else:
                self.isCalculated = True
                self.isTagQuestion = False
        if(self.isTagQuestion):
            questionList = response.xpath('//div[@id="questions"]//div[@class="question-summary"]')
            print "--------- fetching content for tag----------"
            print questionList
            for sel in questionList:
                print ">>>>>>>>>>>> Q & A <<<<<<<<<<<<<"
                isAccepted = response.xpath('.//div[@class="status answered-accepted"]')
                if(isAccepted):
                    url = sel.xpath('.//a[@class="question-hyperlink"]/@href').extract_first()
                    next_full_url = "http://stackoverflow.com"+url
                    yield Request(next_full_url,\
                                callback = self.parse_page)
                    print "content url =======>" + response.urljoin(url)
        else:
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

        # if(self._i < self._page):
        next_url = "http://stackoverflow.com" + response.xpath('//*[@id="mainbar"]//div[@class="pager fl"]//a[@rel="next"]/@href').extract_first()
        #next_url = "http://stackoverflow.com/search?page=" + str(self._i) + "&tab=Relevance&q="+LIB_NAME
        self._i = self._i + 1
        if(next_url):
            print "next page url =======> " + next_url
            yield Request(next_url, \
                                callback = self.parse)
            
    
    def parse_page(self, response):         # analyzise each question and the content
        page = ScrapysofItem()
        page['title'] = response.xpath('//*[@id="question-header"]/h1/a/text()').extract_first()
        # page['question'] = response.xpath('//*[@id="question"]/table/tbody/tr[1]//td[@class="postcell"]//div[@class="post-text"]').extract()
        page['url'] = response.url
        page = page.getStackItem(response, page)
        if(page):
            yield page