# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from pyquery import PyQuery

class ScrapyApiDocItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    url = scrapy.Field()
    code = scrapy.Field()
    code_clean = scrapy.Field()

    def getTitle(self, content):
        titleTemp = PyQuery(content.xpath('.//div[@class="title"]').extract_first())
        title = titleTemp.html()
        return title
        
    def getCleanCode(self, content):
        pS = re.compile(
                    r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
                    re.DOTALL | re.MULTILINE
                )
        cleanCode = re.sub(pS, "", content)
        return cleanCode

    def getCode(self, content):
        codeSet = PyQuery(content.xpath('.//div[@class="content"]').extract_first()) 
        haveCode = codeSet('code')
        itemCode = ""
        count = 0
        for c in codeSet('code'):
            count = count + 1
            print "have ", count, " piece of code"
            itemCode = itemCode + "\n"+ PyQuery(c).html()     # 获取完整代码
        return itemCode
        # print "code: ",itemCode
    def getCode_springmvc(self, content):
        pre = content.xpath('.//pre')
        
        code = PyQuery(pre.extract_first())
        itemCode = ""
        
        if code('code').attr('class') == 'language-java':
            pS = re.compile(
                    r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
                    re.DOTALL | re.MULTILINE
                )
            code = re.sub(pS, "", PyQuery(code('code')).html() )
            itemCode = itemCode + "\n"+ code    # 获取完整代码
        return itemCode
        # print "code: ",itemCode

class ScrapysofItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    url = scrapy.Field()
    question = scrapy.Field()
    question_stars = scrapy.Field()
    answer = scrapy.Field()
    answer_stars = scrapy.Field()
    code = scrapy.Field()
    code_clean = scrapy.Field()

    def getStackItem(self,response,item):
        item = self.getStackAnswer(response,item)
        if(item):
            item = self.getStackQuestion(response,item)
            return item
        else:
            return None

    def getStackQuestion(self,response,item):
        patternForQuestion = re.compile(
            '<div id="mainbar".*?class="vote-count-post.*?>(.*?)</span>.*?<td class="postcell".*?<div class="post-text".*?>(.*?)</div>', re.S)

        patternCode = re.compile(r'<[^>]+>', re.S)
        items = re.search(patternForQuestion, response.body)
        itemQuestion = re.sub(patternCode, "", items.group(2))
        if(items):
            # print("-----question:------")
            # print items.group(1) + " " + itemQuestion
            item['question_stars'] = items.group(1)
            item['question'] = itemQuestion
            
            return item
        else:
            print "not found"
            return None


    def getStackAnswer(self,response,item):
        # patternForAnswer = re.compile(
        #     '<div id="answer-.*?".*?vote-count-post.*?>(.*?)</span>.*?<span class="vote-accepted-on.*?<div class="post-text".*?>(.*?)</div>', re.S)
        patternCode = re.compile(r'<[^>]+>', re.S)
        items = response.xpath('//*[@id="answers"]//div[contains(@class,"accepted-answer")]')    # 判断是否有已经accept的回答
        if(items):
            answerText = PyQuery(items.xpath('.//div[@class="post-text"]').extract_first())   
            haveCode = answerText('code')
            if(haveCode):   # 判断回答中是否用代码
                itemCode = ""
                for c in answerText('code'):
                    itemCode = itemCode + "\n"+ self.getValidCode(c)     # 获取完整代码
                itemAnswer = re.sub(patternCode, "", answerText.html())
                itemStar = items.xpath('.//div[@class="vote"]//span[contains(@class,"vote-count-post")]/text()').extract_first()
                
                item['answer'] = itemAnswer
                item['answer_stars'] = itemStar
                item['code'] = itemCode
                item['code_clean'] = self.getCleanCode(itemCode)
                #print itemCode
                
                return item
            else:
                print "not found code"
                return None
                
        else:
            print "not found answer"
            return None

    def getValidCode(self, code):
        tempCode = PyQuery(code).html()
        if tempCode.find('=') or tempCode.find('.')  or tempCode.find('@')  or tempCode.find(';') or len(tempCode) > 15:
            return tempCode
        else:
            return ""
    
    def getCleanCode(self, code):
        
        pS = re.compile(
                r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
                re.DOTALL | re.MULTILINE
            )
        cleanCode = re.sub(pS, "", code)
        return cleanCode