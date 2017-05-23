#!/usr/bin/python
# -*- coding:utf-8 -*-
import numpy as np
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
from processor import Processor
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora, models, similarities
from settings import *
import nltk.stem
from sklearn.feature_extraction.text import TfidfVectorizer
import gridfs
import os

environment = 1 # 0 测试，1真实

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


class TopicModel(object):
    def __init__(self):
        self.best_doc = None
        self.best_dist = sys.maxint  # 最相似
        self.best_i = None
        self.posts = []
        self.libList = []
        self.corpus = None
        self.dictionary = None
        self.lsi = None
        self.index = None
        #self.process_all_documents()
        #self.testVector()

    def get_libs(self):    # 获取已经爬取的库列表
        self.manager = documentManager()
        collection = self.manager.connect_mongo_lib()
        for loop in collection.find({}):
            # if i == 30:
            #     break
            question = loop["name"]
            self.libList.append(question)

    # 处理所有 MongoDB 中的文档，统计结果 得到 向量化的且经过文本处理的 二维数组 到MongoDB 的分析库  中
    def process_all_documents(self, lib):
        self.manager = documentManager()
        self.posts = []
        collection = self.manager.connect_mongo_sof(lib)
        i = 0
        print "==== start process document ====="
        start = time.clock()
        for loop in collection.find({}):
            # if i == 30:
            #     break
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
        print self.X.toarray()
        # collection = self.manager.connect_analyze()
        # collection.insert({"libname": LIB_NAME,"vector":Binary(pickle.dumps(self.X.toarray(), protocol=2))})
        print "==== vetorization complete  in "+str(end - start)+"seconds ====="

    def build_topicModel(self, corpus, dictionary):
        print "==== generating topic model ... ===="
        lsi = models.LdaModel(corpus = corpus, id2word=dictionary, num_topics = 50
                    # ,update_every = 1,chunksize = 10000
                    )
        
        corpus_lsi = lsi[corpus]
        # print len(lsi.show_topics())
        self.testTopicLen(lsi,corpus)
        print "==== ldamodel constructed ===="
        return lsi
        
    
    def testTopicLen(self, lsi, corpus):
        topics = []
        for doc in corpus:
            topics.append(lsi[doc])
        lens = np.array([len(t) for t in topics])
        print np.mean(lens), np.mean(lens>=2)
        # for topic in topics:
        #     print "topics in one article:===>", topic
        

    def testVector(self):
        self.posts = ["Shipment of gold damaged in a fire <init> !!","Delivery of silver arrived in a silver truck","Shipment of gold arrived in a truck"]
        

    def train(self, env):    # 训练全部主题模型
        self.get_libs()
        processor = Processor()
        for lib in self.libList:
            filename = lib+'.pkl'
            if os.path.exists(filename):
                print lib, "model already exists"
                # self.load_data(lib)
            else:
                print "processing new model...", lib
                if env == 1:
                    self.process_all_documents(lib)
                else:
                    self.testVector()
                texts_after = processor.rm_tokens(self.posts)   # 得到去除停用词的文档二维数组
                self.dictionary = processor.build_dictionary(texts_after) # 构建字典
                self.corpus = processor.build_tfidfModel(texts_after) # 通过构建的字典构建语料库(corpus tfidf),得到包含tfidf的文档向量
                self.lsi = self.build_topicModel(self.corpus, self.dictionary)
                self.index = self.build_index()
                self.dump_data(lib)
                print "Completed!"
        

    def load_data(self,lib):
        self.lsi = models.LdaModel.load(lib+'.pkl')
        self.index = pickle.load(open(lib+"_index.dat","r"))
        self.dictionary = pickle.load(open(lib+"_dictionary.dat","r"))

    def dump_data(self,lib):
        self.lsi.save(lib+'.pkl')
        pickle.dump(self.index, open(lib+"_index.dat","w"))
        pickle.dump(self.dictionary, open(lib+"_dictionary.dat","w"))
        print "all data dumped"
        
    def build_index(self):
        # self.index = pickle.load(open(LIB_NAME+".dat","r"))
        index = similarities.MatrixSimilarity(self.lsi[self.corpus])
        # pickle.dump(self.index, open(LIB_NAME+".dat","w"))
        # print index
        return index


    def find(self,uery):
        # topics = [self.lsi[c] for c in self.corpus]
        # print topics[1]
        processor = Processor()
        input_bow = processor.process_input(self.dictionary, query)
        input_lsi = self.lsi[input_bow] # 将搜索的关键字的词袋映射到主题模型
        # print input_lsi
        sort_input_lsi = sorted(input_lsi, key=lambda item:  -item[1])
        count = 0
        for result in sort_input_lsi:
            if count == 3:
                break
            print "similar topic: ===>", self.lsi.show_topic(sort_input_lsi[count][0])
            count = count + 1
        
        sims = self.index[input_lsi] # 映射到文档预料库的索引中，求得和每个文档的相似度
        # print sims
        sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
        count = 0
        for result in sort_sims:
            if count == 3:
                break
            print "similar article: ===>", sort_sims[count]
            count = count + 1
    
    def show_topics(self, lib):
        self.load_data(lib)
        print self.lsi.show_topics()
        

if __name__ == '__main__':
    topic = TopicModel()
    
    # topic.train(environment)
    # topic.show_topics(LIB_NAME)
    # query = "silver trunk"
    # query = "association"
    
    # print "==== searching" , query , " ... ===="
    # topic.find(query)

    
    
   