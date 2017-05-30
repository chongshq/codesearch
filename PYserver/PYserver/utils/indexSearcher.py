#!/usr/bin/python
# -*- coding:utf-8 -*-

import pickle
import math
from documentManager import documentManager
from cluster import CosineSim
from bson.objectid import ObjectId

class indexSearcher(object):
	
	def __init__(self):

		self.libList = ["jsoup"]  #mock
		self.id_list = []
		self.indexList = {}
		self.manager = documentManager()
	
	def get_libs(self):    # 获取已经爬取的库列表
		self.manager = documentManager()
		collection = self.manager.connect_mongo_lib()
		for loop in collection.find({}):
			question = loop["name"]
			self.libList.append(question)
		return self.libList

	def load_index_cache(self, liblist):
		for lib in liblist:

			self.mydb = open('PYserver/utils/index/sof-postings-'+ lib, 'r')
			self.word_dictionary = pickle.load(self.mydb)
			self.indexList[lib] = self.word_dictionary

	def load_index_test(self, liblist):
		for lib in liblist:

			self.mydb = open('index/sof-postings-'+ lib, 'r')
			self.word_dictionary = pickle.load(self.mydb)
			self.indexList[lib] = self.word_dictionary
	# 计算每个文档的 TF-IDF 值，进行排序
	def caculate_TFIDF(self, word):
		score_dictionary = {}

		if not self.word_dictionary.has_key(word):
			return 0
		
		for posting in self.word_dictionary[word]:
			DocID = posting[0]
			freq = posting[1]

			idf = math.log(float(100) / len(self.word_dictionary[word]))
			tf = 1 + math.log(int(freq)) if freq > 0 else 0
			tfidf_score = tf * idf
			score_dictionary[DocID] = tfidf_score

		score = sorted(score_dictionary.iteritems(), key=lambda d:d[1], reverse = True)
		return score

	def get_wordcount_in_document(self, word, content):
		word_list = content.split(' ')
		cnt = 0
		for one in word_list:
			if one == word:
				cnt += 1
		return cnt

	def DocID2Doc(self, DocID):
		manager = documentManager()
		collection = manager.connect_mongo()
		result = collection.find_one({"_id": ObjectId(DocID)})
		url = result["url"]
		code = result["code"]
		re = {}
		re["url"] = url
		re["code"] = code
		return re

	# 计算 BM25，设定　ｃ(w,q) 为　１，即查询中每个词出现一次
	def caculate_BM25(self, query_words):
		manager = documentManager()
		collection = manager.connect_mongo()
		
		score_dictionary = {}
		b = 0.5 #参数调节因子
		k = 10 # 调节因子
		avdl = 800 # 文档平均长度

		# query_words 中至少一个单元词出现的所有文档
		DocId_of_query_words = set([])
		for word in query_words.split(' '):

			if not self.word_dictionary.has_key(word):
				continue

			for posting in self.word_dictionary[word]:
				DocID = posting[0]
				DocId_of_query_words.add(DocID)
		
		for id in DocId_of_query_words:
			BM25_score = 0
			for word in query_words.split(' '):
				content = collection.find_one({"_id": ObjectId(id)})["answer"]
				freq = self.get_wordcount_in_document(word ,content)
				
				doc_len = len(self.word_dictionary[word])
				idf = math.log(float(100) / doc_len)
				normalizer = 1 - b + b * (doc_len / avdl) 

				BM25_score += (float)((k + 1) * freq) / (freq + k * normalizer) * idf
			# 计算某个文档对　Query 的 BM25 分数 
			score_dictionary[id] = BM25_score

		score = sorted(score_dictionary.iteritems(), key=lambda d:d[1], reverse = True)

		for i in score:
			print self.DocID2Doc(i[0])


	def retrive_word(self, word, lib):
		# 找出 DocID 对应的 url
		
		id_list = []
		try:
			for word in self.indexList[lib][word]:
				id_list.append(word[0])
		except KeyError:
			id_list = []
		# print id_list
		return id_list   # 文档id列表

	def perform_query(self, query_input, lib, cos):
		id_list = []
		output_num = 5 #返回用户的结果个数
		words = query_input.split(' ')
		print "retrive word"
		for word in words:
			temp = self.retrive_word(word, lib)
			for id in temp:
				if id not in self.id_list:
					self.id_list.append(id)
		print "fetch top5"
		top5 = cos.getBestFromDoc(query_input, self.id_list, lib)
		print "get top5 results"
		results=[]
		if len(top5) == 0:
			return results
		# score_dict = self.caculate_TFIDF(word)
		else:
			print "collecting data"
			count = 0
			collection = self.manager.connect_mongo_sof(lib)
			
			for result in top5:
				if count == 5:
					break
				temp = collection.find_one({"id":int(result)})
				# print temp
				temp_result = {}
				temp_result["title"] = temp["title"]
				temp_result["url"] = temp["url"]
				temp_result["code"] = temp["code"]
				results.append(temp_result)
				count = count + 1
			print "return data"
			return results
		# 	count = 0
		# 	for pair in score_dict:
		# 		if count == output_num:
		# 			break
		# 		else:
		# 			count += 1
		# 			id_list.append(pair[0])
		# return id_list
				
if __name__ == '__main__':
	searcher = indexSearcher()
	searcher.load_index_test(["hibernate"])
	cos = CosineSim()
	cos.load_vector_test(["hibernate"])
	searcher.perform_query("annotation","hibernate",cos)
	# searcher.caculate_BM25("Genson")