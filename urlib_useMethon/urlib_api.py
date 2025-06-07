# -*- coding: utf-8 -*-
# @Time: 2025/6/7 18:12
# @Author: 醋汁
# @Email: 2727913856@qq.com
# @File: urlib_api.py
# @Software: PyCharm

import urllib.request
from datetime import datetime
from http.client import responses

#urllib.request.urlopen打开网址获得数据，这是获取一个get请求
#response自动被设置成函数返回的对象
response=urllib.request.urlopen("http://www.baidu.com")
#response.read()获取数据,decode("utf-8")解码形成html的格式
print(response.read().decode("utf-8"))
#注：urllib.error.HTTPError: HTTP Error 418: ）418出现这样的报错信息说明被反爬拦截了

import urllib.parse
#获取一个post请求，post需要提交表单数据,这里一般是模拟用户登录
#在urllib.request.urlopen中可以添加第二个参数data= 来设置，内容的类型需要bytes类型
date=bytes(urllib.parse.urlencode({"date":datetime.today().strftime("%Y/%m/%d")}),encoding="utf-8")
response=urllib.request.urlopen("http://httpbin.org/post",date)
print(response.read().decode("utf-8"))

# 正常访问时，返回的用户代理会很明显的时python爬虫，需要添加超时参数以免网站反爬卡死你的程序
response=urllib.request.urlopen("http://httpbin.org/get",timeout=1)
print(response.read().decode("utf-8"))

#另外，如果timeout设置时间过短，可以设置一个异常处理
try:
    response=urllib.request.urlopen("http://httpbin.org/get",timeout=0.01)
    print(response.read().decode("utf-8"))
except TimeoutError as e:
    print("timeout")

#通过response对象来获取请求的一些信息
response=urllib.request.urlopen("http://www.baidu.com",timeout=1)
#状态码
print(response.status)
#头部信息
print(response.getheaders())
#print(response.getheader("键"))可以获取对应的值,注意函数名，getheaders和getheader
print(response.getheader('Server'))

