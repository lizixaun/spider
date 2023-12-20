# -*- codeing =utf-8 -*-
# @Time:2023/6/28 17:27
# @Author:李子煊
# @File：spider1.py
# @sofyware:PyCharm
# -*- codeing =utf-8 -*-
# @Time:2023/6/21 15:38
# @Author:李子煊
# @File：spider.py
# @sofyware:PyCharm
import re
import urllib.request,urllib.error
import sqlite3
from bs4 import BeautifulSoup
import xlwt

def main():
    baseurl="https://movie.douban.cdbanom/top250?start="
    #1.爬取网页
    datalist=getData(baseurl)
    savepath="豆瓣电影Top250.xls"
    #dpath="movie.db"
    #保存数据
    saveData(datalist,savepath)
    #saveData2DB(datalist,dpath)
    askURL("https://movie.douban.com/top250?start=")
#影片的详情链接规则
findLink=re.compile(r'<a href="(.*?)">')#创建正则表达式对象，表示规则（字符串模式）
#影片图片
findImgSrc=re.compile(r'<img.*src="(.*?)"',re.S)#re.s忽略换行符
#片名
findTitle=re.compile(r'<span class="title">(.*)</span>')
#影片评分
findRating=re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#评价人数
findJudge=re.compile(r'<span>(\d*)人评价</span>')
#找到概况
findInq=re.compile(r'<span class="inq">(.*)</span>')
#相关内容
findBd=re.compile(r'<p class="">(.*?)</p>',re.S)
#获取网页
def getData(baseurl):
    datalist=[]
    for i in range(0,10):#调用获取页面信息10次
        url=baseurl+str(i*25)#一共250条
        html=askURL(url)#保存获取到的页面源码
        #2.逐一解析
        soup=BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item"):
            #print(item)#测试查看电影全部信息
            data=[]#保存一部电影的全部信息
            item=str(item)


            #影片的详情链接
            link=re.findall(findLink,item)[0]#re库用来通过正则表达式查找指定的字符串，[0] 表示从匹配结果的列表中取第一个元素。因为 re.findall() 可能会返回多个匹配的结果
            data.append(link)#添加链接
            imgSrc=re.findall(findImgSrc,item)[0]
            data.append(imgSrc)#添加图片
            titles=re.findall(findTitle,item)#篇名可能只有一个中文名，没有外文名
            if(len(titles)==2):
                ctitle=titles[0]
                data.append(ctitle)#添加中文名字
                otitle=titles[1].replace("/","")#去掉无关的冒号
                data.append(otitle)#添加外国名
            else:
                data.append(titles[0])
                data.append(' ')#外文名留空
            rating=re.findall(findRating,item)[0]
            data.append(rating)#添加评分
            judgeNum=re.findall(findJudge,item)[0]
            data.append(judgeNum)#添加评价人数
            inq=re.findall(findInq,item)
            if len(inq)!=0:
                inq=inq[0].replace("。","")#去掉句号
                data.append(inq)#添加概述
            else:
                data.append(" ")#留空
            bd=re.findall(findBd,item)[0]
            bd=re.sub('<br(\s+)?/>(\s+)?',"",bd)#去掉<br/>
            bd=re.sub('/'," ",bd)#替换/
            data.append(bd.strip())#去掉前后空格
            datalist.append(data)#把处理好的电影信息放入datalist
    return datalist
#得到一个Url的网页内容
def askURL(url):
    # 设置请求头，模拟浏览器访问
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51"
    }
    # 构建请求对象
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        # 发送请求并获取响应
        response = urllib.request.urlopen(request)
        # 读取响应内容
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        # 网络请求异常处理
        if hasattr(e, "code"):
            print(e.code)  # 打印错误代码
        if hasattr(e, "reason"):
            print(e.reason)  # 打印错误原因

    return html
#保存数据
def saveData(datalist, savepath):
    # 输出保存信息
    print("save....")
    # 创建workbook对象，并指定编码和样式压缩效果
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    # 创建工作表，允许每个单元进行覆盖操作
    sheet = book.add_sheet('豆瓣电影top250', cell_overwrite_ok=True)
    # 定义表头列名
    col = ("电影详情链接", "图片链接", "影片中文名", "影片外国名", "评分", "评价数", "概况", "相关信息")
    # 写入表头列名
    for i in range(0, 8):
        sheet.write(0, i, col[i])
    # 写入数据
    for i in range(0, 250):
        print("第%d条" % (i + 1))
        data = datalist[i]
        for j in range(0, 8):
            sheet.write(i + 1, j, data[j])  # 数据
    # 保存文件
    book.save(savepath)
def saveData2DB(datalist, dbpath):
    """
    将数据保存到数据库中

    Args:
        datalist (list): 数据列表，包含多个电影的信息
        dbpath (str): 数据库文件路径

    Returns:
        None
    """

    # 创建数据库
    init_db(dbpath)

    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    # 遍历数据列表
    for data in datalist:
        # 处理每个电影的信息
        for index in range(len(data)):
            # 跳过索引为4和5的字段（score和rated）
            if index == 4 or index == 5:
                continue
            # 对数据的每个字段添加双引号
            data[index] = '"' + data[index] + '"'

        # 构建插入数据的SQL语句
        sql = '''
            insert into movie250(
            info_link, pic_link, cname, ename, score, rated, instroduction, info)
            values(%s)''' % ",".join(data)

        print(sql)
        # 执行插入操作
        cur.execute(sql)
        # 提交事务
        conn.commit()

    # 关闭游标和数据库连接
    cur.close()
    conn.commit()


def init_db(dbpath):
    """
    初始化数据库，创建数据表

    Args:
        dbpath (str): 数据库文件路径

    Returns:
        None
    """

    # 创建数据表的SQL语句
    sql = '''
        create table movie250
        (
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname varchar,
        ename varchar,
        score numeric,
        rated numeric,
        instroduction text,
        info text   
        )'''

    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    # 执行创建数据表的操作
    cursor.execute(sql)

    # 提交事务
    conn.commit()
    conn.close()
if __name__ == '__main__':      #当程序执行时
#调用函数
    main()
    #init_db("movietest.db")
    print("爬取完毕")

