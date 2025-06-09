from bs4 import BeautifulSoup
import re
import urllib.request,urllib.error
import xlwt
import sqlite3

def main():
    # 1.爬取网页
    # 2.解析数据
    # 3.保存数据
    baseurl="https://movie.douban.com/top250?start="
    dataList=getData(baseurl)
    # print(dataList)
    # savePath="豆瓣电影Top250.xls"
    # saveData(dataList,savePath)
    dbPath="doubanmovie250.db"
    saveDataDB(dbPath,dataList)

#获得指定的URL里的内容
def askURL(url):
    #模拟头部信息
    header={"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"}
    request=urllib.request.Request(url=url,headers=header)
    html=""
    #在访问的时候添加异常捕获保证程序运行不会卡住
    try:
        html=urllib.request.urlopen(request)
        # print(html.read().decode("utf-8"))
    except urllib.error.URLError as e:
        if hasattr(e,"code"):#这个函数是如果错误存在于code，打印code
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html

#定义找到url的正则表达式规则
#注：如果正则表达式中有 括号 ()，它会返回匹配的组（group）内容，也就是括号中的那一部分，而不是整个匹配字符串
#影片详情连接
findLink=re.compile('<a href="(.*?)">')
#图片链接
findImgSrc=re.compile('<img.*src="(.*?)"',re.S)#re.S可以让换行符包含在字符中
#影片片名
findTitle=re.compile(r'<span class="title">(.*?)</span>',re.S)
#影片平分
findRating=re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>',re.S)
#评价人数
findJudge=re.compile(r'<span>(\d*)人评价</span>')
#找到概况
findInfo=re.compile(r'<p class="quote">\s*<span>(.*)</span>',re.S)#\s*空格，换行符，tap都可
#找到相关内容
findBd=re.compile(r'<div class="bd">\s*<p>(.*?)</p>',re.S)

def getData(baseurl):
    datalist=[]

    #使用for循环进行对每一个页面的访问
    for i in range(0,10):
        url =baseurl+str(i*25)
        print(url)
        html=askURL(url)
        # 2.逐一解析
        soup=BeautifulSoup(html,"html.parser")
        for item in soup.find_all("div",attrs={"class":"item"}):
            # print(item)
            #我的第一思路是，使用find_all找到各种信息后再转成字符串存下来
            #但其实找到整体后可以转成字符串变成文本，用正则表达式提取，这样思路比较清晰
            #第一思路可能要用到很多特别api
            data = []  # 保存信息
            item=str(item)
            #url
            link = re.findall(findLink,item)[0]
            data.append(link)
            #图片
            pic=re.findall(findImgSrc,item)[0]
            data.append(pic)
            #片名
            title=re.findall(findTitle,item)
            if(len(title)==2):
                ctitle=title[0] #添加中文名
                data.append(ctitle)
                otitle=title[1].replace("/","") #添加外文名，并且去掉/
                data.append(otitle)
            else:
                data.append(title[0])
                data.append(' ')#没有外文名的情况下留空

            rating=re.findall(findRating,item)[0]
            data.append(rating)

            judgeNum=re.findall(findJudge,item)[0]
            data.append(judgeNum)

            info=re.findall(findInfo,item)
            #处理概述可能不存在的情况
            if len(info)!=0:
                info=info[0].replace('。','') #去掉句号
                data.append(info)
            else:
                data.append(" ")#没有概述留空

            bd=re.findall(findBd,item)[0]
            bd=re.sub('<br(\s+)?/>(\s+)?'," ",bd)
            data.append(bd.strip())#去掉空格

            datalist.append(data)
    # print(datalist)
    # print(len(datalist))
    return datalist

def saveData(dataList,savePath):
    print("调用保存到xlwt")
    book = xlwt.Workbook(encoding='utf-8',style_compression=0)  # 创建workbook大对象
    sheet = book.add_sheet('豆瓣电影Top250',cell_overwrite_ok=True)  # 创建工作表
    col=("电影详情链接","图片链接","影片中文名","影片外国名","评分","评价数","概况","相关信息")
    for i in range(0,8):
        sheet.write(0,i,col[i]) #写入列名
    for i in range(0,250):
        print("第%d条" %(i+1))
        data=dataList[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j]) #写入数据

    book.save(savePath)

def saveDataDB(dbPath,dataList):
    print("调用保存到数据库中")
    initDB(dbPath)
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    for data in dataList:
        for index in range(len(data)):
            if index==4 or index==5:
                continue
            data[index]='"'+data[index]+'"'
        # sql='''
        #     insert into movie250
        #     (info_link, pic_url, cname, ename, score, rated, instroduction, info)
        #     values(%s)''' %",".join(data) #join将八个值用,连接到一起
        sql = '''
                    insert into movie250
                    (info_link, pic_url, cname, ename, score, rated, instroduction, info)
                    values(?,?,?,?,?,?,?,?)'''
        cursor.execute(sql,data)#可以使用这种方法，比视频里的简单，不需要拼接
        conn.commit()
    cursor.close()
    conn.close()

def initDB(dbPath):
    sql = '''
        create table movie250
        (
        id integer primary key autoincrement,
        info_link text,
        pic_url text,
        cname varchar,
        ename varchar,
        score numeric,
        rated numeric,
        instroduction text,
        info text
        )
        '''
    conn=sqlite3.connect(dbPath)
    cursor=conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
    # initDB("movietest.db")
    print("爬取完毕！")
