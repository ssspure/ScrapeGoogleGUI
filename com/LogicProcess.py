import os
from PyQt5.QtWidgets import QMessageBox, QApplication
import requests
from bs4 import BeautifulSoup
import time
import re
import datetime
import xlsxwriter
from com.ManageDB import ManageDB
import smtplib
from com.BaseException import BaseException


def initialProcess(ui):
    # 清空运行状态信息
    ui.stateText.clear()

    # 输入值的Check
    # 获取产品值
    productList = ui.productText.text()
    # 获取评分的值
    rating = ui.rateText.text()
    # 获取谷歌地址的值
    googleUrl = ui.googleURLText.text()
    # 获取亚马逊地址的值
    amazonUrl = ui.amazonURLText.text()
    # 获取间隔时间的值
    interval = ui.intervalText.text()
    # 获取结果文件保存路径的值
    resultFilePath = ui.resultText.text()

    # 输入值Check
    result = inputCheck(ui, productList, rating, googleUrl, amazonUrl, interval, resultFilePath)

    return result


def inputCheck(ui, productList, rating, googleUrl, amazonUrl, interval, resultFilePath):
    """各个项目输入值得Check
    :param ui: 界面
    :param productList: 产品名称
    :param rating: 评分
    :param googleUrl: 谷歌地址
    :param amazonUrl: 亚马逊地址
    :param interval: 间隔时间
    :param resultFilePath: 结果文件保存路径
    :return:
    """
    # 产品空值Check
    if productList.strip() == "":
        # self.productText
        warnPrompt(ui, ui.productText, "产品不能为空!!!")
        return False

    if productList.find("，") > 0:
        warnPrompt(ui, ui.productText, "多个产品的情况下，各个产品之间\n必须使用英文状态的逗号!!!")
        return False


    # 评分空值Check
    if rating.strip() == "":
        # self.productText
        warnPrompt(ui, ui.rateText, "评分不能为空!!!")
        return False


    # 评分Check是否为数字
    try:
        rating = float(rating)
    except ValueError as e:
        warnPrompt(ui, ui.rateText, "评分只能为数字!!!")
        return False


    # 谷歌地址不能为空
    if googleUrl.strip() == "":
        # self.productText
        warnPrompt(ui, ui.googleURLText, "谷歌地址不能为空!!!")
        return False


    # 亚马逊地址不能为空
    if amazonUrl.strip() == "":
        # self.productText
        warnPrompt(ui, ui.amazonURLText, "亚马逊地址不能为空!!!")
        return False


    # 间隔时间空值Check
    if interval.strip() == "":
        # self.productText
        warnPrompt(ui, ui.intervalText, "间隔时间不能为空!!!")
        return False

    # 间隔时间Check是否为数字
    try:
        interval = float(interval)
    except ValueError as e:
        warnPrompt(ui, ui.intervalText, "间隔时间只能为数字!!!")
        return False

    # 间隔时间大小Check
    if interval <= 15:
        result = QMessageBox.question(ui, "间隔时间大小确认", "建议您将间隔时间设置为大于15的值,否则可能"
                                             "\n会被谷歌屏蔽,是否重新设置间隔时间?\nYes:重新设置间隔时间\nNo:使用现在的间隔时间搜索数据",
                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if result == QMessageBox.Yes:
            ui.intervalText.setFocus()
            return False
        else:
            pass


    # 结果文件保存路径空值Check
    if resultFilePath.strip() == "":
        # self.productText
        warnPrompt(ui, ui.resultText, "结果文件保存路径不能为空!!!")
        return False

    return True



def runProcess(thread, ui):
    """执行程序按钮对应的处理，获取UI中的值，然后对搜索结果进行爬取
    :param ui:界面对象
    :return:None
    """

    # 获取产品值
    productList = ui.productText.text()
    # 获取评分的值
    rating = ui.rateText.text()
    # 获取谷歌地址的值
    googleUrl = ui.googleURLText.text()
    # 获取亚马逊地址的值
    amazonUrl = ui.amazonURLText.text()
    # 获取间隔时间的值
    interval = ui.intervalText.text()
    # 获取结果文件保存路径的值
    resultFilePath = ui.resultText.text()

    # 执行搜索处理
    searchData(thread, productList, rating, googleUrl, amazonUrl, float(interval), resultFilePath)


def searchData(thread, productList, rating, googleUrl, amazonUrl, interval, resultFilePath):
    """搜索主处理
    :param productList: 产品名称
    :param rating: 评分
    :param googleUrl: 谷歌地址
    :param amazonUrl: 亚马逊地址
    :param interval: 间隔时间
    :param resultFilePath: 结果文件保存路径
    :return:
    """
    # 获取程序开始执行的时间
    starttime = datetime.datetime.now()
    thread._singal.emit("程序开始执行!!!")

    # 产品列表
    products = []
    # 判断产品列表中是否还有逗号
    if productList.find(",") > 0:
        products = productList.split(",")
    else:
        products.append(productList)

    dic = {}

    for product in products:
        datas = []
        try:
            i = 0
            while True:
                thread._singal.emit("开始获取{}产品第{}页数据!!!".format(product, str(i+1)))
                results, nextPage = scrape_google(thread, product, 100, i*100, rating, googleUrl, amazonUrl)

                for result in results:
                    datas.append(result)

                thread._singal.emit("{}产品第{}页数据获取完了!!!".format(product, str(i + 1)))

                # 如果不存在下一页的
                if nextPage is None:
                    break
                else:
                    time.sleep(interval)
                    i = i + 1

            dic[product] = datas

        except BaseException as e:
            return
        except Exception as e:
            thread._singal.emit(str(e))
            thread.scrapeEndPrompt.emit(str(e))
            return

    thread._singal.emit("所有数据获取完毕，开始生成结果文件!!!")
    writeToExcel(dic, resultFilePath)
    thread._singal.emit("结果文件生成完毕!!!")
    thread.scrapeEndPrompt.emit("")

    # 获取程序执行结束的时间
    endtime = datetime.datetime.now()
    intervalTime = endtime - starttime
    minute = (intervalTime.seconds) // 60
    seconds = (intervalTime.seconds) % 60
    thread._singal.emit("程序共运行{}分{}秒".format(str(minute), str(seconds)))


def writeToExcel(dic, resultFilePath):

    nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')

    contactProName = ""
    for key in dic.keys():
        contactProName = contactProName + "_" + "[" + key + "]"

    filename = nowTime + contactProName

    if not os.path.exists(resultFilePath):
        os.makedirs(resultFilePath)

    workbook = xlsxwriter.Workbook(os.path.abspath(resultFilePath) + os.sep + filename + ".xlsx")

    for key, datas in dic.items():
        worksheet = workbook.add_worksheet(key)

        row = 0
        worksheet.write(row, 0, "网址")
        worksheet.write(row, 1, "评分")
        worksheet.write(row, 2, "标题")

        row = row + 1

        for data in datas:
            worksheet.write(row, 0, data.get("link"))
            worksheet.write(row, 1, data.get("rating"))
            worksheet.write(row, 2, data.get("title"))
            row = row + 1


def parse_results(html, keyword, google_url, baseRating):

    pattern = re.compile(r"[\d\.]+")

    soup = BeautifulSoup(html, 'html.parser')

    nextPage = soup.find(id="pnnext")

    found_results = []

    result_block = soup.find_all('div', attrs={'class': 'g'})
    for result in result_block:

        link = result.find('a', href=True)
        rating = result.find('div', attrs={'class': 'slp f'})
        title = result.find('h3', attrs={'class': 'r'})

        if link and rating:
            link = link['href']
            rating = str(rating.get_text())
            title = title.get_text()

            if rating.strip() != "":
                rating = pattern.findall(rating)[0]
                if float(rating) > baseRating:
                    if link != '#':
                        found_results.append({"google_url": google_url, 'keyword': keyword,
                                              'link': link, 'rating': rating, 'title': title})
    return found_results, nextPage


def fetch_results(search_term, number_results, start, rating, googleUrl, amazonUrl):
    USER_AGENT = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

    escaped_search_term = search_term.replace(' ', '+')

    google_url = '{}/search?q=site:{}+{}+currently+unavailable&num={}&start={}'\
        .format(googleUrl, amazonUrl, escaped_search_term, number_results, start)
    response = requests.get(google_url,headers=USER_AGENT)
    response.raise_for_status()

    return search_term, response.text, google_url


def scrape_google(thread, search_term, number_results, start, rating, googleUrl, amazonUrl):
    try:
        results = []
        nextPage = None
        keyword, html, google_url = fetch_results(search_term, number_results, start, rating, googleUrl, amazonUrl)
        results, nextPage = parse_results(html, keyword, google_url, float(rating))
        return results, nextPage
    except AssertionError:
        raise Exception("Incorrect arguments parsed to function")
    except requests.HTTPError:
        thread._singal.emit("您现在已经被谷歌屏蔽,请稍后再尝试运行程序!!!")
        thread.scrapeEndPrompt.emit("您现在已经被谷歌屏蔽,请稍后再尝试运行程序!!!$True")
        raise BaseException("")
    except requests.RequestException:
        thread._singal.emit("您的网络连接出现问题,请检查您的网络!!!")
        thread.scrapeEndPrompt.emit("您的网络连接出现问题,请检查您的网络!!!$True")
        raise BaseException("")




def setStatus(ui, message):
    """设置执行状态信息
    :param widget:执行状态文本框
    :param message:状态信息
    :return:
    """
    ui.stateText.append(message)
    QApplication.processEvents()


def warnPrompt(ui, widget, message):
    """输入值check不满足条件的时候，弹出对话框
    :param ui:
    :param widget:
    :param message:
    :return:
    """
    QMessageBox.warning(ui, "", message)
    widget.setFocus()


def setUIInitialValue(ui):
    """从info表中读取值,给界面设置初始值
    :param ui:界面对象
    :return:None
    """

    dbFile = os.path.join(ui.path, "system.db")

    db = ManageDB(dbFile)

    datas = db.selectFromInfo()

    # 设置产品的值
    ui.productText.setText(datas["products"])
    # 设置评分的值
    ui.rateText.setText(datas["rating"])
    # 设置谷歌地址的值
    ui.googleURLText.setText(datas["googleUrl"])
    # 设置亚马逊地址的值
    ui.amazonURLText.setText(datas["amazonUrl"])
    # 设置时间间隔的值
    ui.intervalText.setText(datas["interval"])
    # 设置结果文件保存路径的值
    ui.resultText.setText(datas["resultFilePath"])

    db.close()


def saveData(ui):
    """将UI中的数据保存到info.properties中
    :param ui:
    :return:
    """
    # 获取产品值
    productList = ui.productText.text()
    # 获取评分的值
    rating = ui.rateText.text()
    # 获取谷歌地址的值
    googleUrl = ui.googleURLText.text()
    # 获取亚马逊地址的值
    amazonUrl = ui.amazonURLText.text()
    # 获取间隔时间的值
    interval = ui.intervalText.text()
    # 获取结果文件保存路径的值
    resultFilePath = ui.resultText.text()

    dbFile = os.path.join(ui.path, "system.db")

    db = ManageDB(dbFile)

    datas = {}

    datas["products"] = productList
    datas["rating"] = rating
    datas["googleUrl"] = googleUrl
    datas["amazonUrl"] = amazonUrl
    datas["interval"] = interval
    datas["resultFilePath"] = resultFilePath

    db.updateInfo(datas)

    db.close()

    QMessageBox.about(ui, "提示", "数据保存完毕!!!")


def openResultFolder(ui):
    # 打开文件夹尽在Windows系统下有效
    os.system("start explorer " + ui.resultText.text())


def sendMail(errMsg):
    fromaddr = "ssspure@qq.com"
    toaddrs = "ssspure@gmail.com"
    subject = "ScrapeGoogleGUI Error Message"

    # Add the From: To: and Subject: headers at the start!
    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
           % (fromaddr, toaddrs, subject))

    msg = msg + "Error Message:\n" + errMsg

    server = smtplib.SMTP_SSL('smtp.qq.com')
    # 如果是其他的服务，只需要更改 host 为对应地址，port 对对应端口即可
    # server = smtplib.SMTP_SSL(host='smtp.qq.com', port=465)
    # server.set_debuglevel(1)    # 开启调试，会打印调试信息#
    username = "ssspure@qq.com"
    password = "plmokn321."
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()