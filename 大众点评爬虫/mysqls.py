# mysqls.py
import pymysql
import joblib
import jieba
import pandas as pd
import uuid
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sqlalchemy import create_engine

# 加载模型和停用词
tv2 = joblib.load(
    r"C:\Users\17662\Desktop\数据库\dianping_textmining\数据库\评论爬取\文本分析挖掘\tfidf_vectorizer.pkl")
clf = joblib.load(
    r"C:\Users\17662\Desktop\数据库\dianping_textmining\数据库\评论爬取\文本分析挖掘\naive_bayes_model.pkl")

infile = open(r"C:\Users\17662\Desktop\数据库\text-and-data\大众点评爬虫\stopwords.txt", encoding='utf-8')
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
            flavor VARCHAR(55),
            environment VARCHAR(55),
            service VARCHAR(55),
            shop_id VARCHAR(55)
            );'''
    cursor.execute(sql)
    print("Table DZDP created successfully")

    cursor.execute("DROP TABLE IF EXISTS Comments")
    sql = '''CREATE TABLE Comments (
            comment_id VARCHAR(100) PRIMARY KEY,
            app_id VARCHAR(100),
            comment_text TEXT,
            flavor VARCHAR(55),
            environment VARCHAR(55),
            service VARCHAR(55),
            rating VARCHAR(55),
            user_id VARCHAR(100),
            shop_id VARCHAR(55),
            comment_date VARCHAR(55),
            sentiment_score VARCHAR(55)
        );'''
    cursor.execute(sql)
    print("Table Comments created successfully")

    cursor.execute("DROP TABLE IF EXISTS CommentStats")
    sql = '''CREATE TABLE CommentStats(
                user_id VARCHAR(100) PRIMARY KEY,
                comment_count INT
                );'''
    cursor.execute(sql)
    print("Table CommentStats created successfully")

    cursor.execute("DROP TABLE IF EXISTS CommentWords")
    sql = '''CREATE TABLE CommentWords(
                shop_id VARCHAR(55),
                word VARCHAR(255),
                frequency FLOAT
                );'''
    cursor.execute(sql)
    print("Table CommentWords created successfully")


def save_data(cursor, data_dict, db):
    # 获取评论内容
    comment_text = data_dict['cus_comment']
    # 调用情感分析函数获取评分
    sentiment_score = fenxi(comment_text)

    sql_dzdp = '''INSERT INTO DZDP(cus_id, comment_time, comment_star, cus_comment, flavor, environment, service, shop_id) 
                  VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'''
    value_tup_dzdp = (
        data_dict['cus_id'],
        data_dict['comment_time'],
        data_dict['comment_star'],
        data_dict['cus_comment'],
        data_dict['flavor'],
        data_dict['environment'],
        data_dict['service'],
        data_dict['shop_id']
    )

    sql_comments = '''INSERT INTO Comments(comment_id, app_id, comment_text, flavor, environment, service, rating, user_id, shop_id, comment_date, sentiment_score) 
                      VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    value_tup_comments = (
        data_dict['comment_id'],  # 评论id
        25,  # 默认应用id
        data_dict['cus_comment'],  # 评论内容
        data_dict['flavor'],  # 口味
        data_dict['environment'],  # 环境
        data_dict['service'],  # 服务
        data_dict['comment_star'],  # 评分
        data_dict['cus_id'],  # 评论用户id
        data_dict['shop_id'],  # 商店id
        data_dict['comment_time'],  # 评论日期
        sentiment_score  # 情感评分
    )

    sql_update_statistics = '''INSERT INTO CommentStats (user_id, comment_count)
                               VALUES (%s, 1)
                               ON DUPLICATE KEY UPDATE comment_count = comment_count + 1'''
    value_tup_statistics = (data_dict['cus_id'],)

    try:
        cursor.execute(sql_dzdp, value_tup_dzdp)
        cursor.execute(sql_comments, value_tup_comments)
        cursor.execute(sql_update_statistics, value_tup_statistics)
        db.commit()
    except Exception as e:
        db.rollback()
        print('Failed to write to database:', e)
    return


def generate_wordcloud_and_save(cursor, texts, shop_id, db):
    text = ' '.join(texts)
    wc = WordCloud(font_path="msyh.ttc", background_color='white', max_words=100, stopwords=stopwords,
                   max_font_size=80, random_state=42, margin=3).generate(text)

    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()

    word_freq = wc.words_
    for word, freq in word_freq.items():
        sql_word = '''INSERT INTO CommentWords(shop_id, word, frequency) VALUES(%s, %s, %s)'''
        cursor.execute(sql_word, (shop_id, word, freq))
    db.commit()


def close_sql(cursor, db):
    cursor.close()
    db.close()
