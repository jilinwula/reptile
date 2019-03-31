import json
import requests
import datetime
import sys
import ssl
import os
import urllib
import pymysql
from urllib import request
from bs4 import BeautifulSoup

ssl._create_default_https_context = ssl._create_unverified_context


def save_info(script):
    db = pymysql.connect(host='47.95.201.47', user='root', passwd='password', port=9294, db='wordpress', charset='utf8')

    cursor = db.cursor()

    sql = "SELECT count(1) from wp_posts where post_title like '%{0}%' and post_status = 'publish' limit 1".format(get_title(script))

    print(sql)

    cursor.execute(sql)

    data = cursor.fetchone()

    if data[0] == 1:
        return

    sql = """
    INSERT INTO wp_posts (post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt,
                                post_status, comment_status, ping_status, post_password, post_name, to_ping, pinged,
                                post_modified, post_modified_gmt, post_content_filtered, post_parent, guid, menu_order,
                                post_type, post_mime_type, comment_count)
VALUES (2, '{0}', '{1}', '{2}', '{3}', '', 'publish', 'open', 'open', '',
        '%e4%b8%ba%e6%a2%a6%e5%90%af%e8%88%aa-%e9%9f%b5%e5%8a%a8%e6%98%a5%e5%9f%8e-%e9%85%b7%e7%8b%97%e9%9f%b3%e4%b9%90%e9%95%bf%e6%98%a5%ef%bc%88%e4%ba%8c%e9%81%93%ef%bc%89%e4%ba%a7%e4%b8%9a%e5%ad%b5%e5%8c%96',
        '', '', '{4}', '{5}', '', 0,
        'http://wordpress.jilinwula.com:80/wordpress/?p=590', 0, 'post', '', 0);
    """.format(get_time(script), get_time(script), get_content(script), get_title(script), get_time(script),
               get_time(script))
    print(sql)
    try:
        cursor.execute(sql)

        db.commit()
    except:
        db.rollback()
    id = cursor.lastrowid

    sql = """update wp_posts set guid = 'http://wordpress.jilinwula.com:80/wordpress/?p={0}' where ID = {1};""".format(
        id, id)
    print(sql)
    try:
        cursor.execute(sql)

        db.commit()
    except:
        db.rollback()

    sql = """INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order)VALUES ({0}, 36, 0);""".format(
        id)
    print(sql)
    try:
        cursor.execute(sql)

        db.commit()
    except:
        db.rollback()

    sql = """INSERT INTO wordpress.wp_postmeta (post_id, meta_key, meta_value) VALUES (%s, '_wpcom_metas', 'a:2:{s:14:"copyright_type";s:6:"type_1";s:13:"original_name";s:12:"今日头条";}')""" % id
    print(sql)
    try:
        cursor.execute(sql)

        db.commit()
    except:
        db.rollback()

    sql = """INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order)VALUES (%s, 38, 0);""" % id
    print(sql)
    try:
        cursor.execute(sql)

        db.commit()
    except:
        db.rollback()

    db.close()


def get_html(url):
    headers = {
        'user-agent': 'Mozilla / 5.0(Windows NT 10.0; WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 53.0.2785.104Safari / 537.36Core / 1.53.4882.400QQBrowser / 9.7.13059.400'
    }
    req = requests.get(url, headers=headers)
    return req.text.encode(req.encoding).decode()


def get_json(url):
    req = requests.get(url)
    return req.json()


def get_title(script):
    script = repr(script)
    script = script[script.find('articleInfo') + 12:script.find('commentInfo') - 7]
    script = script[:script.find('groupId') - 44] + '\"'
    script = script[script.find('title') + 8: script.find('content') - 10]
    return script


def get_content(script):
    script = repr(script)
    script = script[script.find('articleInfo') + 12:script.find('commentInfo') - 7]
    script = script[:script.find('groupId') - 44] + '\"'
    script = script[script.find('content') + 10: -13].replace('&lt;', '<').replace('&gt;', ">").replace('&quot;',
                                                                                                        '\"').replace(
        '&#x3D;', '=')
    return script


def get_time(script):
    script = repr(script)
    script = script[script.find('subInfo') + 12:script.find('commentInfo') - 7]
    script = script[script.find('time'):][7:23]
    return script


def get_info(offset, keyword):
    keyword = urllib.parse.quote(keyword)
    print
    '正在抓取%s数据...' % (keyword)
    url = """
    https://www.toutiao.com/api/search/content/?aid=24&app_name=web_search&offset=%s&format=json&keyword=%s
    """ % (offset, keyword)
    for str in get_json(url)['data']:
        try:
            url = str.get('article_url')
            if url != None and url.startswith('http://toutiao.com'):
                html = get_html(url)
                print(url)
                if html != '<html><head></head><body></body></html>':
                    soup = BeautifulSoup(html, 'html5lib')
                    scripts = soup.find_all('script')
                    script = scripts[6]
                    save_info(script)
        except Exception as ex:
            print('错误', ex)
            continue


if __name__ == "__main__":
    for offset in range(0, 100, 20):
        get_info(offset, '长春')
        get_info(offset, '吉林')
        get_info(offset, '吉林省')
        get_info(offset, '长春新区')
        get_info(offset, '景俊海')
