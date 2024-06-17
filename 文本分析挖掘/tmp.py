import pandas as pd
from matplotlib import pyplot as plt
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import roc_auc_score, f1_score, confusion_matrix
from imblearn.over_sampling import SMOTE

# 读取数据
data = pd.read_csv('data.csv')

# 构建label值
def zhuanhuan(score):
    if score > 3:
        return 1
    elif score < 3:
        return 0
    else:
        return None

# 特征值转换
data['target'] = data['stars'].map(lambda x: zhuanhuan(x))
data_model = data.dropna()

# 切分测试集、训练集
x_train, x_test, y_train, y_test = train_test_split(data_model['cus_comment'], data_model['target'], random_state=3, test_size=0.25)

# 引入停用词
infile = open("stopwords.txt", encoding='utf-8')
stopwords_lst = infile.readlines()
stopwords = [x.strip() for x in stopwords_lst]

# 中文分词
def fenci(train_data):
    words_df = train_data.apply(lambda x: ' '.join(jieba.cut(x)))
    return words_df

x_train = fenci(x_train)
x_test = fenci(x_test)

# 使用TF-IDF进行文本转向量处理
tv = TfidfVectorizer(stop_words=stopwords, max_features=3000, ngram_range=(1,2))
x_train_vec = tv.fit_transform(x_train)
x_test_vec = tv.transform(x_test)

# 检查训练集中每个类别的样本数
print(y_train.value_counts())

# 设置 k_neighbors 为 1
oversampler = SMOTE(random_state=0, k_neighbors=1)
x_resampled, y_resampled = oversampler.fit_resample(x_train_vec, y_train)

# 训练朴素贝叶斯分类器
clf = MultinomialNB()
clf.fit(x_resampled, y_resampled)

# 测试分类器
y_pred = clf.predict_proba(x_test_vec)[:, 1]
print("ROC AUC Score:", roc_auc_score(y_test, y_pred))

# 混淆矩阵
y_predict = clf.predict(x_test_vec)
cm = confusion_matrix(y_test, y_predict)
print("Confusion Matrix:\n", cm)

# 计算一条评论的情感评分
def ceshi(model, strings):
    strings_fenci = fenci(pd.Series([strings]))
    return float(model.predict_proba(tv.transform(strings_fenci))[:, 1])

# 测试评论
test1 = '很好吃，环境好，所有员工的态度都很好，上菜快，服务也很好，味道好吃，都是用蒸馏水煮的，推荐，超好吃' # 5星好评
test2 = '糯米外皮不绵滑，豆沙馅粗躁，没有香甜味。12元一碗不值。' # 1星差评
print('好评实例的模型预测情感得分为{}\n差评实例的模型预测情感得分为{}'.format(ceshi(clf, test1), ceshi(clf, test2)))
