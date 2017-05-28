# -*- coding: utf-8 -*-
import sys
from utils.topicmodel import TopicModel
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
import json


model = TopicModel()
print settings.BASE_DIR

 
# 表单
def search_form(request):
    return render_to_response('search_form.html')
 
# 接收请求数据
def search(request):  
    request.encoding='utf-8'
    print model.show_topics("hibernate")
    
    if 'q' in request.GET:
        message = '你搜索的内容为: ' + request.GET['q']
        result_list = model.find(request.GET['q'],request.GET['lib'])
    else:
        message = '你提交了空表单'
    response_data = {}  
    response_data['result'] = result_list 
    return HttpResponse(json.dumps(response_data), content_type="application/json")