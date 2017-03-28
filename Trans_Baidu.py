# -*- coding: UTF-8 -*- 。
import urllib
import urllib2
import re
import time
import os
import MySQLdb
import hashlib
import json
import random
#http://api.fanyi.baidu.com/api/trans/product/apidoc

class Baidu_Translation:
    def __init__(self):
        self._q = ''        #需要翻译的语句
        self._from = ''
        self._to = ''
        self._appid = 0
        self._key = ''
        self._salt = 0
        self._sign = ''
        self._dst = ''
        self._enable = True

    def GetResult(self):
        self._q.encode('utf8')
        m = str(Trans._appid) + Trans._q + str(Trans._salt) + Trans._key
        m_MD5 = hashlib.md5(m)
        Trans._sign = m_MD5.hexdigest()
        Url_1 = 'http://api.fanyi.baidu.com/api/trans/vip/translate?'
        Url_2 = 'q=' + self._q + '&from=' + self._from + '&to=' + self._to + '&appid=' + str(
            Trans._appid) + '&salt=' + str(Trans._salt) + '&sign=' + self._sign
        Url = Url_1 + Url_2
        PostUrl = Url.decode()
        TransRequest = urllib2.Request(PostUrl)
        TransResponse = urllib2.urlopen(TransRequest)
        TransResult = TransResponse.read()
        data = json.loads(TransResult)
        if 'error_code' in data:
            print 'Crash'
            print 'error:', data['error_code']
            return data['error_msg']
        else:
            self._dst = data['trans_result'][0]['dst']
            return self._dst

    def ShowResult(self, result):
        print result

    def Welcome(self):
        self._q = 'Welcome to use icedaisy online translation tool'
        self._from = 'auto'
        self._to = 'zh'
        self._appid = 20170328000043598
        self._key = 'o8skojHFnsMc9KFSqcZB'
        self._salt = random.randint(10001, 99999)
        welcome = self.GetResult()
        self.ShowResult(welcome)

    def StartTrans(self):
        while self._enable:
            self._q = raw_input()
            if cmp(self._q, '!quit') == 0:
                self._enable = False
                print 'Thanks for using!'
            _q_len = len(self._q)
            if _q_len < 4096:
                result = self.GetResult()
                self.ShowResult(result)
            else:
                print 'Exceeds the maximum limit of 4096 characters'


# ----------- 程序的入口 -----------
print u"""  
---------------------------------------  
    程序：Dante的在线翻译工具  
    版本：1.0
    作者：icedaisy  
    日期：2017-03-28  
    语言：Python 2.7 
    功能：输入原文后得到翻译结果
    原理：调用百度翻译API
    退出：输入!quit
---------------------------------------  
"""
Trans = Baidu_Translation()
Trans.Welcome()
Trans.StartTrans()