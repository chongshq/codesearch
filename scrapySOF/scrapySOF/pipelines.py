# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log
from pymongo import MongoClient

class ScrapysofPipeline(object):
    def __init__(self):
		connection = MongoClient(settings['MONGO_HOST'], settings['MONGO_PORT'])
		db = connection[settings['MONGO_DB_NAME']]
		self.collection = db[settings['MONGO_DB_TABLE']+settings['LIB_NAME']]
        
    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing data!")
                
        if valid:
			#self.collection.update({'url':item['url']}, dict(item), upsert = True)
            self.collection.insert(dict(item))
            log.msg("Article add to mongodb database!",level = log.DEBUG, spider = spider)
	    return item
