# coding: utf-8

import sys
sys.path.append('../')
reload(sys)
sys.setdefaultencoding('utf-8')


from Queues import *
import requests
import re
import threading
import time
from lxml import etree
from datetime import datetime, timedelta
from lxml import etree
from Xpath import *
from database import MongoDB
import json
from Logging import Logging



class getnews(object):
    def __init__(self):
        self.mongo = MongoDB()
        self.news_url_queue=news_url_Queue() # 存新闻url，用于多线程爬取
        self.news_html_queue=news_url_Queue() # 存新闻html
        self.old_day_news_queue = news_url_Queue()
        # self.log = Logging('../helloword/static/sina').get_logging()
        self.log=Logging('../Sina/sina.txt').get_logging()


    def run(self,nums):
        #开始计时，爬完一次需用时
        time_0 = time.time()

        #获取当天所有新闻url，加入news_url_queue
        self.get_news_url()
        time.sleep(5)

       #将数据库里以前的url信息读取到old_day_news_queue
        self.read_url_info()

        #开始逐个判断old_day_news_queue里的评论是否有更新，有则加入news_url_queue，否则就删除数据库本地信息，直到队列空
        thread_list3 = [threading.Thread(target=self.judge_comment) for i in range(nums)]
        for t in thread_list3:
            t.start()
        for t in thread_list3:
            if t.is_alive():
                t.join()
        time.sleep(5)


        #去除重复元素
        xqueue = set(self.news_url_queue.queue)
        self.news_url_queue.queue=list(xqueue)


        #逐个读取news_url_queue内容，获取正文html，并存入news_html_queue，直到队列空
        thread_list = [threading.Thread(target=self.get_news_html) for i in range(nums)]
        for t in thread_list:
            t.start()
        for t in thread_list:
            if t.is_alive():
                t.join()
        time.sleep(5)
        print '新闻个数：   '+str(len(self.news_html_queue.queue))

        #开始逐个解析news_html_queue里的内容，同时存正文，爬评论存评论，存url信息到数据库，直到队列空
        thread_list2=[threading.Thread(target=self.get_message) for i in range(nums)]
        for x in thread_list2:
            x.start()
        for x in thread_list2:
            if x.is_alive():
                x.join()
        print ("结束: ", time.time() - time_0, "\n")




    def get_news_url(self):
        URL_LIST = ['http://news.sina.com.cn/society/',
                    'http://ent.sina.com.cn/',
                    'http://sports.sina.com.cn/',
                    'http://finance.sina.com.cn/',
                    'http://news.sina.com.cn/china/']
        re_list = ['http://news.sina.com.cn/[a-z]+/[a-z]+/\d{4}-\d{2}-\d{2}/doc-[a-z]{8}\d{7}.shtml',
                   'http://ent.sina.com.cn/[a-z]+/[a-z]+/\d{4}-\d{2}-\d{2}/doc-[a-z]{8}\d{7}.shtml',
                   'http://sports.sina.com.cn/[a-z]+/[a-z]+/\d{4}-\d{2}-\d{2}/doc-[a-z]{8}\d{7}.shtml',
                   'http://finance.sina.com.cn/[a-z]+/[a-z]+/\d{4}-\d{2}-\d{2}/doc-[a-z]{8}\d{7}.shtml',
                   'http://news.sina.com.cn/[a-z]+/[a-z]+/\d{4}-\d{2}-\d{2}/doc-[a-z]{8}\d{7}.shtml']

        time_today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
        for channel in range(0, 5):
            URL = URL_LIST[channel]
            while 1:
                print '新闻版块：     '+ URL
                try:
                    html = requests.get(URL, timeout=30).content
                    break
                except Exception as e:
                    self.log.info('can not get the source page for news urllist')
                    # print e
            re_ = re_list[channel]
            news_url_list = re.findall(re_, html)
            print '本版块个数：     '+str(len(news_url_list))
            for j in news_url_list:
                this_time = re.search('\d{4}-\d{2}-\d{2}',j).group(0)
                if this_time == time_today:
                    self.news_url_queue.queue.append(j)
                else:
                    pass

    def read_url_info(self):
        try:
            self.old_day_news_queue.queue= self.mongo.get_urls()
        except Exception as e:
            self.log.info('function read_url_info() error!')
            self.log.info(e)



    def judge_comment(self):
        while len(self.old_day_news_queue.queue):
            try:
                info = self.old_day_news_queue.out_queue()
                url = info['_id']
                comment_count = self.getCommentNumber(url)
                flag = comment_count-info['comment_count']
                if flag>=20:
                    self.news_url_queue.queue.append(url)
                else:
                    self.mongo.delete_url(url)
            except Exception as e:
                self.log.info('function judge_comment() error')
                self.log.info(e)


    def get_news_html(self):
        while  len(self.news_url_queue.queue):
            i = self.news_url_queue.out_queue()
            try:
                html=requests.get(i,timeout=30).content.decode()
                # print i
                self.news_html_queue.in_queue(html)
            except Exception as e:
                self.log.info('can not get this page of html'+i)
                self.log.info(e)


    def get_message(self):
        while len(self.news_html_queue.queue):
            try:
                i = self.news_html_queue.out_queue()
                #排除手机版网页
                if re.findall(r'<meta property="og:url" content="(.*?)" />', i):
                    news_url = re.findall(r'<meta property="og:url" content="(.*?)" />', i)[0]
                else:
                    continue

                ping_lun_shu_liang = self.getCommentNumber(news_url)
                yue_du_shu = None
                if ping_lun_shu_liang:
                    all_page = ping_lun_shu_liang / 20
                    comment_url_list = []
                    for page in xrange(1, all_page + 1):
                        newsid = re.findall(r'([a-z]{7}\d{7})\.shtml', news_url)[0]
                        channel = re.findall(r'http://(.*?).sina', news_url)[0]
                        if (channel == 'finance'):
                            channel = 'cj'
                        elif (channel == 'sports'):
                            channel = 'ty'
                        elif (channel == 'ent'):
                            channel = 'yl'
                        else:
                            channel = re.findall(r'com\.cn/([a-z]+)/', news_url)[0]
                            if (channel == 's'):
                                channel = 'sh'
                            else:
                                channel = 'gn'
                        comment_url = 'http://comment5.news.sina.com.cn/page/info?format=js&channel=%s&newsid=comos-%s&group=&compress=1&ie=gbk&oe=gbk&page=%s&page_size=20' % (channel, newsid, page)
                        comment_url_list.append(comment_url)
                    for com_url in comment_url_list:
                        self.get_comment(news_url,com_url)



                else:
                    ping_lun_shu_liang = 0

                tree = etree.HTML(i)
                message_dict = dict()
                url_info = dict()

                # print' 文章网址'
                wen_zhang_wang_zhi = news_url
                message_dict['wen_zhang_wang_zhi'] = wen_zhang_wang_zhi
                # print'  # 文章标题'
                wen_zhang_biao_ti = pathOneNode(tree,
                                             '//div[@class="main-content w1240"]/h1/text()')

                message_dict['wen_zhang_biao_ti'] = wen_zhang_biao_ti

                # print'  # 发布时间'
                fa_bu_shi_jian = pathOneNode(tree,
                                             '//div[@class="date-source"]/span/text()')
                if not fa_bu_shi_jian:
                    fa_bu_shi_jian = re.findall('<span class="titer">(.*?)</span>', i)[0]

                fa_bu_shi_jian = re.findall('(\d{4}.*\d{2})', fa_bu_shi_jian)[0]
                # print news_url+fa_bu_shi_jian
                message_dict['fa_bu_shi_jian'] = fa_bu_shi_jian
                # print'  # 评论数量'
                ping_lun_shu_liang = ping_lun_shu_liang
                message_dict['ping_lun_shu_liang'] = ping_lun_shu_liang

                # print'  # 文章来源'
                # (//div[@class="article article_16"]/p[2]/text())
                wen_zhang_lai_yuan = pathOneNode(tree,
                                                 '//div[@class="date-source"]/a/text()| //div[@class="date-source"]/span[@class="source ent-source"]/text()|//div[@class="date-source"]/span[@class="source"]/text()')
                message_dict['wen_zhang_lai_yuan'] = wen_zhang_lai_yuan

                # print'  # 文章正文'
                wen_zhang_zheng_wen = tree.xpath('//div[@class="article"]/p/text()')
                wen_zhang_zheng_wen = ''.join(wen_zhang_zheng_wen)
                #print wen_zhang_zheng_wen
                message_dict['wen_zhang_zheng_wen'] = wen_zhang_zheng_wen

                # print' # 抓取时间'
                do_time = time.time()
                message_dict['do_time'] = do_time

                # print' # 抓取网站'
                zhan_dian = u'新浪网'
                message_dict['zhan_dian'] = zhan_dian

                # print'  # 图片链接'
                tu_pian_lian_jie = tree.xpath('//div[@class="img_wrapper"]/img/@src')
                if tu_pian_lian_jie:
                    tu_pian_lian_jie = ' '.join(tu_pian_lian_jie)
                    if tu_pian_lian_jie.startswith('http:'):
                        tu_pian_lian_jie=tu_pian_lian_jie
                    else:tu_pian_lian_jie='http:'+tu_pian_lian_jie
                    message_dict['tu_pian_lian_jie'] = tu_pian_lian_jie
                else:
                    message_dict['tu_pian_lian_jie'] = None

                    # print'  # 文章栏目'
                # wen_zhang_lan_mu = pathAllNode(tree,
                #                                '(//div[@class="bread"]/a)|(//div[@class="bread"]/span)|(//div[@class="nav-g__breadcrumb layout-fl"]/a)|(//div[@class="text notInPad"]/a)')
                # message_dict['wen_zhang_lan_mu'] = wen_zhang_lan_mu
                #
                # print'   # 文章作者'
                if tree.xpath('(//p[@class="article-editor"]/text())|(//p[@class="show_author"]/text())'):
                 wen_zhang_zuo_zhe = pathOneNode(tree,
                                                '(//p[@class="article-editor"]/text())|(//p[@class="show_author"]/text())')
                else:
                    wen_zhang_zuo_zhe = '佚名'
                message_dict['wen_zhang_zuo_zhe'] = wen_zhang_zuo_zhe

                # print' # 关键词'
                if tree.xpath('//div[@class="keywords"]'):
                 guan_jian_ci = tree.xpath(
                                           '//div[@class="keywords"]/a/text()')

                 guan_jian_ci = ' '.join(guan_jian_ci)
                else:guan_jian_ci=None
                message_dict['guan_jian_ci'] = guan_jian_ci

                # print'  # 相关标签'
                # xiang_guan_biao_qian = pathAllNode(tree,'(//section[@class="article-a_keywords"])|(//p[@class="art_keywords"])')
                # message_dict['xiang_guan_biao_qian'] = xiang_guan_biao_qian
                #
                # print'  # 阅读数量'
                yue_du_shu = yue_du_shu
                message_dict['yue_du_shu'] = yue_du_shu

                # print'  # 主键'
                message_dict['_id'] = news_url

                # print json.dumps(message_dict, ensure_ascii=False, indent=4)
                print '剩余未爬取新闻个数'+str(len(self.news_html_queue.queue))
                url_info['_id'] = news_url
                url_info['comment_count'] = ping_lun_shu_liang
                url_info['do_time'] = do_time
                self.mongo.put_url(url_info)
                self.mongo.put_content(message_dict)
            except Exception as e:
                self.log.info(e)
                # print e

    def getCommentNumber(self, news_url):
        newsid = re.findall(r'([a-z]{7}\d{7})\.shtml',news_url)[0]
        channel=re.findall(r'http://(.*?).sina',news_url)[0]
        if(channel=='finance'):
            channel = 'cj'
        elif(channel=='sports'):
            channel = 'ty'
        elif (channel == 'ent'):
            channel = 'yl'
        else:
            channel = re.findall(r'com\.cn/([a-z]+)/',news_url)[0]
            if(channel=='s'):
                channel='sh'
            else:
                channel='gn'
        comment_url = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel=%s&newsid=comos-%s&group=&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=20' % (channel,newsid)
        flag = 1
        while 1:
            try:
                x = requests.get(comment_url, timeout=30).content
                #　print x
                json_object = json.loads(re.findall('var data=([\S\s]+)', x)[0])
                break
            except Exception as e:
                flag += 1
                self.log.info('default to get this page of comment')
                # print e
            if flag > 5:
                return
        # 阅读数
        # yue_du_shu = json_object['join_count']
        # 评论数
        try:
            ping_lun_shu_liang = json_object['result']['count']['show']
        except Exception as e:
            ping_lun_shu_liang = 0
        #return yue_du_shu
        return ping_lun_shu_liang


    def get_comment(self,news_url,comment_url):
        #　print '开始获取评论'
        try:
            # print comment_url
            json_object = json.loads(requests.get(comment_url, timeout=30).content.replace('var data=', ''))
            # print json_object
            comment_dict = dict()
            for item in json_object['result']['cmntlist']:
                # 评论文章url
                news_url = news_url
                # 评论内容
                ping_lun_nei_rong = item["content"]
                comment_dict['ping_lun_nei_rong'] = ping_lun_nei_rong

                # 评论时间
                ping_lun_shi_jian = item["time"]
                comment_dict['ping_lun_shi_jian'] = ping_lun_shi_jian

                # 回复数量
                hui_fu_shu = None
                comment_dict['hui_fu_shu'] = hui_fu_shu

                # 点赞数量
                dian_zan_shu = item["agree"]
                comment_dict['dian_zan_shu'] = dian_zan_shu

                # 评论id
                ping_lun_id = item["mid"]
                comment_dict['ping_lun_id'] = ping_lun_id

                # 用户昵称
                yong_hu_ming = item["nick"]
                comment_dict['yong_hu_ming'] = yong_hu_ming

                # 性别
                xing_bie = None
                comment_dict['xing_bie'] = xing_bie

                # 用户等级
                yong_hu_deng_ji = item["level"]
                comment_dict['yong_hu_deng_ji'] = yong_hu_deng_ji

                # 用户省份
                yong_hu_sheng_fen = item["area"]
                comment_dict['yong_hu_sheng_fen'] = yong_hu_sheng_fen

                # 抓取时间
                do_time = time.time()
                comment_dict['do_time'] = do_time

                # 抓取网站
                zhan_dian = u'新浪'
                comment_dict['zhan_dian'] = zhan_dian

                # 主键
                comment_dict['_id'] = ping_lun_id + news_url

                # print json.dumps(comment_dict, ensure_ascii=False, indent=4)
                self.mongo.put_comment(comment_dict)
        except Exception as e:
            self.log.info(e)
            # print e


def DeltaSeconds():
    from datetime import datetime, timedelta
    curTime = datetime.now()
    try:
        desTime = curTime.replace(day=curTime.day+1, hour=20, minute=0, second=0, microsecond=0)
    except ValueError:
        desTime = curTime.replace(month=curTime.month+1, day=1, hour=20, minute=0, second=0, microsecond=0)
    delta = desTime - curTime
    print delta
    skipSeconds = delta.total_seconds()
    return skipSeconds


if __name__=='__main__':
    while 1:
        try:
            x = getnews()
            x.run(20)
            print '爬取完毕，进入休眠'
            sleepTime = DeltaSeconds()
            time.sleep(sleepTime)
        except Exception as e:
            print e
