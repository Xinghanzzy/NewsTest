# -*- coding: UTF-8 -*- 。
import urllib
import urllib2
import re
import time
import os
import MySQLdb


conn = MySQLdb.connect(
        host = '127.0.0.1',
        port=3309,  # Dante 3306  Lab 3309
        user = 'root',
        passwd = '123456',
        db = 'news',
        )
cur = conn.cursor()

#处理页面标签类
class Tool:
    #去除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    #去除img标签2
    removeImg2 = re.compile('<figcaption([\s\S]*?)</figcaption>')
    #去掉图片来源
    removeFrom = re.compile('<span class="story-image-copyright">(.*?)</span>')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')    
    #将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    #把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    removeElse = re.compile('">')
	#将其余标签剔除
    removeExtraTag = re.compile('<[\s\S]*?>')
    #将注释剔除/\*.*?\*/
    removeComments = re.compile('/\*\*/([\s\S]*?)/\*\*/')
	#将空行剔除
    removeBlockline = re.compile('\n')
    #图片
    #剔除span
    removespan = re.compile('<span.*?>|</span>')
    #剔除图片标识字
    removeIc = re.compile('Image copyright')
    #剔除前面赘余
    removeSrcF = re.compile('(.*?)src="')
    #剔除后面赘余
    removeSrcL = re.compile('.jpg"([\s\S]*)')
    #替换图片尺寸大小
    replaceSize = re.compile('/320/')
    #标题
    removeTitleElse = re.compile('[/|\:*?"<>|]')
    
    def replace(self,x):
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeImg2,"",x)
        x = re.sub(self.removeFrom,"",x)
        x = re.sub(self.removeAddr,"",x)        
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replacePara,"  ||||  ",x)
        x = re.sub(self.replaceBR,"",x)
        x = re.sub(self.removeExtraTag,"",x)
        #x = re.sub(self.removeElse,"",x)
        x = re.sub(self.removeComments,"",x)
        x = re.sub(self.removeBlockline,"",x)
        #strip()将前后多余内容删除
        return x.strip()
    
    def replacePic(self,x):
        x = re.sub(self.removeSrcF,"",x)
        x = re.sub(self.removeSrcL,".jpg",x)
        x = re.sub(self.replaceSize,"/1024/",x)
        return x.strip()
        
    def replaceTitle(self,x):
        x = re.sub(self.removeTitleElse,"",x)
        return x.strip()


class BdTb:
    def __init__(self, baseUrl):
        self.baseURL = baseUrl
        self.tool = Tool()
        self.Count = 0
        self.newsURL = None
        self.Title = None
        self.SubTitle = None
        self.Time = None
        self.time = time.strftime('%Y-%m-%d %H-%M-%S',time.localtime(time.time()))

    def getPage(self):
        try:
            url = self.baseURL+self.newsURL
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            print "response ok"
            return response.read().decode('utf-8')
        except urllib2.URLError, e: 
            if hasattr(e, "reason"):
                print "连接BBC,错误原因", e.reason # u''会报错 why
                return None

    def getPostData(self):
        #从url里面寻找正文
        page = self.getPage()
        pattern = re.compile('property="articleBody">(.*?) <div class="share share--lightweight', re.S)
        result = re.findall(pattern, page)
        contents = []
        for item in result:
			#将文本进行去除标签处理，同时在前后加入换行符
            content = self.tool.replace(item)
            contents.append(content.encode('utf-8'))
        return contents	

    def getPostData2(self):
        #从url里面寻找正文 针对于视频类网页 没有articalbody标签
        page = self.getPage()
        pattern = re.compile('property="articleBody">(.*?) <div class="share share--lightweight', re.S)
        result = re.findall(pattern, page)
        contents = []
        for item in result:
			#将文本进行去除标签处理，同时在前后加入换行符
            content = self.tool.replace(item)
            contents.append(content.encode('utf-8'))
        return contents	 

    def getPicture(self):
        #从url里面寻找新闻图片
        page = self.getPage()
        pattern = re.compile('<span class="image-and-copyright-container">(.*?) <span class="off-screen">Image copy', re.S)
        result = re.findall(pattern, page)
        contents = []
        for item in result:
            #print   "The Picture url is :  " + self.tool.replacePic(item)
			#将文本进行去除标签处理，同时在前后加入换行符
            content = self.tool.replacePic(item)
            contents.append(content.encode('utf-8'))
        return contents

    def readData(self):
        try:
            count=cur.execute('select * from news where news_Text is  NULL and news_From="BBC"')
            print  count
            info = cur.fetchmany(count)         
            for item,countitem in zip(info,range(1,100)):
                self.Count = str(item[0])                    
                self.newsURL = item[1]
                self.Title = item[3]
                self.SubTitle = "2333"
                self.Time = item[2]
                print"--------------------------------------------------"
                print countitem
                #保存body
                start = time.clock()
                contentsText = self.getPostData()
                #空正文错误处理
                if contentsText == [] :
                    contentsText = ['articleBody is None']
                end = time.clock()
                print('getPostData Running time: %s Seconds'%(end-start))

                start = time.clock()
                contentsPic = self.getPicture()               
                #空正文错误处理
                if contentsPic == [] :
                    contentsPic = ['Picture is None']
                pic = ""
                for itemPic in contentsPic:
                    pic = pic + str(itemPic) + " "
                #self.saveImg(contentsPic,mkpath) #保存图片另写   
                cur.execute("update news set news_Text=%s,news_Img=%s where news_URL = %s ;",(contentsText[0] ,str(pic) , self.newsURL))
                conn.commit()
        finally:
            pass
                
	
    def start(self):
        try:
            print "Read BBC News "
            self.readData()
            
        #出现写入异常
        except IOError,e:
            print "写入异常，原因" + e.message
        finally:
            print "写入任务完成"

a = time.clock()
baseURL = 'http://www.bbc.com'
BdTb = BdTb(baseURL)
BdTb.start()
cur.close()
conn.close()
b = time.clock()
print '%s'%(b-a)