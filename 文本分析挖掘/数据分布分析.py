import os
import pandas as pd
import joblib
import jieba
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from wordcloud import WordCloud
from sqlalchemy import create_engine
from PIL import Image

# 获取图片保存路径
image_dir = os.getenv('IMAGE_DIR', '.')
print(f"Image directory: {image_dir}")

# 设置模型和数据文件的绝对路径
base_dir = r'C:\Users\17662\Desktop\数据库\text-and-data\文本分析挖掘'
tfidf_vectorizer_path = os.path.join(base_dir, 'tfidf_vectorizer.pkl')
naive_bayes_model_path = os.path.join(base_dir, 'naive_bayes_model.pkl')
stopwords_path = os.path.join(base_dir, 'stopwords.txt')

def ciyun(shop_ID='all', filename='ph5.png'):
    texts = data['cus_comment']

    if shop_ID == 'all':
        text = ' '.join(texts)
    else:
        text = ' '.join(texts[data['shop_id'] == shop_ID])

    wc = WordCloud(font_path="msyh.ttc", background_color='white', max_words=100, stopwords=stopwords,
                   max_font_size=80, random_state=42, margin=3)
    wc.generate(text)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(os.path.join(image_dir, filename))
    plt.close()
    print(f"Word cloud saved as {filename}")

# 加载模型
print(f"Loading tfidf_vectorizer from {tfidf_vectorizer_path}")
tv2 = joblib.load(tfidf_vectorizer_path)
print(f"Loading naive_bayes_model from {naive_bayes_model_path}")
clf = joblib.load(naive_bayes_model_path)

# 加载停用词
print(f"Loading stopwords from {stopwords_path}")
infile = open(stopwords_path, encoding='utf-8')
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

try:
    # 创建数据库连接
    print("Connecting to database")
    engine = create_engine("mysql+pymysql://root:5457hzcx@localhost/TESTDB")

    # 读取数据
    sql = "SELECT * FROM dzdp;"
    data = pd.read_sql(sql, engine)
    print("Data loaded from database")

    # 关闭数据库连接
    engine.dispose()

    data['comment_star'].value_counts()
    # 数据清洗
    data.loc[data['comment_star'] == 'sml-str1', 'comment_star'] = 'sml-str10'
    data['stars'] = data['comment_star'].str.findall(r'\d+').str.get(0)
    data['stars'] = data['stars'].astype(float) / 10

    # 检查数据类型
    print(data.dtypes)

    # 绘制并保存图表
    plt.figure(figsize=(10, 6))
    sns.countplot(data=data, x='stars')
    plt.title('Distribution of Stars')
    plt.xlabel('Stars')
    plt.ylabel('Count')
    plt.savefig(os.path.join(image_dir, 'ph1.png'))
    plt.close()
    print("ph1.png saved")

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=data, x='shop_id', y='comment_star')
    plt.savefig(os.path.join(image_dir, 'ph2.png'))
    plt.close()
    print("ph2.png saved")

    # 时间提取
    data.comment_time = pd.to_datetime(data.comment_time.str.findall(r'\d{4}-\d{2}-\d{2} .+').str.get(0))
    data['year'] = data.comment_time.dt.year
    data['month'] = data.comment_time.dt.month
    data['weekday'] = data.comment_time.dt.weekday
    data['hour'] = data.comment_time.dt.hour

    # 检查数据类型和内容
    print(data[['hour', 'weekday']].head())

    # 绘制并保存各星期的小时评论数分布图
    fig1, ax1 = plt.subplots(figsize=(14, 4))
    df = data.groupby(['hour', 'weekday']).count()['cus_id'].unstack()

    # 确认数据为数值类型
    print(df.dtypes)

    df.plot(ax=ax1, style='-.')
    plt.savefig(os.path.join(image_dir, 'ph3.png'))
    plt.close()
    print("ph3.png saved")

    # 绘制并保存评论的长短与评分关系图
    data['comment_len'] = data['cus_comment'].str.len()
    fig2, ax2 = plt.subplots()
    sns.boxplot(x='stars', y='comment_len', data=data, ax=ax2)
    ax2.set_ylim(0, 600)
    plt.savefig(os.path.join(image_dir, 'ph4.png'))
    plt.close()
    print("ph4.png saved")

    # 除去非文本数据和无意义文本
    data['cus_comment'] = data['cus_comment'].str.replace(r'[^\u4e00-\u9fa5]', '').str.replace('收起评论', '')
    data['cus_comment'] = data['cus_comment'].apply(lambda x: ' '.join(jieba.cut(x)))
    data['cus_comment'].head()

    matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
    matplotlib.rcParams['font.serif'] = ['KaiTi']

    # 绘制并保存词云
    ciyun('521698', 'ph5.png')

    # 评论情感分析
    test_comment = '糯米外皮不绵滑，豆沙馅粗躁，没有香甜味。12元一碗不值。'
    print(fenxi(test_comment))
except Exception as e:
    print(f"An error occurred: {e}")
