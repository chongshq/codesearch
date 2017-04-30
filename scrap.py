import urllib
import urllib2
import cookielib
import re


class scrapy_test(object):
    def __init__(self):
		pass

    def getHtml(self,url, data):
        request = urllib2.Request(url, data)
        try:
            page = urllib2.urlopen(request)
        except urllib2.URLError, e:
            print e.reason
        html = page.read()
        return html

    def getHtmlNoData(self,url, header):
        request = urllib2.Request(url, headers=header)
        try:
            page = urllib2.urlopen(request)
        except urllib2.URLError, e:
            print e.reason
        html = page.read()
        return html


    def getStackHeader(self,url, header):
        request = urllib2.Request(url, headers=header)
        try:
            page = urllib2.urlopen(request)
        except urllib2.URLError, e:
            print e.reason
        html = page.read()
        patternForHeader = re.compile(
            '<div id="question-header".*?<h1.*?<a href.*?class="question-hyperlink">(.*?)</a>', re.S)
        items = re.search(patternForHeader, html)
        if(items):
            print items.group(1)
            self.getStackQuestion(html)
            self.getStackAnswer(html)
        else:
            print "not found"

        return html


    def getStackQuestion(self,page):
        patternForQuestion = re.compile(
            '<div id="mainbar".*?class="vote-count-post.*?>(.*?)</span>.*?<td class="postcell".*?<div class="post-text".*?>(.*?)</div>', re.S)
        items = re.search(patternForQuestion, page)
        if(items):
            print("-----question:------")
            print items.group(1) + " " + items.group(2)
        else:
            print "not found"


    def getStackAnswer(self,page):
        patternForAnswer = re.compile(
            '<div id="answer-.*?".*?vote-count-post.*?>(.*?)</span>.*?<span class="vote-accepted-on.*?<div class="post-text".*?>(.*?)</div>', re.S)
        patternCode = re.compile(
            '<p>|</p>|<a.*?>|</a>|<ul>|</ul>|<li>|</li>|<strong>|</strong>')
        items = re.search(patternForAnswer, page)
        print "searching code ....."
        if(items):
                print "found .."
                itemAnswer = re.sub(patternCode, "", items.group(2))
                haveCode = re.findall("<pre>(.*?)</pre>", items.group(2))
                print itemAnswer
                if haveCode:
                    print items.group(1), itemAnswer
        else:
            print "not found"


# cookie = cookielib.CookieJar()
# handler = urllib2.HTTPCookieProcessor(cookie)
# opener = urllib2.build_opener(handler)
# values = {"username": "00000", "password": "123456"}
# data = urllib.urlencode(values)
# htmlTemp = "http://admin.qiancs.cn/admin/login.php"
# htmlBaike = 'http://www.qiushibaike.com/hot/page/1'
# htmlS = "http://stackoverflow.com/questions/5042886/resteasy-or-jersey"
# headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

# response = opener.open("https://baidu.com")
# mySrapyTest = scrapy_test()
# html = mySrapyTest.getHtmlNoData(htmlS, headers).decode('utf-8')
# patternReplace = re.compile('<span>|</span>|<br>|<br/>')
# pattern = re.compile(
#     '<div class="author clearfix">.*?href.*?<img src.*?title=.*?<h2>(.*?)</h2>.*?<div class="content">(.*?)</div>.*?<i class="number">(.*?)</i>', re.S)

#page = mySrapyTest.getStackHeader(htmlS, headers)

#cookie.save(ignore_discard=True, ignore_expires=True)
# for item in items:
#haveImg = re.search("img",item[3])
# if not haveImg:
#itemClean = re.sub(patternReplace,"",item[1])
# print item[0],itemClean,item[2]


# print html

# result = re.search(pattern, 'fefediv')
# if result:
#     print result.group()
# else:
#     print "error"
