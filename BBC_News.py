# -*- coding: UTF-8 -*- 
#BBC 热点新闻获取
#保存如数据库
#取消缩略图保存
#datetime 标签可以直接提取到时间
#Video 标签 处理视频类
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
    #去除第一个时间
    removeTime = re.compile('<span aria-hidden="true" class="qa-status-date-output">(.*?)</span>')
    #
    replaceURL = re.compile('href="(.*?)">')
    #去除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    #把换行的标签换为\n 无用
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    #把段落开头换为\n加空两格
    replacePara = re.compile('<p .*?>')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
	#将url后面的赘余去掉
    removeElse = re.compile('">')
	#将其余标签剔除
    removeExtraTag = re.compile('<.*?>')
	#将Video剔除
    removeVideo = re.compile('Video')
	#将&#x27;装换为'
    replaceFen = re.compile('&#x27;')
	#剔除width标签
    removeWidth = re.compile('{width}')
    #剔除后面赘余
    removeSrcL = re.compile('.jpg"([\s\S]*)')
    
    def replace(self,x):
        x = re.sub(self.replaceURL,x+"\n",x)
        x = re.sub(self.removeTime,"\n",x)
        x = re.sub(self.removeVideo,"",x)
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"",x)
        x = re.sub(self.replaceTD,"",x)
        x = re.sub(self.replacePara,"\n",x)
        x = re.sub(self.replaceBR,"",x)
        x = re.sub(self.removeExtraTag,"",x)
        x = re.sub(self.removeElse,"\n",x)
        x = re.sub(self.replaceFen,'\"',x)
        #strip()将前后多余内容删除
        return x.strip()

    def replacePic(self,x):
        x = re.sub(self.removeWidth,"320",x)
        #strip()将前后多余内容删除
        return x.strip()

class BBC:
    def __init__(self, baseUrl):
        print "__init__"
        self.baseURL = baseUrl
        self.tool = Tool()
        #全局file变量，文件写入操作对象
        self.file = None
        self.time = time.strftime('%Y-%m-%d %H-%M-%S',time.localtime(time.time()))

    def getPage(self, pageNum):
        try:
            url = self.baseURL
            request = urllib2.Request(url)
            print "request ok"
            response = urllib2.urlopen(request)
            print "response ok"
            return response.read().decode('utf-8')
        except urllib2.URLError, e:
            print "error"
            if hasattr(e, "reason"):
                print "连接BBC,错误原因", e.reason # u''会报错 why
                return None


    def getPostData(self):
        page = self.getPage(1)
        print  type(page)
        pattern = re.compile('<a class="gs-c-promo-heading nw-o-link-split__anchor gs-o-faux-block-link__overlay-link gel-pica-bold" href="(.*?)</span></time></span>', re.S)
        result = re.findall(pattern, page)
        contents = []
        count = 1
        for item in result:
            #print   "The News url is :  " + self.tool.replace(item)
			#将文本进行去除标签处理，同时在前后加入换行符
            content = str(count) + "\n" + self.tool.replace(item)+"\n"+"\n"               
            count = count + 1                  
            contents.append(content.encode('utf-8'))
        return contents
			
			
    def getPicture(self):
        #从url里面寻找新闻缩略图
        page = self.getPage(1)
        pattern = re.compile('data-src="(.*?)" data-widths=', re.S)
        result = re.findall(pattern, page)
        contents = []
        for item in result:
            #print   "The Picture url is :  " + self.tool.replacePic(item)
			#将文本进行去除标签处理，同时在前后加入换行符
            content = "\n" + self.tool.replacePic(item) + "\n"
            contents.append(content.encode('utf-8'))
        return contents
 		
    def saveDataToFile(self,contents):
        #向文件写入每一楼的信息
        for item in contents:
            self.file.write(item)       
        
    def saveImg(self,contents,fileName):
        num = 1
        for imageURL in contents:
            u = urllib.urlopen(imageURL)
            data = u.read()
            f = open(fileName + "\\" + str(num) + ".jpg", 'wb')
            num = num + 1
            f.write(data)
            f.close()        
    
    def saveAllToDb(self, contentsfile , contentsimg):
        for (contentfile ,contentimg) in zip(contentsfile , contentsimg):
            dbTemp =  str(contentfile).split('\n',5)            
            ISOTIMEFORMAT='%Y-%m-%d %X'
            cur.execute("insert ignore into news(news_ID,news_URL,news_Title,news_Data,news_From,news_MiniImg,news_Top_n,news_InTime) values('%d','%s','%s','%s','%s','%s','%s','%s') "   % (0,str(dbTemp[1]),str(dbTemp[2]),str(dbTemp[4]),"BBC",str(contentimg).split('\n')[1],str(dbTemp[0]),time.strftime( ISOTIMEFORMAT, time.localtime() )))
            conn.commit()
	
    def start(self):
        try:
            print "BBC News "
            contents = BBC.getPostData()
            print "getPostData OK"
            #self.saveDataToFile(contents)
            contentsPic = BBC.getPicture()

            #空正文错误处理
            if contents == [] :
                contents = ['URL is None']
            if contentsPic == [] :
                contentsPic = ['Pic is None']

            self.saveAllToDb(contents,contentsPic)
            mkpath = os.path.abspath('.') + "\\News\\BBC_Mini"
            #无文件夹则创建
            if os.path.isdir(mkpath):
                pass
            else:
                os.mkdir(mkpath)
            #self.saveImg(contentsPic ,  mkpath )
        #出现写入异常
        except IOError,e:
            print "写入异常，原因" + e.message

start = time.clock()
baseURL = 'http://www.bbc.com/news'
BBC = BBC(baseURL)
BBC.start()
cur.close()
conn.close()
end = time.clock()
print('Running time: %s Seconds'%(end-start))