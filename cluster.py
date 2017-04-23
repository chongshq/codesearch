#!/usr/bin/python
# -*- coding:utf-8 -*-
import string
import pickle
import scipy as sp
import sys
import math
from timeit import Timer
from sklearn.feature_extraction.text import CountVectorizer
from documentManager import documentManager
from sklearn.feature_extraction.text import TfidfVectorizer

class Cluster(object):
    def __init__(self):
        self.best_doc = None
        self.best_dist = sys.maxint  # 最相似
        self.best_i = None
        self.posts = []
        self.process_all_documents()
        #self.testVector()

    # 处理所有 MongoDB 中的文档，统计结果 <word, DocID, Freq> 写入到文本 wiki-result 中
    def process_all_documents(self):
        manager = documentManager()
        collection = manager.connect_mongo()
        i = 0
        print "==== start process document ====="
        for loop in collection.find({}):
            
            question = loop["question"]
            answer = loop["answer"]
            _id = loop["_id"]
            content = question + "\n"+ answer
            if(i == 0):
                self.test_raw = content
                i = i+1
            self.posts.append(content)
        print "==== process document complete ====="
        	#print _id.str
        	# code = loop["code"]
    def getContent(self):
        return self.posts
    def getTestRaw(self):
        return self.test_raw

    def vectorize(self, vectorizer):
        print "==== start vectorizing ====="
        self.X = vectorizer.fit_transform(self.posts)     #源数据向量化 X
        self.num_samples, self.num_features = self.X.shape       # 样本数和特征数
        print "==== vetorization complete ====="

    def dist_norm(self, v1, v2):  # 词频向量的欧式距离 向量归一化
        v1_normalized = v1/sp.linalg.norm(v1.toarray())
        v2_normalized = v2/sp.linalg.norm(v2.toarray())
        delta = v1_normalized - v2_normalized
        return sp.linalg.norm(delta.toarray())

    def getBest(self, input_search, input_search_vec):
        print " ==== fetching best related ... ===="
        for i in range(0, self.num_samples):
            post = self.posts[i]    # 循环访问源数据向量
            if post == input_search:
                continue
            post_vec = self.X.getrow(i)
            d = self.dist_norm(post_vec, input_search_vec)
            print i, d
            if d<self.best_dist:
                self.best_dist = d
                self.best_i = i
        print "best====>", self.best_i, self.best_dist
    
    def tfidf(self,term,doc,docset):
        tf = float(doc.count(term))/sum(doc.count(w) for w in docset)
        idf = math.log(float(len(docset))/(len([doc for doc in docset 
                            if term in doc])))
        return tf*idf

    def testVector(self):
        self.posts.append("this is a toy in the past")
        self.posts.append("Imaging databases can get huge")
        self.posts.append("Most imaging databases safe images permanently")

# class StemmedTfidfVectorizer(TfidfVectorizer):
#     def build_analyzer(self):
#         analyzer = super(TfidfVectorizer,
#                         self).build_analyzer()
#         return lambda doc: (english_stemmer.stem(w) for w in analyzer(doc))

if __name__ == '__main__':
    cluster = Cluster()
    vectorizer = TfidfVectorizer(min_df=1, stop_words='english')    # 出现频率小于min_df的词语都会被丢弃 并加入停用词过滤
    cluster.vectorize(vectorizer)

    input_search = cluster.getTestRaw()
    input_search_vec = vectorizer.transform([input_search])
    cluster.getBest(input_search, input_search_vec)