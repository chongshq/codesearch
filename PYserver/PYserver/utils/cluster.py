#!/usr/bin/python
# -*- coding:utf-8 -*-
import string
import pickle
import scipy as sp
import sys
import math
import time
import json
import os
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


class CosineSim(object):
    def __init__(self):
        self.best_doc = None
        self.best_dist = 0.0  # 最相似
        self.best_i = None
        self.posts = []
        self.dictionary = []
        self.libList = ["jsoup"]  #mock
        self.vectorList = {}
        self.XList = {}
        #self.testVector()

    def load_vector_cache(self, liblist):
        for lib in liblist:
            self.vectorizer = pickle.load(open('PYserver/utils/index/vocabulary_'+lib+'.json', mode = 'rb'))
            self.X = pickle.load(open("PYserver/utils/index/vector_"+lib+".dat","r"))   #源数据向量化 X,元素a[i][j]表示j词在i类文本中的tf-idf权重
            self.num_samples, self.num_features = self.X.shape       # 样本数和特征数
            self.vectorList[lib] = self.vectorizer
            self.XList[lib] = self.X

    def load_vector_test(self, liblist):
        for lib in liblist:
            self.vectorizer = pickle.load(open('index/vocabulary_'+lib+'.json', mode = 'rb'))
            self.X = pickle.load(open("index/vector_"+lib+".dat","r"))   #源数据向量化 X,元素a[i][j]表示j词在i类文本中的tf-idf权重
            self.num_samples, self.num_features = self.X.shape       # 样本数和特征数
            self.vectorList[lib] = self.vectorizer
            self.XList[lib] = self.X

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
            collection.update({"_id":_id},{"$set" : {"id" : i}})
            # if(i<10):
            self.dictionary.append(_id)
            self.posts.append(content)
            i = i+1
            # else:
            #     break
        end = time.clock()
        print "==== process document complete in "+str(end - start)+"seconds ====="
        	#print _id.str
        	# code = loop["code"]
    def getContent(self):
        return self.posts
    # def getTestRaw(self):
    #     return self.test_raw

    def vectorize(self, vectorizer):
        filename = 'index/vocabulary_'+LIB_NAME+'.json'
        if os.path.exists(filename):
            vectorizer = pickle.load(open(filename, mode = 'rb'))
            self.X = pickle.load(open("index/vector_"+LIB_NAME+".dat","r"))   #源数据向量化 X,元素a[i][j]表示j词在i类文本中的tf-idf权重
            self.num_samples, self.num_features = self.X.shape       # 样本数和特征数
        else:

            self.process_all_documents()
            start = time.clock()
            print "==== start vectorizing ====="
            self.X = vectorizer.fit_transform(self.posts)     #源数据向量化 X,元素a[i][j]表示j词在i类文本中的tf-idf权重
            self.num_samples, self.num_features = self.X.shape       # 样本数和特征数
            end = time.clock()
            # print self.X.toarray()
            weight = self.X.toarray()
            word_dictionary = vectorizer.get_feature_names()   # 文本空间中的字典
            for i in range(len(weight)):#打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
                # print u"-------第",i,u"个帖子的词语tf-idf权重------"
                for j in range(len(word_dictionary)):
                    # print word_dictionary[j],weight[i][j]   # 权重矩阵的行即为字典的单词id
                    continue
            print "==== vetorization complete  in "+str(end - start)+"seconds ====="
            pickle.dump(vectorizer, open(filename, mode = 'wb'))
            pickle.dump(self.X, open("index/vector_"+LIB_NAME+".dat","w"))
        return vectorizer

    def dist_norm(self, v1, v2):  # 词频向量的欧式距离 向量归一化
        v1_normalized = v1/sp.linalg.norm(v1.toarray())
        v2_normalized = v2/sp.linalg.norm(v2.toarray())
        delta = v1_normalized - v2_normalized
        return sp.linalg.norm(delta.toarray())

    def cos(self, vector1,vector2):  
        dot_product = 0.0;  
        normA = 0.0;  
        normB = 0.0;  
        for a,b in zip(vector1,vector2):  
            dot_product += a*b  
            normA += a**2  
            normB += b**2  
        if normA == 0.0 or normB==0.0:  
            return None  
        else:  
            return dot_product / ((normA*normB)**0.5)  

    def getBest(self, input_search, input_search_vec):
        start = time.clock()
        print " ==== fetching best related ... ===="
        for i in range(0, self.num_samples):
            # post = self.posts[i]    # 循环访问源数据向量
            # if post == input_search:
            #     continue
            post_vec = self.X.getrow(i)
            d = self.cos(post_vec.toarray()[0], input_search_vec.toarray()[0])
            print i, d
            if d>self.best_dist:
                self.best_dist = d
                self.best_i = i
        end = time.clock()
        print "best  in ",str(end - start),"seconds ====>", self.best_i
            #, "\n",self.posts[self.best_i]

    def getBestFromDoc(self, input_search, id_list, lib):
        input_search_vec = self.vectorList[lib].transform([input_search])
        start = time.clock()
        print " ==== fetching best related ... ===="
        tuple_list = []
        print id_list
        for i in id_list:
            # post = self.posts[i]    # 循环访问源数据向量
            # if post == input_search:
            #     continue
            # print "calculating:", i
            try:
                post_vec = self.XList[lib].getrow(int(i))
                d = self.cos(post_vec.toarray()[0], input_search_vec.toarray()[0])
                t = (i, d)
                tuple_list.append(t)
                if d>self.best_dist:
                    self.best_dist = d
                    self.best_i = i
            except IndexError:
                print i
        print "sorting result"
        sorted_list = sorted(tuple_list,key=lambda x: x[1], reverse = True)
        end = time.clock()
        print "best  in ",str(end - start),"seconds ====>", self.best_i
        result_doc_id = []
        count = 0
        for item in sorted_list:
            if count == 5:
                break
            result_doc_id.append(item[0])
            count = count+1
        # print sorted_list
        print result_doc_id
        return result_doc_id
            #, "\n",self.posts[self.best_i]
    
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
    cos = CosineSim()
    vectorizer = TfidfVectorizer(min_df=1)    # 出现频率小于min_df的词语都会被丢弃 并加入停用词过滤
    
    # vectorizer = StemmedTfidfVectorizer(min_df=1, stop_words='english')
    vectorizer = cos.vectorize(vectorizer)

    # input_search = "Entity"
    # input_search_vec = vectorizer.transform([input_search])
    # cos.getBest(input_search, input_search_vec)