# -*- coding: utf-8 -*-
import sys
from utils.topicmodel import TopicModel
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
import json


model = TopicModel()
# model.load_to_cache(model.get_libs())
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

        model.load_to_cache([request.GET['lib']])
        result_list = model.find_cache(request.GET['q'],request.GET['lib'])
        response_data['result'] = result_list 
    else:
        message = '你提交了空表单'
    
    return HttpResponse(json.dumps(response_data), content_type="application/json")