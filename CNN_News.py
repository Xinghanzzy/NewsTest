# -*- coding: UTF-8 -*- ��
import urllib
import urllib2
import re
import time
import os



#����ҳ���ǩ��
class Tool:
    #ȥ��headline
    replaceHeadline = re.compile('","headline":"')  
    #thumbnail 1
    removeThumbnail_1 = re.compile('"thumbnail":"')  
    #thumbnail 2
    removeThumbnail_2 = re.compile('","thumbnail"":"')  
	#��˫�����޳�
    removeQuoMark = re.compile('"')
    #�������޳� 1
    removeStrong_1 = re.compile('\\u003cstrong>')
    #�������޳� 2
    removeStrong_2 = re.compile('\\u003c/strong>')
    #��б���޳� ??
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
        #strip()��ǰ���������ɾ��
        return x.strip()

    def replacePic(self,x):
        x = re.sub(self.removeWidth,"800",x)
        #strip()��ǰ���������ɾ��
        return x.strip()
        
    def replaceTime(self , x):
        x = re.match(self.replacetime, x)
        print x.group()
        a = re.sub(self.replacetime2,"-",str(x.group()))
        b = a.strip()
        return b[1:]

class CNN:
    def __init__(self, baseUrl):
        self.baseURL = baseUrl
        self.tool = Tool()
		#ȫ��file�������ļ�д���������
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
                print "����CNN,����ԭ��", e.reason # u''�ᱨ�� why
                return None


    def getPostData(self):
        page = self.getPage(1)
        pattern = re.compile('"uri":"(.*?)","thumbnail"', re.S)
        result = re.findall(pattern, page)
        contents = []
        count = 1 #��������20��
        for item in result:
            if count > 19 :
                break
            print   "The News url is :  " + self.tool.replace(item)
			#���ı�����ȥ����ǩ����ͬʱ��ǰ����뻻�з�
            content = str(count) + "\n" + self.tool.replace(item) + "\n" + self.tool.replaceTime(self.tool.replace(item)) + "\n" + "\n"
            print str(content)
            if len(content) < 10 :
                continue            
            contents.append(content.encode('utf-8'))
            count += 1
        return contents
			
			
    def getPicture(self):
        #��url����Ѱ����������ͼ
        page = self.getPage(1)
        pattern = re.compile('"thumbnail":"(.*?)"', re.S)
        result = re.findall(pattern, page)
        contents = []
        count = 1
        for item in result:
            if count > 19 :
                break
            print   "The Picture url is :  " + self.tool.replace(item)
			#��ͼƬ����ȥ����ǩ����ͬʱ��ǰ����뻻�з� 
            content = "\n" + self.tool.replace(item) + "\n"
            if len(content) < 10 :
                continue
            contents.append(content.encode('utf-8'))
            count += 1
        return contents	
        return "0.0"
        
        
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
        for item in contents:
            self.file.write(item)
	
    def start(self):
        self.file = open("CNN News " + ".txt","w+")
        try:
            print "CNN News "
            contents = CNN.getPostData()
            self.writeData(contents)
            contents = CNN.getPicture()
            mkpath = os.path.abspath('.') + "\\News\\CNN_Mini"
            if os.path.isdir(mkpath):
                pass
            else:
                os.mkdir(mkpath)
            self.saveImg(contents ,  mkpath )
        #����д���쳣
        except IOError,e:
            print "д���쳣��ԭ��" + e.message
        finally:
            print "д���������"
            self.file.close()


baseURL = 'http://edition.cnn.com/'
CNN = CNN(baseURL)
CNN.start()