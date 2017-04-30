#!/usr/bin/python
# -*- coding:utf-8 -*-
import string
import pickle
import scipy as sp
import sys
import math
import time
from timeit import Timer
from bson.binary import Binary
from sklearn.feature_extraction.text import CountVectorizer
from documentManager import documentManager
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora, models, similarities
from settings import *
import nltk.stem
from sklearn.feature_extraction.text import TfidfVectorizer
import gridfs



class StemmedCountVectorizer(CountVectorizer):
    def build_analyzer(self):
        english_stemmer = nltk.stem.SnowballStemmer('english')
        analyzer = super(StemmedCountVectorizer, self).build_analyzer()
        return lambda doc: (english_stemmer.stem(w) for w in analyzer(doc))


class StemmedTfidfVectorizer(TfidfVectorizer):
    def build_analyzer(self):
        english_stemmer = nltk.stem.SnowballStemmer('english')
        analyzer = super(StemmedTfidfVectorizer, self).build_analyzer()
        return lambda doc: (english_stemmer.stem(w) for w in analyzer(doc))


class Cluster(object):
    def __init__(self):
        self.best_doc = None
        self.best_dist = sys.maxint  # 最相似
        self.best_i = None
        self.posts = []
        self.process_all_documents()
        #self.testVector()

    # 处理所有 MongoDB 中的文档，统计结果 得到 向量化的且经过文本处理的 二维数组 到MongoDB 的分析库  中
    def process_all_documents(self):
        self.manager = documentManager()
        collection = self.manager.connect_mongo()
        i = 0
        print "==== start process document ====="
        start = time.clock()
        for loop in collection.find({}):
            
            question = loop["question"]
            answer = loop["answer"]
            _id = loop["_id"]
            content = question + "\n"+ answer
            if(i == 0):
                self.test_raw = content
                i = i+1
            self.posts.append(content)
        end = time.clock()
        print "==== process document complete in "+str(end - start)+"seconds ====="
        	#print _id.str
        	# code = loop["code"]
    def getContent(self):
        return self.posts
    def getTestRaw(self):
        return self.test_raw

    def vectorize(self, vectorizer):
        start = time.clock()
        print "==== start vectorizing ====="
        self.X = vectorizer.fit_transform(self.posts)     #源数据向量化 X
        self.num_samples, self.num_features = self.X.shape       # 样本数和特征数
        end = time.clock()
        # print self.X.toarray()
        # collection = self.manager.connect_analyze()
        # collection.insert({"libname": LIB_NAME,"vector":Binary(pickle.dumps(self.X.toarray(), protocol=2))})
        print "==== vetorization complete  in "+str(end - start)+"seconds ====="

    def dist_norm(self, v1, v2):  # 词频向量的欧式距离 向量归一化
        v1_normalized = v1/sp.linalg.norm(v1.toarray())
        v2_normalized = v2/sp.linalg.norm(v2.toarray())
        delta = v1_normalized - v2_normalized
        return sp.linalg.norm(delta.toarray())

    def getBest(self, input_search, input_search_vec):
        start = time.clock()
        print " ==== fetching best related ... ===="
        for i in range(0, self.num_samples):
            post = self.posts[i]    # 循环访问源数据向量
            if post == input_search:
                continue
            post_vec = self.X.getrow(i)
            d = self.dist_norm(post_vec, input_search_vec)
            #print i, d
            if d<self.best_dist:
                self.best_dist = d
                self.best_i = i
        end = time.clock()
        print "best  in ",str(end - start),"seconds ====>", self.posts[self.best_i]
    
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
    # vectorizer = TfidfVectorizer(min_df=1, stop_words='english')    # 出现频率小于min_df的词语都会被丢弃 并加入停用词过滤
    
    vectorizer = StemmedTfidfVectorizer(min_df=1, stop_words='english')
    cluster.vectorize(vectorizer)

    input_search = cluster.getTestRaw()
    input_search_vec = vectorizer.transform([input_search])
    cluster.getBest(input_search, input_search_vec)