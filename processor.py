#!/usr/bin/python
# -*- coding:utf-8 -*-
import string
import pickle
import scipy as sp
import sys
import math
import time
import re
from timeit import Timer
from bson.binary import Binary
from sklearn.feature_extraction.text import CountVectorizer
from documentManager import documentManager
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora, models, similarities
from settings import *
import nltk.stem
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import gridfs
import HTMLParser

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


class Processor(object):
    def __init__(self):
        self.english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%', '<', '>']

    # 处理所有 MongoDB 中的文档，统计结果 得到 向量化的且经过文本处理的 二维数组 到MongoDB 的分析库  中
    def rm_tokens(self, passages_before):  # nltk 去掉一些停用次和数字
        print "==== start tokenizeing ... ===="
        s = nltk.stem.SnowballStemmer('english')
        h= HTMLParser.HTMLParser()
        words_list = []
        for document in passages_before:
            document = h.unescape(document)     # html转移失败的字符 : <>
            # deleteNumAndChar = re.compile(r'[^a-zA-Z0-9]+', re.S)
            # document = re.sub(deleteNumAndChar, " ", document)  # 去除文本中的特殊字符和数字
            # word_list = []
            # for word in document.lower().split():
            #     if word in self.stop_words:
            #         continue
            #     else:
            #         #word = s.stem(word) #nltk 词干转化
            #         word_list.append(word)
            # words_list.append(word_list)
            texts_tokenized = [word.lower() for word in nltk.tokenize.word_tokenize(document.decode('utf-8'))] 
            texts_filtered_stopwords = [word for word in texts_tokenized if not word in stopwords.words('english')] 
            texts_filtered = [word for word in texts_filtered_stopwords if not word in self.english_punctuations] 
            words_list.append(texts_filtered)
        # print words_list
        print "==== tokenization complete ===="
        return words_list
    
    def build_dictionary(self, passages_after):
        print "==== build dictionary from tokenized text ... ===="
        self.dictionary = corpora.Dictionary(passages_after)
        print "====  dictionary complete ===="
        return self.dictionary
    
    def build_tfidfModel(self, passages_after):
        print "==== build tfidfmodel for corpus from tokenized text ... ===="
        corpus = [self.dictionary.doc2bow(passage) for passage in passages_after]
        # print corpus
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        # for doc in corpus_tfidf:
        #     print "doc in corpus tfidf:=====>",doc
        print "==== tfidf model complete ===="
        return corpus_tfidf
    def process_input(self, input):  # 映射到词袋
        query_bow = self.dictionary.doc2bow(input.lower().split())
        print query_bow
        return query_bow

if __name__ == '__main__':
    print "processor"
    processor = Processor()
    # vectorizer = TfidfVectorizer(min_df=1, stop_words='english')    # 出现频率小于min_df的词语都会被丢弃 并加入停用词过滤

    # input_search = topic.getTestRaw()
