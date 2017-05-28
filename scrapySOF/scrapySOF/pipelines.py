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
        if settings['ENV'] == 1:
            tableName = settings['MONGO_DB_TABLE_APIDOC']+settings['LIB_NAME']
        else:
            tableName = settings['MONGO_DB_TABLE']+settings['LIB_NAME']
        connection = MongoClient(settings['MONGO_HOST'], settings['MONGO_PORT'])
        db = connection[settings['MONGO_DB_NAME']]
        self.collection = db[tableName]
        self.lib_collection = db['MONGO_DB_TABLE_LIB']

    def open_spider(self, spider):
        print "starting pipeline for DB:", settings['LIB_NAME']

    def close_spider(self, spider):
        # self.collection.ensure_index("code_clean", unique=True)
        # self.lib_collection.insert({"name":'LIB_NAME',"language":"java"})
        print "finish"

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
