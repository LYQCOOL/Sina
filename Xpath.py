# coding: utf-8
import re


def pathOneNode(tree, path):
    try:
        content = tree.xpath(path)
        return re.sub('\s', '', content[0])
    except Exception as e:
        print 'Xpath解析错误:', e
        print path
        return None


def pathAllNode(tree, path):
    try:
        content = tree.xpath(path)
        return re.sub('\s', '', content[0].xpath('string(.)'))
    except Exception as e:
        print 'Xpath解析错误:', e
        print path
        return None
