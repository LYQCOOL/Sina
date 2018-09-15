#coding:utf-8

from database import  MongoDB
import requests

def start():
    urllist = [
    'http://comment5.news.sina.com.cn/page/info?format=js&channel=ty&newsid=comos-fymkwwk7111427&group=&compress=1&ie=gbk&oe=gbk&page=21&page_size=20',
    'http://comment5.news.sina.com.cn/page/info?format=js&channel=ty&newsid=comos-fymkwwk7098702&group=&compress=1&ie=gbk&oe=gbk&page=10&page_size=20',
    'http://comment5.news.sina.com.cn/page/info?format=js&channel=ty&newsid=comos-fymmiwm1786333&group=&compress=1&ie=gbk&oe=gbk&page=6&page_size=20',
    'http://comment5.news.sina.com.cn/page/info?format=js&channel=ty&newsid=comos-fymmiwm1786333&group=&compress=1&ie=gbk&oe=gbk&page=7&page_size=20',
    'http://comment5.news.sina.com.cn/page/info?format=js&channel=ty&newsid=comos-fymkwwk7111427&group=&compress=1&ie=gbk&oe=gbk&page=22&page_size=20',
    'http://comment5.news.sina.com.cn/page/info?format=js&channel=ty&newsid=comos-fymkwwk7098702&group=&compress=1&ie=gbk&oe=gbk&page=11&page_size=20',
    'http://comment5.news.sina.com.cn/page/info?format=js&channel=ty&newsid=comos-fymmiwm1786333&group=&compress=1&ie=gbk&oe=gbk&page=8&page_size=20']

    for i in urllist:
        html = requests.get(i).contentS
        print html

start()