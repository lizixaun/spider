# -*- codeing =utf-8 -*-
# @Time:2023/12/20 9:24
# @Author:李子煊
# @File：app.py
# @sofyware:PyCharm
from urllib.request import urlopen
url="http://www.baidu.com"
resp=urlopen(url)
print(resp.read().decode("utf-8"))
with open("baidu.html",mode="w") as f:
    f.write(resp.read().decode("utf-8"))
print("over")