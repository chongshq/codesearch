import scrapy
from scrapySOF.settings import *
from scrapy.http import Request,FormRequest
from scrapySOF.items import ScrapysofItem
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

class SOFSpider(CrawlSpider):
    name = "SOF"
    allowed_domains = ["stackoverflow.com"]
    start_urls = [
        "http://stackoverflow.com/search?q=jersey"
    ]
    rules = (
		Rule(SgmlLinkExtractor(allow=(r'/search\?page=.*')), follow=True),
        Rule(SgmlLinkExtractor(allow=(r'/questions/.*'), restrict_xpaths=('//div[@class="question-summary search-result"]'), deny=(r'/questions/tagged/.*')), callback='parse_page', follow=True)
	)

    # def __init__(self):
    #     self.headers = HEADERS

    # def start_requests(self):
    #     for i, url in enumerate(self.start_urls):
    #         yield FormRequest(url, meta = {'cookiejar': i}, \
    #                           headers = self.headers, \
    #                           callback = self.parse)

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

    def parse_next_url(self, response):
        
        questionList = response.xpath('//div[@class="question-summary search-result"]')
        # for sel in questionList:
        #     stars = sel.xpath('.//div[@class="status answered-accepted"]/strong/text()').extract_first()
        #     if(stars):
        #         url = sel.xpath('.//div[@class="result-link"]/span/a/@href').extract_first()
        #         next_full_url = "http://stackoverflow.com"+url
        #         yield scrapy.Request(next_full_url, callback=self.parse_page)
        #         print stars, url
        
        print questionList
        #yield scrapy.Request("http://stackoverflow.com"+nextlink[-1], callback=self.parse)
        

    def parse_page(self, response):
        page = ScrapysofItem()
        page['title'] = response.xpath('//*[@id="question-header"]/h1/a/text()').extract_first()
        # page['question'] = response.xpath('//*[@id="question"]/table/tbody/tr[1]//td[@class="postcell"]//div[@class="post-text"]').extract()
        page['url'] = response.url
        page = page.getStackItem(response, page)
        if(page):
            yield page