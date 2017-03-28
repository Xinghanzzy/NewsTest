# -*- coding: UTF-8 -*- 。
import urllib
import urllib2
import re
import time
import os
# import BBC_News.py
# import BBC_ReadNews.py
# import CNN_News.py
# import CNN_ReadNews.py

start = time.clock()
os.system("BBC_News.py")
os.system("BBC_ReadNews.py")
os.system("CNN_News.py")
os.system("CNN_ReadNews.py")
end = time.clock()
print "Running time is %s Second." % (end - start)
# start = time.clock()
# baseURL = 'http://www.bbc.com/news'
# BBC = BBC(baseURL)
# BBC.start()
# end = time.clock()
# print('Running time: %s Seconds'%(end-start))

# baseURL = 'http://edition.cnn.com/'
# CNN = CNN(baseURL)
# CNN.start()


# a = time.clock()
# baseURL = 'http://www.bbc.com'
# BdTb = BdTb(baseURL)
# BdTb.start()
# b = time.clock()
# print '%s'%(b-a)

# a = time.clock()
# baseURL = 'http://edition.cnn.com/'
# CNN = CNN(baseURL)
# CNN.start()
# b = time.clock()
# print('All Running time: %s Seconds'%(b-a))