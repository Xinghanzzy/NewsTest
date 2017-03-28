# -*- coding: UTF-8 -*- 。
import urllib
import urllib2
import re
import time
import os
import sys
import MySQLdb
import hashlib
import json
import random
#http://api.fanyi.baidu.com/api/trans/product/apidoc
#"from":"zh","to":"en",

conn = MySQLdb.connect(
        host = '127.0.0.1',
        port = 3309,            #Dante 3306  Lab 3309
        user = 'root',
        passwd = '123456',
        db = 'news',
        )
cur = conn.cursor()


import urllib
import urllib2

count = cur.execute('select * from news where news_Url = "/2017/03/27/motorsport/ferrari-f1-hamilton-vettel-australia-battle/index.html"')
info = cur.fetchmany(count)
print info
list = str(info[0][5]).split("  ||||  ")
print info[0][5]
print len(list)
sys.exit(0)
for item,counitem in zip(list,range(1,500)):
    print counitem
    print item
    test_data = {"tgt_text":"apple","src_text":"Apple"}
    test_data['src_text'] = str(item)
    test_data_urlencode = urllib.urlencode(test_data)
    requrl = "http://218.75.34.138:8080/NiuTransServer/translation?from=en&to=zh"
    req = urllib2.Request(url = requrl,data =test_data_urlencode)    
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print res






# import requests
# import json
#
#
# # POS请求：直接向服务器发送数据
# # get请求：从服务器获取数据
# # 有道，向服务器发送数据，再获取数据
# def get_translate_data(word=None):
#     url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'
#     payload = {'type': 'AUTO', 'i': word, 'doctype': 'json', 'xmlVersion': 1.8,
#                'keyfrom': 'fanyi.web', 'ue': 'UTF-8', 'action': 'FY_BY_CLICKBUTTON',
#                'typoResult': 'true'
#                }  # 建立数据字典
#     response = requests.post(url, data=payload)
#     # print response.text #返回字符串
#
#     content = json.loads(response.text)  # 将字符串转换为json数据
#     print content  # 直接打印，又编码问题，在http://jsoneditoronline.org/中无法查看
#     print json.dumps(content, encoding='utf-8', ensure_ascii=False)  # json，有方法.dumps 实现转码
#
#     print content['translateResult'][0][0]['tgt']
#
#
# if __name__ == '__main__':
#     get_translate_data('苹果')