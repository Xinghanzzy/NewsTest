# -*- coding: UTF-8 -*- 。
import urllib
import urllib2
import re
import time
import os
import sys
import MySQLdb

conn = MySQLdb.connect(
        host = '127.0.0.1',
        port = 3309,            #Dante 3306  Lab 3309
        user = 'root',
        passwd = '123456',
        db = 'news',
        )
cur = conn.cursor()


#处理页面标签类
class Tool:

    #去除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    #把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    #把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    #把highlight段落开头
    replacePara2 = re.compile('<li class="el__storyhighlights__item el__storyhighlights--normal">')   
    #把body段落开头
    replacePara3 = re.compile('<div class="zn-body__paragraph">')  
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    removeElse = re.compile('">')
    #将其余标签剔除
    removeExtraTag = re.compile('<.*?>')
    #将注释剔除/\*.*?\*/
    removeComments = re.compile('/\*\*/([\s\S]*?)/\*\*/')
    #将空行剔除
    removeBlockline = re.compile('\s\n\s?\n\s?\n')
    #将articleBody剔除
    removeArticleBody = re.compile('articleBody">')
    #{"
    removeElse = re.compile('{"(.*?)"}')
    #script
    removeScript = re.compile('<script(.*?)</script>')
    
    #去除headline
    replaceHeadline = re.compile('","headline":"')  
    #thumbnail 1
    removeThumbnail_1 = re.compile('"thumbnail":"')  
    #thumbnail 2
    removeThumbnail_2 = re.compile('","thumbnail"":"')  
    #medium
    removeMedium = re.compile('data-src-medium="')  
    #large 
    removeLarge = re.compile('" data-src-large="')  
    #将双引号剔除
    removeQuoMark = re.compile('"')
    
    #标题
    removeTitleElse = re.compile('[/|\:*?"<>|]')

    
    def replace(self,x):
        x = re.sub(self.replaceHeadline,"  ||||  ",x)
        x = re.sub(self.removeElse,"",x)
        x = re.sub(self.removeThumbnail_1,"",x)
        x = re.sub(self.removeThumbnail_2,"",x)
        x = re.sub(self.removeMedium,"",x)
        x = re.sub(self.removeLarge,"",x)
        x = re.sub(self.removeQuoMark,"",x)
        #strip()将前后多余内容删除
        return x.strip()

    def replaceBody(self,x):
        x = re.sub(self.replacePara2,"  ||||  ",x)
        x = re.sub(self.replacePara3,"  ||||  ",x)
        x = re.sub(self.removeScript,"",x)
        x = re.sub(self.replaceHeadline,"",x)
        x = re.sub(self.removeElse,"",x)
        
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"",x)
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replacePara,"  ||||  ",x)
        x = re.sub(self.replaceBR,"",x)
        x = re.sub(self.removeExtraTag,"",x)
        x = re.sub(self.removeElse,"",x)
        x = re.sub(self.removeComments,"",x)
        x = re.sub(self.removeBlockline,"",x)
        x = re.sub(self.removeArticleBody,"",x)
        
        #strip()将前后多余内容删除
        return x.strip()
        
    def replaceTitle(self,x):
        x = re.sub(self.removeTitleElse,"",x)
        return x.strip()

class CNN:
    def __init__(self, baseUrl):
        self.baseURL = baseUrl
        self.tool = Tool()
        #全局file变量，文件写入操作对象
        self.file = None
        self.newsURL = None
        self.time = time.strftime('%Y-%m-%d %H-%M-%S',time.localtime(time.time()))

    def getPage(self):
        try:
            url = self.baseURL + self.newsURL
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            print "response OK"
            return response.read().decode('utf-8')
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print "连接CNN,错误原因", e.reason # u''会报错 why
                return None


    def getNewsBody(self):
        page = self.getPage()
        #获取新闻正文 
        pattern = re.compile('articleBody(.*?)<p class="zn-body__paragraph zn-body__footer">', re.S)
        result = re.findall(pattern, page)    
        contents5 = []        
        for item in result:            
            #将文本进行去除标签处理，同时在前后加入换行符
            content = self.tool.replaceBody(item)+"\n"
            contents5.append(content.encode('utf-8'))     
        return contents5


    def getPicture(self):
        #从url里面寻找新闻缩略图
        page = self.getPage()
        pattern = re.compile('data-src-medium="(.*?)" data-src-large="', re.S)
        result = re.findall(pattern, page)
        contents = []
        count = 1
        for item in result:
            if count > 4 :
                break
            #print   "The Picture url is :  " + self.tool.replace(item)
            #将图片进行去除标签处理，同时在前后加入换行符
            content = self.tool.replace(item)
            if len(content) < 10 :
                continue
            contents.append(content.encode('utf-8'))
            count += 1
        return contents	
        
        
    def saveImg(self,contents,fileName):
        num = 1
        for imageURL in contents:
            if num > 5 :
                break
            #print "imageURL:" + imageURL
            u = urllib.urlopen(imageURL)
            data = u.read()
            f = open(fileName + "\\" + str(num) + ".jpg", 'wb')
            num = num + 1
            f.write(data)
            f.close()

    def start(self):
        try:
            print "CNN ReadNews "
            count = cur.execute('select * from news where news_Text is  NULL and news_From="CNN"')
            print  count
            contents = cur.fetchmany(count)
            #contents = CNN.readData()
            for item,countitem in zip(contents,range(1,50)):
                #URL
                print countitem
                self.newsURL = item[1]
                start = time.clock()
                contentsText = self.getNewsBody()
                if contentsText == [] :
                    contentsText = ['articleBody is None']
                end = time.clock()
                print('getNewsBody Running time: %s Seconds'%(end-start))
                #保存图片
                start = time.clock()
                contentsPic = self.getPicture()
                # 空正文错误处理

                if contentsPic == []:
                    contentsPic = ['Picture is None']
                pic = ""
                for itemPic in contentsPic:
                    pic = pic + str(itemPic) + " "
                end = time.clock()
                print('saveImg Running time: %s Seconds'%(end-start))
                cur.execute("update news set news_Text=%s,news_Img=%s where news_URL = %s ;",
                        (contentsText[0], str(pic), self.newsURL))
                conn.commit()
        #出现写入异常
        except IOError,e:
            print "写入异常，原因" + e.message
        finally:
            print "Save in DB is finish"
            

a = time.clock()
baseURL = 'http://edition.cnn.com/'
CNN = CNN(baseURL)
CNN.start()
b = time.clock()
print('All Running time: %s Seconds'%(b-a))