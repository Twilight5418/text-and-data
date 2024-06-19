# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 16:42:52 2018

@author: bin
"""

# 目标爬取店铺的评论

import requests
from bs4 import BeautifulSoup
import time, random
import pymysql
import re
from fake_useragent import UserAgent
import os
import joblib
import jieba
import pandas as pd
import uuid
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 加载模型和停用词
tv2 = joblib.load(
    r"C:\Users\17662\Desktop\数据库\dianping_textmining\数据库\评论爬取\文本分析挖掘\tfidf_vectorizer.pkl")
clf = joblib.load(
    r"C:\Users\17662\Desktop\数据库\dianping_textmining\数据库\评论爬取\文本分析挖掘\naive_bayes_model.pkl")


infile = open("stopwords.txt", encoding='utf-8')
stopwords_lst = infile.readlines()
stopwords = [x.strip() for x in stopwords_lst]

# 中文分词函数
def fenci(train_data):
    words_df = train_data.apply(lambda x: ' '.join(jieba.cut(x)))
    return words_df

# 定义分析函数
def fenxi(strings):
    strings_fenci = fenci(pd.Series([strings]))
    return float(clf.predict_proba(tv2.transform(strings_fenci))[:, 1])
ua = UserAgent()

# 设置cookies
cookie = ("_lxsdk_cuid=18f140237dcc8-0233cb317ee2a8-4c657b58-190140-18f140237dcc8; "
          "_lxsdk=18f140237dcc8-0233cb317ee2a8-4c657b58-190140-18f140237dcc8; "
          "_hc.v=5aed5439-6a4d-e693-2a27-1f47e19b99b9.1714027642; "
          "s_ViewType=10; "
          "ua=%E5%93%88%E5%93%88%E5%93%88; "
          "ctu=161c08166efc15e81c2300a4a485cf164138cf1a127f729c648cc006f2ab3e96; "
          "cye=hangzhou; "
          "Hm_lvt_e6f449471d3527d58c46e24efb4c343e=1714027739; "
          "cy=3; "
          "dper=0202362124ccf5b4b324a3d11d54f89c49246d8cd3403c17e98d731c31511324160265da59720d101b22c292fc005d35d2480c3f97e2e682c3ed00000000a32000004520cff69c0f82cff91794a0cec0d48da7155ea233ee048607a33fa43328d69451c3de5938c302d116392b7d3db9c266; "
          "ll=7fd06e815b796be3df069dec7836c3df; "
          "_lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; "
          "_lxsdk_s=190050d6ebd-e29-f5c-870%7C%7C60")

# 修改请求头
headers = {
    'User-Agent': ua.random,
    'Cookie': cookie,
    'Connection': 'keep-alive',
    'Host': 'www.dianping.com',
    'Referer': 'http://www.dianping.com/shop/521698/review_all/p6'
}


# 获取html页面
def getHTMLText(url, code="utf-8"):
    """
    发送HTTP请求获取HTML页面内容，并返回页面的文本。
    """
    try:
        time.sleep(random.random() * 6 + 2)
        r = requests.get(url, timeout=5, headers=headers)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except Exception as e:
        print("产生异常:", e)
        return "产生异常"


# 因为评论中带有emoji表情，是4个字符长度的，mysql数据库不支持4个字符长度，因此要进行过滤
def remove_emoji(text):
    """
    移除评论中的emoji表情。
    """
    try:
        highpoints = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return highpoints.sub(u'', text)


# 从html中提取所需字段信息
def parsePage(html, shopID):
    """
    解析HTML页面，提取所需的字段信息，并返回包含这些信息的字典列表。
    """
    infoList = []  # 用于存储提取后的信息，列表的每一项都是一个字典
    soup = BeautifulSoup(html, "html.parser")

    for item in soup.find_all('div', class_='main-review'):
        # 生成唯一的评论ID
        comment_id = str(uuid.uuid4())

        cus_id = item.find('a', class_='name').text.strip()
        comment_time = item.find('span', class_='time').text.strip()
        try:
            comment_star_class = item.find('span', class_=re.compile('sml-rank-stars')).get('class')[1]
            comment_star = float(re.search(r'\d+', comment_star_class).group()) / 10
        except:
            comment_star = 0.0

        cus_comment = item.find('div', class_="review-words").text.strip()
        scores = str(item.find('span', class_='score'))

        try:
            kouwei = re.search(r'口味：(\d+)', scores).group(1)
            huanjing = re.search(r'环境：(\d+)', scores).group(1)
            fuwu = re.search(r'服务：(\d+)', scores).group(1)
        except AttributeError:
            kouwei = huanjing = fuwu = '无'

        infoList.append({
            'comment_id': comment_id,
            'cus_id': cus_id,
            'comment_time': comment_time,
            'comment_star': comment_star,
            'cus_comment': remove_emoji(cus_comment),
            'kouwei': kouwei,
            'huanjing': huanjing,
            'fuwu': fuwu,
            'shopID': shopID
        })

    return infoList


# 存储爬取到的数据
def save_data(data_dict):
    # 获取评论内容
    comment_text = data_dict['cus_comment']
    # 调用情感分析函数获取评分
    sentiment_score = fenxi(comment_text)

    sql_dzdp = '''INSERT INTO DZDP(cus_id, comment_time, comment_star, cus_comment, kouwei, huanjing, fuwu, shopID) 
                  VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'''
    value_tup_dzdp = (
        data_dict['cus_id'],
        data_dict['comment_time'],
        data_dict['comment_star'],
        data_dict['cus_comment'],
        data_dict['kouwei'],
        data_dict['huanjing'],
        data_dict['fuwu'],
        data_dict['shopID']
    )

    sql_comments = '''INSERT INTO 评论(评论id, 应用id, 评论内容, 口味, 环境, 服务, 评分, 评论用户id, 商店id, 评论日期, 情感评分) 
                      VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    value_tup_comments = (
        data_dict['comment_id'],  # 评论id
        25,  # 默认应用id
        data_dict['cus_comment'],  # 评论内容
        data_dict['kouwei'],  # 口味
        data_dict['huanjing'],  # 环境
        data_dict['fuwu'],  # 服务
        data_dict['comment_star'],  # 评分
        data_dict['cus_id'],  # 评论用户id
        data_dict['shopID'],  # 商店id
        data_dict['comment_time'],  # 评论日期
        sentiment_score  # 情感评分
    )

    sql_update_statistics = '''INSERT INTO 评论统计 (评论用户id, 评论数)
                               VALUES (%s, 1)
                               ON DUPLICATE KEY UPDATE 评论数 = 评论数 + 1'''
    value_tup_statistics = (data_dict['cus_id'],)

    try:
        cursor.execute(sql_dzdp, value_tup_dzdp)
        cursor.execute(sql_comments, value_tup_comments)
        cursor.execute(sql_update_statistics, value_tup_statistics)
        db.commit()
    except Exception as e:
        db.rollback()
        print('数据库写入失败:', e)
    return


# 生成词云并存储高频词
def generate_wordcloud_and_save(texts, shopID):
    text = ' '.join(texts)
    wc = WordCloud(font_path="msyh.ttc", background_color='white', max_words=100, stopwords=stopwords,
                   max_font_size=80, random_state=42, margin=3).generate(text)

    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()

    word_freq = wc.words_
    for word, freq in word_freq.items():
        sql_word = '''INSERT INTO 评论分词表(shopID, word, frequency) VALUES(%s, %s, %s)'''
        cursor.execute(sql_word, (shopID, word, freq))
    db.commit()


def close_sql():
    cursor.close()
    db.close()


# 构造每一页的url，并且对爬取的信息进行存储
def getCommentinfo(shop_url, shopID, page_begin, page_end):
    """
    构造每一页的URL，调用getHTMLText和parsePage函数获取并存储爬取的信息。
    """
    comments = []
    for i in range(page_begin, page_end):
        try:
            url = shop_url + 'p' + str(i)
            html = getHTMLText(url)
            infoList = parsePage(html, shopID)
            print('成功爬取第{}页数据,有评论{}条'.format(i, len(infoList)))
            for info in infoList:
                save_data(info)
                comments.append(info['cus_comment'])
            # 断点续传中的断点
            if (html != "产生异常") and (len(infoList) != 0):
                with open('xuchuan.txt', 'a') as file:
                    duandian = str(i) + '\n'
                    file.write(duandian)
            else:
                print('休息60s...')
                time.sleep(60)
        except Exception as e:
            print('跳过本次:', e)
            continue

    if comments:
        generate_wordcloud_and_save(comments, shopID)

    return


def xuchuan():
    """
    读取断点续传文件，获取当前爬取的页码。
    """
    if os.path.exists('xuchuan.txt'):
        file = open('xuchuan.txt', 'r')
        nowpage = int(file.readlines()[-1])
        file.close()
    else:
        nowpage = 0
    return nowpage


def delete_file(filename):
    """
    删除指定的文件。
    """
    try:
        os.remove(filename)
        print(f"文件 {filename} 已成功删除")
    except FileNotFoundError:
        print(f"错误：文件 {filename} 未找到")
    except PermissionError:
        print(f"错误：没有权限删除文件 {filename}")
    except Exception as e:
        print(f"错误：无法删除文件 {filename}。错误信息：{e}")


# 根据店铺id，店铺页码进行爬取
def craw_comment(shopID='521698', page=5):
    """
    根据店铺ID和页码爬取评论，并进行断点续传。
    """
    delete_file('xuchuan.txt')
    shop_url = "http://www.dianping.com/shop/" + shopID + "/review_all/"
    # 读取断点续传中的续传断点
    nowpage = xuchuan()
    getCommentinfo(shop_url, shopID, page_begin=nowpage + 1, page_end=page + 1)
    close_sql()
    return


def connect_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="5457hzcx",
        database="TESTDB",
        charset='utf8mb4',
        connect_timeout=60,
        read_timeout=300,
        write_timeout=300
    )


def create_table(cursor):
    """
    创建表DZDP和评论。
    """
    cursor.execute("DROP TABLE IF EXISTS DZDP")
    sql = '''CREATE TABLE DZDP(
            cus_id VARCHAR(100),
            comment_time VARCHAR(55),
            comment_star VARCHAR(55),
            cus_comment TEXT,
            kouwei VARCHAR(55),
            huanjing VARCHAR(55),
            fuwu VARCHAR(55),
            shopID VARCHAR(55)
            );'''
    cursor.execute(sql)
    print("表DZDP创建成功")

    cursor.execute("DROP TABLE IF EXISTS 评论")
    sql = '''CREATE TABLE 评论 (
            评论id VARCHAR(100) PRIMARY KEY,
            应用id VARCHAR(100),
            评论内容 TEXT,
            口味 VARCHAR(55),
            环境 VARCHAR(55),
            服务 VARCHAR(55),
            评分 VARCHAR(55),
            评论用户id VARCHAR(100),
            商店id VARCHAR(55),
            评论日期 VARCHAR(55),
            情感评分 VARCHAR(55)
        );'''
    cursor.execute(sql)
    print("表评论创建成功")

    cursor.execute("DROP TABLE IF EXISTS 评论统计")
    sql = '''CREATE TABLE 评论统计(
                评论用户id VARCHAR(100) PRIMARY KEY,
                评论数  INT
                );'''
    cursor.execute(sql)
    print("表评论统计创建成功")

    cursor.execute("DROP TABLE IF EXISTS 评论分词表")
    sql = '''CREATE TABLE 评论分词表(
                shopID VARCHAR(55),
                word VARCHAR(255),
                frequency FLOAT
                );'''
    cursor.execute(sql)
    print("表评论分词表创建成功")


db = connect_db()
cursor = db.cursor()
create_table(cursor)

if __name__ == "__main__":
    craw_comment()
