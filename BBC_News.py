# -*- coding: UTF-8 -*- 
#BBC �ȵ����Ż�ȡ
#���������ݿ�
#ȡ������ͼ����
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
    #ȥ����һ��ʱ��
    removeTime = re.compile('<span aria-hidden="true" class="qa-status-date-output">(.*?)</span>')
    #
    replaceURL = re.compile('href="(.*?)">')
    #ȥ��img��ǩ,7λ���ո�
    removeImg = re.compile('<img.*?>| {7}|')
    #ɾ�������ӱ�ǩ
    removeAddr = re.compile('<a.*?>|</a>')
    #�ѻ��еı�ǩ��Ϊ\n ����
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #������Ʊ�<td>�滻Ϊ\t
    replaceTD= re.compile('<td>')
    #�Ѷ��俪ͷ��Ϊ\n�ӿ�����
    replacePara = re.compile('<p .*?>')
    #�����з���˫���з��滻Ϊ\n
    replaceBR = re.compile('<br><br>|<br>')
	#��url�����׸��ȥ��
    removeElse = re.compile('">')
	#�������ǩ�޳�
    removeExtraTag = re.compile('<.*?>')
	#��Video�޳�
    removeVideo = re.compile('Video')
	#��&#x27;װ��Ϊ'
    replaceFen = re.compile('&#x27;')
	#�޳�width��ǩ
    removeWidth = re.compile('{width}')
    #�޳�����׸��
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
        #strip()��ǰ���������ɾ��
        return x.strip()

    def replacePic(self,x):
        x = re.sub(self.removeWidth,"320",x)
        #strip()��ǰ���������ɾ��
        return x.strip()

class BBC:
    def __init__(self, baseUrl):
        print "__init__"
        self.baseURL = baseUrl
        self.tool = Tool()
		#ȫ��file�������ļ�д���������
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
                print "����BBC,����ԭ��", e.reason # u''�ᱨ�� why
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
			#���ı�����ȥ����ǩ����ͬʱ��ǰ����뻻�з�
            content = str(count) + "\n" + self.tool.replace(item)+"\n"+"\n"               
            count = count + 1                  
            contents.append(content.encode('utf-8'))
        return contents
			
			
    def getPicture(self):
        #��url����Ѱ����������ͼ
        page = self.getPage(1)
        pattern = re.compile('data-src="(.*?)" data-widths=', re.S)
        result = re.findall(pattern, page)
        contents = []
        for item in result:
            #print   "The Picture url is :  " + self.tool.replacePic(item)
			#���ı�����ȥ����ǩ����ͬʱ��ǰ����뻻�з�
            content = "\n" + self.tool.replacePic(item) + "\n"
            contents.append(content.encode('utf-8'))
        return contents	
        return "0.0"
 		
    def saveDataToFile(self,contents):
        #���ļ�д��ÿһ¥����Ϣ
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
        self.file = open("BBC News " + ".txt","w+")
        try:
            print "BBC News "
            contents = BBC.getPostData()
            print "getPostData OK"
            #self.saveDataToFile(contents)
            contentsPic = BBC.getPicture()

            #�����Ĵ�����
            if contents == [] :
                contents = ['URL is None']
            if contentPic == [] :
                contentPic = ['Pic is None']

            self.saveAllToDb(contents,contentsPic)
            mkpath = os.path.abspath('.') + "\\News\\BBC_Mini"
            #���ļ����򴴽�
            if os.path.isdir(mkpath):
                pass
            else:
                os.mkdir(mkpath)
            #self.saveImg(contentsPic ,  mkpath )
        #����д���쳣
        except IOError,e:
            print "д���쳣��ԭ��" + e.message
        finally:
            print "д���������"
            self.file.close()

start = time.clock()
baseURL = 'http://www.bbc.com/news'
BBC = BBC(baseURL)
BBC.start()
cur.close()
conn.close()
end = time.clock()
print('Running time: %s Seconds'%(end-start))