# -*- coding: UTF-8 -*-
#使用 str 类的.replace函数替换 ‘ -> " 比正则好用一些
import urllib
import urllib2
import re
import time
import os
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
    #去除headline
    replaceHeadline = re.compile('","headline":"')  
    #thumbnail 1
    removeThumbnail_1 = re.compile('"thumbnail":"')  
    #thumbnail 2
    removeThumbnail_2 = re.compile('","thumbnail"":"')  
    #将双引号剔除
    removeQuoMark = re.compile('"')
    #将黑体剔除 1
    removeStrong_1 = re.compile('\\u003cstrong>')
    #将黑体剔除 2
    removeStrong_2 = re.compile('\\u003c/strong>')
    #将斜杠剔除 ??
    #removeXie = re.compile('\\\\')
    
    
    
    replacetime = re.compile('^.{11}')
    replacetime2 = re.compile('/')
    
    def replace(self,x):
        x = re.sub(self.replaceHeadline,"\n",x)
        x = re.sub(self.removeThumbnail_1,"",x)
        x = re.sub(self.removeThumbnail_2,"",x)
        x = re.sub(self.removeStrong_1,"",x)
        x = re.sub(self.removeStrong_2,"",x)
        x = re.sub(self.removeQuoMark,"",x)
        x = re.sub(r'\\',"",x)
        #strip()将前后多余内容删除
        return x.strip()

    def replacePic(self,x):
        x = re.sub(self.removeWidth,"800",x)
        #strip()将前后多余内容删除
        return x.strip()
        
    def replaceTime(self , x):
        x = re.match(self.replacetime, x)
        #print x.group()
        a = re.sub(self.replacetime2,"-",str(x.group()))
        b = a.strip()
        return b[1:]

class CNN:
    def __init__(self, baseUrl):
        self.baseURL = baseUrl
        self.tool = Tool()
        #全局file变量，文件写入操作对象
        self.file = None
        self.time = time.strftime('%Y-%m-%d %H-%M-%S',time.localtime(time.time()))

    def getPage(self, pageNum):
        try:
            url = self.baseURL
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            return response.read().decode('utf-8')
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print "连接CNN,错误原因", e.reason # u''会报错 why
                return None


    def getPostData(self):
        page = self.getPage(1)
        pattern = re.compile('"uri":"(.*?)","thumbnail"', re.S)
        result = re.findall(pattern, page)
        #print result
        contents = []
        count = 1 #新闻少于20个
        for item in result:
            if count > 30 :
                break
            #print   "The News url is :  " + self.tool.replace(item)
            #将文本进行去除标签处理，同时在前后加入换行符
            content = str(count) + "\n" + self.tool.replace(item) + "\n" + self.tool.replaceTime(self.tool.replace(item)) + "\n" + "\n"
            #print str(content)
            if len(content) < 10 :
                continue
            if "videos" in content:
                continue
            contents.append(content.encode('utf-8'))
            count += 1
        return contents


    def getPicture(self):
        #从url里面寻找新闻缩略图
        page = self.getPage(1)
        pattern = re.compile('"thumbnail":"(.*?)"', re.S)
        result = re.findall(pattern, page)
        contents = []
        count = 1
        for item in result:
            if count > 30 :
                break
            #print   "The Picture url is :  " + self.tool.replace(item)
            #将图片进行去除标签处理，同时在前后加入换行符
            content = "\n" + self.tool.replace(item) + "\n"
            if len(content) < 10 :
                continue
            contents.append(content.encode('utf-8'))
            count += 1
        return contents
        
        
    def saveImg(self,contents,fileName):
        num = 1
        for imageURL in contents:
            u = urllib.urlopen(imageURL)
            data = u.read()
            f = open(fileName + "\\" + str(num) + ".jpg", 'wb')
            num = num + 1
            f.write(data)
            f.close()
        

    def writeData(self,contents):
        #向文件写入每一楼的信息
        for item in contents:
            self.file.write(item)

    def saveAllToDb(self, contentsfile, contentsimg):
        for (contentfile, contentimg) in zip(contentsfile, contentsimg):
            dbTemp = str(contentfile).split('\n', 5)
            ISOTIMEFORMAT = '%Y-%m-%d %X'
            cur.execute(
                "insert ignore into news(news_ID,news_URL,news_Title,news_Data,news_From,news_MiniImg,news_Top_n,news_InTime) values('%d','%s','%s','%s','%s','%s','%s','%s') "
                % (0, str(dbTemp[1]), str(dbTemp[2].replace('\'','"')), str(dbTemp[3]), "CNN", str(contentimg).split('\n')[1],
                str(dbTemp[0]), time.strftime(ISOTIMEFORMAT, time.localtime())))
            conn.commit()

    def start(self):
        self.file = open("CNN News " + ".txt","w+")
        try:
            print "CNN News "
            contents = CNN.getPostData()
            #self.writeData(contents)
            contentsPic = CNN.getPicture()
            print "Next DB"
            self.saveAllToDb(contents , contentsPic)
            # mkpath = os.path.abspath('.') + "\\News\\CNN_Mini"
            # if os.path.isdir(mkpath):
            #     pass
            # else:
            #     os.mkdir(mkpath)
            #self.saveImg(contentsPic ,  mkpath )
        #出现写入异常
        except IOError,e:
            print "写入异常，原因" + e.message
        finally:
            print "写入任务完成"
            self.file.close()


baseURL = 'http://edition.cnn.com/'
CNN = CNN(baseURL)
CNN.start()
cur.close()
conn.close()