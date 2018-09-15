#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../')
import requests
import re
from lxml import etree



def start():
    urllist=['http://www.028qz.com/forum-2-1.html','http://www.028qz.com/forum-38-1.html', 'http://www.028qz.com/forum-39-1.html', 'http://www.028qz.com/forum-40-1.html','http://www.028qz.com/forum-41-1.html',  'http://www.028qz.com/forum-42-1.html',  'http://www.028qz.com/forum-43-1.html', 'http://www.028qz.com/forum-45-1.html',   'http://www.028qz.com/forum-91-1.html',  'http://www.028qz.com/forum-92-1.html', 'http://www.028qz.com/forum-93-1.html','http://www.028qz.com/forum-95-1.html', 'http://www.028qz.com/forum-96-1.html', 'http://www.028qz.com/forum-97-1.html']
    try:
        for url in urllist:
            print url
            html = requests.get(url).content.decode('gbk')
            url_block_list = re.findall(r'(<tbody id="normalthread_\d+">[\S\s]*?</tbody>)', html)
            # titlelist = re.findall(r'class="s xst">(.*?)</a>',html)
            for i in url_block_list:
                # print i
                tree = etree.HTML(i)
                new_url =  ''.join(tree.xpath('//a[@class="s xst"]/@href')[0])
                title = ''.join(tree.xpath('//a[@class="s xst"]/text()')[0])
                fabu_time =  ''.join(tree.xpath('//td[@class="by"]/em/span/text()|//td[@class="by"]/em/span/span/@title')[0])
                gengxin_time = ''.join(tree.xpath('//td[@class="by"]/em/a/span/@title|//td[@class="by"]/em/a/text()')[0])
                # print new_url,title,fabu_time,'                            ',gengxin_time
                content = requests.get(new_url).content
                treexx = etree.HTML(content)
                fbsj = treexx.xpath('//div[@class="authi"]/em/text()')[0]
                if len(fbsj)<10:
                    fbsj = treexx.xpath('//div[@class="authi"]/em/span/@title')[0]
                else:
                    fbsj = fbsj[3:]
                biaoti = treexx.xpath('//span[@id="thread_subject"]/text()')[0]
                print new_url,fbsj,len(fbsj),biaoti

                # print '\n'.join(tznr.split())
                plsl = treexx.xpath('//div[@class="hm ptn"]/span[5]/text()')[0]
                print plsl
                tzzz = treexx.xpath('//div[@class="authi"]/a[@class="xw1"]/text()')[0]
                print tzzz
    except:
        pass
start()
