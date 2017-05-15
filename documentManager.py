#!/usr/bin/python
# -*- coding:utf-8 -*-

from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import pickle
import re
import sys
from scrap import scrapy_test
from settings import *

reload(sys)
sys.setdefaultencoding("utf8")

class documentManager(object):
	def __init__(self):
		self.seeds_temp = set([])
		self.seeds = set([])
		self.seeds_visited = set([])

	def connect_mongo(self):
		client = MongoClient(MONGO_HOST,MONGO_PORT)
		db = client[MONGO_DB_NAME]
		collection = db[MONGO_DB_TABLE+LIB_NAME]
		return collection
	
	def connect_mongo_sof(self, lib):
		client = MongoClient(MONGO_HOST,MONGO_PORT)
		db = client[MONGO_DB_NAME]
		collection = db[MONGO_DB_TABLE+lib]
		return collection

	def connect_mongo_lib(self):
		client = MongoClient(MONGO_HOST,MONGO_PORT)
		db = client[MONGO_DB_NAME]
		collection = db[MONGO_DB_TABLE_LIB]
		return collection

	def connect_analyze(self):
		client = MongoClient(MONGO_HOST,MONGO_PORT)
		db = client[MONGO_DB_NAME]
		collection = db[MONGO_DB_TABLE_ANALYZE+LIB_NAME]
		return collection
		# mydict = {"name":"Lucy", "sex":"female","job":"nurse"}
		# collection.insert(mydict)
		# for i in collection.find():
		# 	print i

	def crawl_url(self, target_url):
		headers_base = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch',
		'Accept-Language': 'en-US,en;q=0.8',
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/40.0.2214.111 Chrome/40.0.2214.111 Safari/537.36',
		}

		ret = requests.get(target_url, headers=headers_base)
		# print 'crawl status: %s', ret.status_code
		return ret.text

	def collect_seeds_sof(self, seed_url):
		mydb = open('seedbase_sof', 'w')
		self.seeds_visited.add(seed_url)
		pickle.dump(self.seeds_visited, mydb)
		print "seeds are OK!!!!"

	# 抓取 WIKI 的有效 URL
	def collect_seeds(self, seed_url):		
		page = self.crawl_url(seed_url)
		soup = BeautifulSoup(page)
		pat = re.compile(r'/wiki/*')

		for one in soup.find_all('a'):
			if pat.match(str(one.get('href'))) is None:
				continue
			new_url = pat.match(str(one.get('href'))).string

			if new_url not in self.seeds and new_url not in self.seeds_visited:
				self.seeds.add(new_url)

		self.seeds_temp = self.seeds
		# for url in self.seeds_temp:
		# 	self.seeds_visited.add(url)
		# 	self.seeds.remove(url)

		# 	# 收集 100 链接之后将数据持久化并退出
		# 	if len(self.seeds_visited) == 100:
		# 		mydb = open('seedbase', 'w')
		# 		pickle.dump(self.seeds_visited, mydb)
		# 		print "seeds are OK!!!!"
		# 		return 

		# 	another_url = 'https://en.wikipedia.org' + url
		# 	self.collect_seeds(another_url)

	def collect_content_sof_test(self):
		mydb = open('seedbase_sof', 'r')
		seeds = pickle.load(mydb)
		docid_cnt = 1
		seed = "preparedstatement"
		headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'} 
		for seed in seeds:
			seed_url = seed
			scrapy = scrapy_test()
			content = scrapy.getStackHeader(htmlS, headers)
			posting = {
					"DocID": docid_cnt,
					"url": seed_url,
					"content": content,
					"keyword": seed
					}

			docid_cnt += 1
			collection = self.connect_mongo()
			collection.insert(posting)

	def collect_content(self):
		mydb = open('seedbase', 'r')
		seeds = pickle.load(mydb)
		docid_cnt = 1
		for seed in seeds:
			seed_url = 'https://en.wikipedia.org' + seed
			page = self.crawl_url(seed_url)
			soup = BeautifulSoup(page)
			data = soup(class_='mw-content-ltr')
			# 去除 HTML 标签
			dr = re.compile(r'<[^>]+>', re.S)
			pure_data = dr.sub('', str(data))
			# 去除回车
			content = "".join(pure_data.split('\n'))

			# 构造存入 MongoDB 的数据

			posting = {
				"DocID": docid_cnt,
				"url": seed_url,
				"content": content,
				"keyword": seed
				}

			docid_cnt += 1
			collection = self.connect_mongo()
			collection.insert(posting)

		# test data
		# loop = 0
		# collection = self.connect_mongo()
		# for i in collection.find():
		# 	print i
		# 	loop += 1
		# 	if loop == 3:
		# 		break

if __name__ == '__main__':
	#seed_url = 'https://en.wikipedia.org/wiki/Main_Page'
	manager = documentManager()
	manager.connect_mongo()
	#manager.collect_seeds(seed_url)
	# manager.collect_content()

	# htmlS = "http://stackoverflow.com/questions/3271249/difference-between-statement-and-preparedstatement" #test!
	# manager.collect_seeds_sof(htmlS)
	# manager.collect_content_sof_test()