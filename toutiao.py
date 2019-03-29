import json
import requests
import datetime
import sys
import ssl
import os
import urllib
from urllib import request
from bs4 import BeautifulSoup

ssl._create_default_https_context = ssl._create_unverified_context


def get_html(url):
    headers = {
        'user-agent': 'Mozilla / 5.0(Windows NT 10.0; WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 53.0.2785.104Safari / 537.36Core / 1.53.4882.400QQBrowser / 9.7.13059.400'
    }
    req = requests.get(url, headers=headers)
    return req.text.encode(req.encoding).decode()


def get_json(url):
    req = requests.get(url)
    return req.json()


def getTitle(script):
    script = repr(script)
    script = script[script.find('articleInfo') + 12:script.find('commentInfo') - 7]
    script = script[:script.find('groupId') - 44] + '\"'
    script = script[script.find('title') + 8: script.find('content') - 10]
    return script.decode("unicode-escape")


def getContent(script):
    script = repr(script)
    script = script[script.find('articleInfo') + 12:script.find('commentInfo') - 7]
    script = script[:script.find('groupId') - 44] + '\"'
    script = script[script.find('content') + 10: -13].replace('&lt;', '<').replace('&gt;', ">").replace('&quot;', '\"')
    return script.decode("unicode-escape")


def getTime(script):
    script = repr(script)
    script = script[script.find('subInfo') + 12:script.find('commentInfo') - 7]
    script = script[script.find('time'):][7:23]
    return script.decode("unicode-escape")


def getInfo(offset, keyword):
    keyword = urllib.parse.quote(keyword)
    print
    '正在抓取%s数据...' % (keyword)
    url = """
    https://www.toutiao.com/api/search/content/?aid=24&app_name=web_search&offset=%s&format=json&keyword=%s
    """ % (offset, keyword)
    print(url)
    for str in get_json(url)['data']:
        try:
            url = str.get('article_url')
            if url != None and url.startswith('http://toutiao.com'):
                html = get_html(url)
                if html != '<html><head></head><body></body></html>':
                    soup = BeautifulSoup(html, 'html5lib')
                    scripts = soup.find_all('script')
                    script = scripts[6]
                    print(getTitle(script))
                    print(script)
        except Exception as ex:
            print('错误', ex)
            continues


if __name__ == "__main__":
    # for offset in range(0, 1, 1):
    getInfo(0, '长春')
