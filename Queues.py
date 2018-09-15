#coding:utf-8

class news_url_Queue(object):
    def __init__(self):
        self.queue = []
    #新闻url
    def in_queue(self,value):
        self.queue.append(value)
    def out_queue(self):
        url = self.queue.pop(0)
        return url

