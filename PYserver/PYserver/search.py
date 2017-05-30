# -*- coding: utf-8 -*-
import sys
from utils.indexSearcher import indexSearcher
from utils.cluster import CosineSim
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
import json


indexSearcher = indexSearcher()
liblist = indexSearcher.get_libs()
# indexSearcher.load_index_cache(liblist)
print "index loaded"
cos = CosineSim()
# cos.load_vector_cache(liblist)
print "vector loaded"
print settings.BASE_DIR

 
# 表单
def search_form(request):
    return render_to_response('search_form.html')
 
# 接收请求数据
def search(request):  
    request.encoding='utf-8'
    # print model.show_topics("hibernate")
    response_data = {}  
    if 'q' in request.GET:
        message = '你搜索的内容为: ' + request.GET['q']
        print "start searching"
        indexSearcher.load_index_cache([request.GET['lib']])
        cos.load_vector_cache([request.GET['lib']])
        result_list = indexSearcher.perform_query(request.GET['q'],request.GET['lib'],cos)
        response_data['sof'] = result_list 
    else:
        message = '你提交了空表单'
    
    return HttpResponse(json.dumps(response_data), content_type="application/json")