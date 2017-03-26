# -*- coding: UTF-8 -*- ��
import urllib
import urllib2
import re
import time
import os



#����ҳ���ǩ��
class Tool:

    #ȥ��img��ǩ,7λ���ո�
    removeImg = re.compile('<img.*?>| {7}|')
    #ɾ�������ӱ�ǩ
    removeAddr = re.compile('<a.*?>|</a>')
    #�ѻ��еı�ǩ��Ϊ\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #������Ʊ�<td>�滻Ϊ\t
    replaceTD= re.compile('<td>')
    #�Ѷ��俪ͷ��Ϊ\n�ӿ�����
    replacePara = re.compile('<p.*?>')
    #��highlight���俪ͷ
    replacePara2 = re.compile('<li class="el__storyhighlights__item el__storyhighlights--normal">')   
    #��body���俪ͷ
    replacePara3 = re.compile('<div class="zn-body__paragraph">')  
    #�����з���˫���з��滻Ϊ\n
    replaceBR = re.compile('<br><br>|<br>')
    removeElse = re.compile('">')
	#�������ǩ�޳�
    removeExtraTag = re.compile('<.*?>')
    #��ע���޳�/\*.*?\*/
    removeComments = re.compile('/\*\*/([\s\S]*?)/\*\*/')
	#�������޳�
    removeBlockline = re.compile('\s\n\s?\n\s?\n')
    #��articleBody�޳�
    removeArticleBody = re.compile('articleBody">')
    #{"
    removeElse = re.compile('{"(.*?)"}')
    #script
    removeScript = re.compile('<script(.*?)</script>')
    
    #ȥ��headline
    replaceHeadline = re.compile('","headline":"')  
    #thumbnail 1
    removeThumbnail_1 = re.compile('"thumbnail":"')  
    #thumbnail 2
    removeThumbnail_2 = re.compile('","thumbnail"":"')  
    #medium
    removeMedium = re.compile('data-src-medium="')  
    #large 
    removeLarge = re.compile('" data-src-large="')  
	#��˫�����޳�
    removeQuoMark = re.compile('"')
    
    #����
    removeTitleElse = re.compile('[/|\:*?"<>|]')
	
    
    def replace(self,x):
        x = re.sub(self.replaceHeadline,"  ||||  ",x)
        x = re.sub(self.removeElse,"",x)
        x = re.sub(self.removeThumbnail_1,"",x)
        x = re.sub(self.removeThumbnail_2,"",x)
        x = re.sub(self.removeMedium,"",x)
        x = re.sub(self.removeLarge,"",x)
        x = re.sub(self.removeQuoMark,"",x)
        #strip()��ǰ���������ɾ��
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
        
        #strip()��ǰ���������ɾ��
        return x.strip()
        
    def replaceTitle(self,x):
        x = re.sub(self.removeTitleElse,"",x)
        return x.strip()

class CNN:
    def __init__(self, baseUrl):
        self.baseURL = baseUrl
        self.tool = Tool()
		#ȫ��file�������ļ�д���������
        self.file = None
        self.newsURL = None
        self.time = time.strftime('%Y-%m-%d %H-%M-%S',time.localtime(time.time()))

    def getPage(self, pageNum):
        try:
            url = self.baseURL + self.newsURL
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            return response.read().decode('utf-8')
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print "����CNN,����ԭ��", e.reason # u''�ᱨ�� why
                return None


    def getNewsBody(self):
        page = self.getPage(1)
        #��ȡ�������� 
        pattern = re.compile('articleBody(.*?)<p class="zn-body__paragraph zn-body__footer">', re.S)
        result = re.findall(pattern, page)    
        contents5 = []        
        for item in result:            
			#���ı�����ȥ����ǩ����ͬʱ��ǰ����뻻�з�
            content = "\n"+self.tool.replaceBody(item)+"\n"                 
            contents5.append(content.encode('utf-8'))     
        return contents5
			
			
    def getPicture(self):
        #��url����Ѱ����������ͼ
        page = self.getPage(1)
        pattern = re.compile('data-src-medium="(.*?)" data-src-large="', re.S)
        result = re.findall(pattern, page)
        contents = []
        count = 1
        for item in result:
            if count > 4 :
                break
            print   "The Picture url is :  " + self.tool.replace(item)
			#��ͼƬ����ȥ����ǩ����ͬʱ��ǰ����뻻�з� 
            content = "\n" + self.tool.replace(item) + "\n"
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
        
		
    def writeData(self,contents):
        #���ļ�д��ÿһ¥����Ϣ
        for item in contents:
            self.file.write(item)
            
    def readData(self):
        #��ȡbbsnews��������� ���ֳ���url ���� ������
        contents4 = []
        try:
            f = open('CNN News .txt', 'r')
            for line in f.readlines():
                if len(line) != 1:                     
                    contents4.append(line)
                    print "line : " + line
            print "------------------------------\n"             
            return contents4
        except IOError,e:
            print "Read CNN NEWS �쳣" + e.message  
        finally:
            if f:
                f.close()
	
    def start(self):
        try:
            print "CNN ReadNews "
            contents = CNN.readData()                
            count = 1
            for item in contents: 
                #ID
                print str(count) + "   " + item
                if count % 4 == 1 :
                    count = count + 1
                    continue
                #URL
                if count % 4 == 2 :
                    #print "URL : " + item
                    self.newsURL = item
                    count = count + 1
                    continue
                #Title
                if count % 4 == 3 :
                    mkpath = os.path.abspath('.') + "\\News\\CNN\\" + self.tool.replaceTitle(item)
                    print "dir : " + mkpath
                    #����������Ѿ�����������
                    if os.path.isdir(mkpath):
                        count = count + 1
                        continue                        
                    else:
                        os.mkdir(mkpath) 
                    #��������
                    start = time.clock()
                    contents2 = self.getNewsBody()
                    self.file = open( mkpath + "\\body"+ ".txt","w+" )
                    self.writeData(contents2)                    
                    self.file.close()
                    end = time.clock()
                    print('getNewsBody Running time: %s Seconds'%(end-start))
                    
                    #����ͼƬ
                    start = time.clock()
                    contents3 = self.getPicture()                    
                    self.saveImg(contents3,mkpath) 
                    end = time.clock()
                    print('saveImg Running time: %s Seconds'%(end-start))
                    
                    count = count + 1
                    continue                    
                if count % 4 == 0 :
                    count = count + 1
                    continue
            
            
        #����д���쳣
        except IOError,e:
            print "д���쳣��ԭ��" + e.message
        finally:
            print "д���������"
            

a = time.clock()
baseURL = 'http://edition.cnn.com/'
CNN = CNN(baseURL)
CNN.start()
b = time.clock()
print('All Running time: %s Seconds'%(b-a))