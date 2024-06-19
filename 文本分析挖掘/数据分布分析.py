#引入库
import pandas as pd
import pymysql
import joblib
import jieba
import seaborn as sns
import numpy as np #导入模块numpy，多维数组
import matplotlib.pyplot as plt #导入模块matplotlib，作图
import matplotlib
from sklearn.naive_bayes import MultinomialNB
from wordcloud import WordCloud, STOPWORDS
from sqlalchemy import create_engine
from PIL import Image #导入模块PIL(Python Imaging Library)图像处理库


def ciyun(shop_ID='all'):#词云寻找
    texts = data['cus_comment']

    if shop_ID == 'all':
        text = ' '.join(texts)
    else:
        text = ' '.join(texts[data['shop_id'] == shop_ID])

    wc = WordCloud(font_path="msyh.ttc", background_color='white', max_words=100, stopwords=stopwords,
                   max_font_size=80, random_state=42, margin=3)  # 配置词云参数
    wc.generate(text)  # 生成词云
    plt.imshow(wc, interpolation="bilinear")  # 作图
    plt.axis("off")  # 不显示坐标轴

# 加载模型
tv2 = joblib.load('tfidf_vectorizer.pkl')
clf = joblib.load('naive_bayes_model.pkl')

# 加载停用词
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
# 创建数据库连接
engine = create_engine("mysql+pymysql://root:5457hzcx@localhost/TESTDB")

# 读取数据
sql = "SELECT * FROM dzdp;"
data = pd.read_sql(sql, engine)

# 关闭数据库连接
engine.dispose()

data['comment_star'].value_counts()
# 数据清洗
data.loc[data['comment_star'] == 'sml-str1', 'comment_star'] = 'sml-str10'
data['stars'] = data['comment_star'].str.findall(r'\d+').str.get(0)
data['stars'] = data['stars'].astype(float) / 10

# 绘制图表
plt.figure(figsize=(10, 6))
sns.countplot(data=data, x='stars')
plt.title('Distribution of Stars')
plt.xlabel('Stars')
plt.ylabel('Count')
plt.show()
sns.boxplot(data=data,x='shop_id',y='comment_star')
plt.show()

#时间提取
data.comment_time = pd.to_datetime(data.comment_time.str.findall(r'\d{4}-\d{2}-\d{2} .+').str.get(0))
data['year'] = data.comment_time.dt.year
data['month'] = data.comment_time.dt.month
data['weekday'] = data.comment_time.dt.weekday
data['hour'] = data.comment_time.dt.hour
# 绘制图表
# 各星期的小时评论数分布图
fig1, ax1=plt.subplots(figsize=(14,4))
df=data.groupby(['hour', 'weekday']).count()['cus_id'].unstack()
df.plot(ax=ax1, style='-.')
plt.show()
# 绘制图表
#评论的长短可以看出评论者的认真程度
data['comment_len'] = data['cus_comment'].str.len()
fig2, ax2=plt.subplots()
sns.boxplot(x='stars',y='comment_len',data=data, ax=ax2)
ax2.set_ylim(0,600)
plt.show()
#除去非文本数据和无意义文本
data['cus_comment'] = data['cus_comment'].str.replace(r'[^\u4e00-\u9fa5]','').str.replace('收起评论','')
data['cus_comment'] = data['cus_comment'].apply(lambda x:' '.join(jieba.cut(x)))
data['cus_comment'].head()

matplotlib.rcParams['font.sans-serif'] = ['KaiTi']#作图的中文
matplotlib.rcParams['font.serif'] = ['KaiTi']#作图的中文

infile = open("stopwords.txt",encoding='utf-8')
stopwords_lst = infile.readlines()
STOPWORDS = [x.strip() for x in stopwords_lst]
stopwords = set(STOPWORDS) #设置停用词
data['shop_id'].unique()
# 绘制图表
# 词云
ciyun('521698')
plt.show()


# 评论情感分析
test_comment = '糯米外皮不绵滑，豆沙馅粗躁，没有香甜味。12元一碗不值。'
print(fenxi(test_comment))