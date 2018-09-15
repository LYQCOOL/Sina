#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class Status(object):
    def __init__(self,name,author,status,timestamp,count):
        '''

        :param name:爬虫名字
        :param author: 爬虫负责人
        :param status: 爬虫状态（1,0） 1位OK
        :param timestamp: 本轮时间戳
        :param count: 本轮爬取到的记录数量
        '''
        self.name= name
        self.author = author
        self.status = status
        self.timestamp = timestamp
        self.count = count

    def PostInformation(self):
        info = {}
        info['name']=self.name
        info['author'] = self.author
        info['status'] = self.status
        info['timestamp'] = self.timestamp
        info['count'] = self.count

        print info


        url ='http://182.150.37.55:5000/api/message'
        try:
            ss  = requests.post(url,data=info)
            print ss
            print ss.content
        except Exception as e:
            print e
            pass



if __name__=='__main__':
    x = Status("新浪","刘勇七",1,'00',0)
    x.PostInformation()
