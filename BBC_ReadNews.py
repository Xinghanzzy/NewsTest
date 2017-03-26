# -*- coding: UTF-8 -*- ��
import urllib
import urllib2
import re
import time
import os
import MySQLdb


conn = MySQLdb.connect(
        host = '127.0.0.1',
        port = 3306,
        user = 'root',
        passwd = '123456',
        db = 'news',
        )
cur = conn.cursor()

#����ҳ���ǩ��
class Tool:
    #ȥ��img��ǩ,7λ���ո�
    removeImg = re.compile('<img.*?>| {7}|')
    #ȥ��img��ǩ2
    removeImg2 = re.compile('<figcaption([\s\S]*?)</figcaption>')
    #ȥ��ͼƬ��Դ
    removeFrom = re.compile('<span class="story-image-copyright">(.*?)</span>')
    #ɾ�������ӱ�ǩ
    removeAddr = re.compile('<a.*?>|</a>')    
    #������Ʊ�<td>�滻Ϊ\t
    replaceTD= re.compile('<td>')
    #�Ѷ��俪ͷ��Ϊ\n�ӿ�����
    replacePara = re.compile('<p.*?>')
    #�����з���˫���з��滻Ϊ\n
    replaceBR = re.compile('<br><br>|<br>')
    removeElse = re.compile('">')
	#�������ǩ�޳�
    removeExtraTag = re.compile('<[\s\S]*?>')
    #��ע���޳�/\*.*?\*/
    removeComments = re.compile('/\*\*/([\s\S]*?)/\*\*/')
	#�������޳�
    removeBlockline = re.compile('\n')
    
    #ͼƬ
    #�޳�span
    removespan = re.compile('<span.*?>|</span>')
    #�޳�ͼƬ��ʶ��
    removeIc = re.compile('Image copyright')
    #�޳�ǰ��׸��
    removeSrcF = re.compile('(.*?)src="')
    #�޳�����׸��
    removeSrcL = re.compile('.jpg"([\s\S]*)')
    #�滻ͼƬ�ߴ��С
    replaceSize = re.compile('/320/')
    
    #����
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
        #strip()��ǰ���������ɾ��
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
		#ȫ��file�������ļ�д���������
        self.file = None
        self.time = time.strftime('%Y-%m-%d %H-%M-%S',time.localtime(time.time()))

    def getPage(self):
        try:
            url = self.baseURL+self.newsURL
            request = urllib2.Request(url)
            print "request ok"
            response = urllib2.urlopen(request)
            print "response ok"
            return response.read().decode('utf-8')
        except urllib2.URLError, e: 
            if hasattr(e, "reason"):
                print "����BBC,����ԭ��", e.reason # u''�ᱨ�� why
                return None

    def getPostData(self):
        #��url����Ѱ������
        page = self.getPage()
        pattern = re.compile('property="articleBody">(.*?) <div class="share share--lightweight', re.S)
        result = re.findall(pattern, page)
        contents = []
        for item in result:
			#���ı�����ȥ����ǩ����ͬʱ��ǰ����뻻�з�
            content = self.tool.replace(item)
            contents.append(content.encode('utf-8'))
        return contents	

    def getPostData2(self):
        #��url����Ѱ������ �������Ƶ����ҳ û��articalbody��ǩ
        page = self.getPage()
        pattern = re.compile('property="articleBody">(.*?) <div class="share share--lightweight', re.S)
        result = re.findall(pattern, page)
        contents = []
        for item in result:
			#���ı�����ȥ����ǩ����ͬʱ��ǰ����뻻�з�
            content = self.tool.replace(item)
            contents.append(content.encode('utf-8'))
        return contents	 

    def getPicture(self):
        #��url����Ѱ������ͼƬ
        page = self.getPage()
        pattern = re.compile('<span class="image-and-copyright-container">(.*?) <span class="off-screen">Image copy', re.S)
        result = re.findall(pattern, page)
        contents = []
        for item in result:
            #print   "The Picture url is :  " + self.tool.replacePic(item)
			#���ı�����ȥ����ǩ����ͬʱ��ǰ����뻻�з�
            content = self.tool.replacePic(item)
            contents.append(content.encode('utf-8'))
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
        #���ļ�д��ÿһ¥����Ϣ
        self.file.write("URL: " + self.baseURL + self.newsURL)
        self.file.write("Title: " + self.Title)
        self.file.write("SubTitle: " + self.SubTitle)
        for item in contents:
            self.file.write(item)
			
    def readData(self):
        #��ȡbbsnews��������� ���ֳ���url ���� ������
        try:
            count=cur.execute('select * from news where news_Text is  NULL')
            print  count
            info = cur.fetchmany(count)         
            for item in info:    
                self.Count = str(item[0])                    
                self.newsURL = item[1]
                self.Title = item[3]
                self.SubTitle = "2333"
                self.Time = item[2]
                print"\n--------------------------------------------------\n"
                print "end: " + self.Count + self.newsURL + self.Title + self.SubTitle+self.Time                    
                mkpath = os.path.abspath('.') + "\\News\\BBC\\" + self.tool.replaceTitle(self.Title)
                #����������Ѿ�����������
                # if os.path.isdir(mkpath):
                    # continue                        
                # else:
                    # os.mkdir(mkpath)  
                        
                #����body
                start = time.clock()
                contentsText = self.getPostData()
                #print contentsText
                #�����Ĵ�����
                if contentsText == [] :
                    contentsText = ['articleBody is None']
                #print contentsText
                end = time.clock()
                print('getPostData Running time: %s Seconds'%(end-start))
                
                #д������
                #start = time.clock()
                #self.file = open( mkpath + "\\body"+ ".txt","w+" )
                #self.writeData(contentsText)
                #self.file.close()
                #end = time.clock()
                #print('self.writeData Running time: %s Seconds'%(end-start))                    
                
                #����ͼƬ
                start = time.clock()
                contentsPic = self.getPicture()               
                #�����Ĵ�����
                if contentsPic == [] :
                    contentsPic = ['Picture is None']
                pic = ""
                for itemPic in contentsPic:
                    pic = pic + str(itemPic) + " "
                print pic
                #self.saveImg(contentsPic,mkpath) #����ͼƬ��д   
                cur.execute("update news set news_Text=%s,news_Img=%s where news_URL = %s ;",(contentsText[0] ,str(pic) , self.newsURL))
                conn.commit()
                end = time.clock()
                print('self.saveImg Running time: %s Seconds'%(end-start))         

                
                        
        finally:
            pass
                
	
    def start(self):
        try:
            print "Read BBC News "
            self.readData()
            
        #����д���쳣
        except IOError,e:
            print "д���쳣��ԭ��" + e.message
        finally:
            print "д���������"

a = time.clock()
baseURL = 'http://www.bbc.com'
BdTb = BdTb(baseURL)
BdTb.start()
cur.close()
conn.close()
b = time.clock()
print '%s'%(b-a)