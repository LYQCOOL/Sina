# coding:utf-8

import pymongo

class MongoDB(object):
    def __init__(self):
        #self.__conn = pymongo.MongoClient('localhost', port=27017)
        self.__conn = pymongo.MongoClient('localhost', port=27001)
        db = self.__conn['news']

        self.collection_zhengwen = db['content']
        self.collection_comment = db['comment']
        self.collection_news_url=db['sina_url']

    def put_content(self,value):
        return self.collection_zhengwen.save(value)

    def put_comment(self,value):
        return self.collection_comment.save(value)

    def put_url(self,value):
        return self.collection_news_url.save(value)

    def get_urls(self):
        result = self.collection_news_url.find()
        queue = []
        for  i in result:
            queue.append(i)
        return queue

    def delete_url(self,value):
        self.collection_news_url.remove({'_id':value})


