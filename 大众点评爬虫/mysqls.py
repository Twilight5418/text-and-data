# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 15:45:05 2018

@author: bin
"""

import pymysql


# 在数据库中创建表
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

    cursor.execute("DROP TABLE IF EXISTS 评论")
    sql = '''CREATE TABLE 评论 (
            评论id INT AUTO_INCREMENT PRIMARY KEY,
            应用id VARCHAR(100),
            评论内容 TEXT,
            口味 VARCHAR(55),
            环境 VARCHAR(55),
            服务 VARCHAR(55),
            评分 VARCHAR(55),
            评论用户id VARCHAR(100),
            商店id VARCHAR(55),
            评论日期 VARCHAR(55)
        );'''
    cursor.execute(sql)

    cursor.execute("DROP TABLE IF EXISTS 评论统计")
    sql = '''CREATE TABLE 评论统计(
                评论用户id VARCHAR(100) PRIMARY KEY,
                评论数  INT
                );'''
    cursor.execute(sql)

    # 连接MYSQL数据库
db = pymysql.connect(
    host="localhost",
    user="root",
    password="5457hzcx",
    database="TESTDB",
    charset='utf8mb4',
    connect_timeout=10,  # 连接超时
    read_timeout=300,    # 读取超时
    write_timeout=300    # 写入超时
)
cursor = db.cursor()


# 存储爬取到的数据
def save_data(data_dict):
    """
    将爬取的数据保存到DZDP和评论表中，并更新评论统计表。
    """
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

    sql_comments = '''INSERT INTO 评论(应用id, 评论内容, 口味, 环境, 服务, 评分, 评论用户id, 商店id, 评论日期) 
                      VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    value_tup_comments = (
        25,  # 默认应用id
        data_dict['cus_comment'],  # 评论内容
        data_dict['kouwei'],  # 口味
        data_dict['huanjing'],  # 环境
        data_dict['fuwu'],  # 服务
        data_dict['comment_star'],  # 评分
        data_dict['cus_id'],  # 评论用户id
        data_dict['shopID'],  # 商店id
        data_dict['comment_time']  # 评论日期
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


# 关闭数据库
def close_sql():
    """
    关闭数据库连接。
    """
    cursor.close()
    db.close()




