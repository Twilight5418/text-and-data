# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 15:45:05 2018

@author: bin
"""

import pymysql
#在数据库建表
def creat_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS DZDP")
    sql = '''CREATE TABLE DZDP(
            cus_id varchar(100),
            comment_time varchar(55),
            comment_star varchar(55),
            cus_comment text,
            kouwei varchar(55),
            huanjing varchar(55),
            fuwu varchar(55),
            shopID varchar(55)
            );'''
    cursor.execute(sql)

    cursor.execute("DROP TABLE IF EXISTS 评论")
    sql = '''CREATE TABLE 评论(
            评论id INT AUTO_INCREMENT PRIMARY KEY,
            应用id varchar(100),
            评论内容 text,
            口味 varchar(55),
            环境 varchar(55),
            服务 varchar(55),
            评分 varchar(55),
            评论用户id varchar(100),
            商店id varchar(55),
            评论日期 varchar(55)
            );'''
    cursor.execute(sql)


#连接MYSQL数据库
db = pymysql.connect(
    host="localhost",
    user="root",
    password="5457hzcx",
    database="TESTDB"
)
cursor = db.cursor()


#存储爬取到的数据
def save_data(data_dict):
    sql = '''INSERT INTO DZDP(cus_id,comment_time,comment_star,cus_comment,kouwei,huanjing,fuwu,shopID) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'''
    value_tup = (data_dict['cus_id']
                 ,data_dict['comment_time']
                 ,data_dict['comment_star']
                 ,data_dict['cus_comment']
                 ,data_dict['kouwei']
                 ,data_dict['huanjing']
                 ,data_dict['fuwu']
                 ,data_dict['shopID']
                 )
    sql_comments = '''INSERT INTO 评论(应用id, 评论内容, 口味, 环境, 服务, 评分, 评论用户id, 商店id, 评论日期) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    value_tup_comments = (
        25,
        data_dict['cus_comment'],
        data_dict['kouwei'],
        data_dict['huanjing'],
        data_dict['fuwu'],
        data_dict['comment_star'],
        data_dict['cus_id'],
        data_dict['shopID'],
        data_dict['comment_time']
    )
    try:
        cursor.execute(sql,value_tup)
        cursor.execute(sql_comments, value_tup_comments)
        db.commit()
    except:
        print('数据库写入失败')
    return

#关闭数据库
def close_sql():
    db.close()
