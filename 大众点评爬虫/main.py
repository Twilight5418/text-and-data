# main.py
import requests
from bs4 import BeautifulSoup
import time, random
import re
from fake_useragent import UserAgent
import os
import uuid
import mysqls
from mysqls import  create_table,close_sql

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

# 构造每一页的url，并且对爬取的信息进行存储
def getCommentinfo(shop_url, shopID, page_begin, page_end, cursor, db):
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
                mysqls.save_data(cursor, info, db)
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
        mysqls.generate_wordcloud_and_save(cursor, comments, shopID, db)

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
    db = mysqls.connect_db()
    cursor = db.cursor()
    getCommentinfo(shop_url, shopID, page_begin=nowpage+1, page_end=page+1, cursor=cursor, db=db)
    mysqls.close_sql(cursor, db)
    return

if __name__ == "__main__":
    db = mysqls.connect_db()
    cursor = db.cursor()
    create_table(cursor)
    craw_comment()
    close_sql(cursor, db)
