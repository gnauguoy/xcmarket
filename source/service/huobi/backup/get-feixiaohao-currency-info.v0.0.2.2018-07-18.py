# final date: 2018-07-18 01:55
# desc: 此版本已经实现守护进程。
from urllib import request, parse
import json
import re
import sys
import traceback
import socket
import time
import datetime
import threading
try:
    import thread
except ImportError:
    import _thread as thread
import os
from chengutil import mysqlutil, util


def get_thirdpart_currency_info(fullname):

    url = 'not set'

    try:

        url = 'https://www.feixiaohao.com/currencies/%s/' % (fullname)
        print('url >>>', url)
        socket.setdefaulttimeout(10)
        response = request.urlopen(url)
        content = response.read().decode('utf-8')
        # print('content >>>', content[0:100])
        # print('==================================================')
        # print(content)
        # print('==================================================')

        # 获取缩小范围的内容
        matchObj = re.search(
            r'\<small\>.*?\<\/small\>.*换手率\<\/div\>', content, re.I)
        html = matchObj.group()
        # print(html)

        currency = {}

        # 获取人民币价格、涨幅
        matchObj = re.search(
            r'\<div class=coinprice\>(.*?)\<span class=tags-.*?>(.*?)</span>', html, re.I)
        price_cny = replace_punctuation(matchObj.group(1))
        # print('人民币价格       >>>', price_cny)
        price_scope = replace_punctuation(matchObj.group(2))
        # print('涨跌幅           >>>', price_scope)
        currency['price_cny'] = price_cny
        currency['price_scope'] = price_scope

        # 获取24H最高价
        matchObj = re.search(
            r'\<div\>24H最高\<span class=value\>(.*?)\<\/span\>', html, re.I)
        high = replace_punctuation(matchObj.group(1))
        # print('24H最高价        >>>', high)
        currency['high'] = high

        # 获取24H最低价
        matchObj = re.search(
            r'\<div\>24H最低\<span class=value\>(.*?)\<\/span\>', html, re.I)
        low = replace_punctuation(matchObj.group(1))
        # print('24H最低价        >>>', low)
        currency['low'] = low

        # 获取人民币流通市值，市值排名、美元市值、btc市值
        matchObj = re.search(
            r'\<div class=tit\>流通市值\<\/div\>.*?\<div class=value\>(?P<ccv>.*?)' +
            r'((\<span class=tag-marketcap\>(?P<r>.*?)\<\/span\>.*?)\<\/div\>|\<\/div\>).*?' +
            r'\<div class=sub\>≈(?P<cuv>.*?)\<\/div\>.*?' +
            r'\<div class=sub\>≈(?P<cbv>.*?)\<\/div\>', html, re.I)
        # print(matchObj.group())
        # print(matchObj.groupdict())
        matchDict = matchObj.groupdict()
        circulating_cny_value = replace_punctuation(matchDict['ccv'])
        # print('人民币流通市值   >>>', circulating_cny_value)
        ranking = replace_punctuation(matchDict['r'])
        # print('市值排名         >>>', ranking)
        circulating_usd_value = replace_punctuation(matchDict['cuv'])
        # print('美元市值         >>>', circulating_usd_value)
        circulating_btc_value = replace_punctuation(matchDict['cbv'])
        # print('btc市值          >>>', circulating_btc_value)
        currency['circulating_cny_value'] = circulating_cny_value
        currency['ranking'] = ranking
        currency['circulating_usd_value'] = circulating_usd_value
        currency['circulating_btc_value'] = circulating_btc_value

        # 获取全球总市值百分比
        matchObj = re.search(
            r'333\>+?(.*?)\<\/span\>\<br\>\s*占全球总市值', html, re.I)
        circulating_value_percent = replace_punctuation(matchObj.group(1))
        # print('全球总市值百分比 >>>', circulating_value_percent)
        currency['circulating_value_percent'] = circulating_value_percent

        # 获取流通量
        matchObj = re.search(
            r'\<div class=tit\>流通量\<\/div\>\<div class=value\>(.*?)\<\/div\>', html, re.I)
        circulating_volume = replace_punctuation(matchObj.group(1))
        # print('流通量           >>>', circulating_volume)
        currency['circulating_volume'] = circulating_volume

        # 获取总发行量
        matchObj = re.search(
            r'\<div class=tit\>总发行量\<\/div\>\<div class=value\>(.*?)\<\/div\>', html, re.I)
        total_volume = replace_punctuation(matchObj.group(1))
        # print('总发行量         >>>', total_volume)
        currency['total_volume'] = total_volume

        # 获取流通率
        matchObj = re.search(
            r'占全球总市值.*?333\>(.*?)\<\/span\>\<br\>\s*流通率', html, re.I)
        circulating_rate = replace_punctuation(matchObj.group(1))
        # print('流通率           >>>', circulating_rate)
        currency['circulating_rate'] = circulating_rate

        # 获取24H成交额、排名
        matchObj = re.search(
            r'\<div class=tit\>24H成交额\<\/div\>' +
            r'\<div class=value\>(?P<tv>.*?)(<span class=tag-vol>(?P<tvr>.*?)</span>\<\/div\>)|(\<\/div\>)', html, re.I)
        matchDict = matchObj.groupdict()
        turn_volume = replace_punctuation(matchDict['tv'])
        # print('24H成交额        >>>', turn_volume)
        turn_volume_ranking = replace_punctuation(matchDict['tvr'])
        # print('成交额排名       >>>', turn_volume_ranking)
        currency['turn_volume'] = turn_volume
        currency['turn_volume_ranking'] = turn_volume_ranking

        # 获取换手率
        matchObj = re.search(
            r'流通率.*?333\>(.*?)\<\/span\>\<br\>\s*换手率', html, re.I)
        turnover_rate = replace_punctuation(matchObj.group(1))
        # print('换手率           >>>', turnover_rate)
        currency['turnover_rate'] = turnover_rate

        # matchObj = re.search(r'', html, re.I)
        # var = matchObj.group(1)
        # print(var)

        # print(currency)
    except:
        print('\033[0;30;41m get_feixiaohao_currency_info except >>> \033[0m')
        filename = os.path.basename(sys.argv[0]).split(".")[0]
        util.printExcept(filename)
        return {}

    return currency


def replace_punctuation(str):

    if str == None:
        return 0
    # if str == '?':
    #     return 0

    # str = str.replace(' ', '')
    # str = str.replace('%', '')
    # str = str.replace('￥', '')
    # str = str.replace('¥', '')
    # str = str.replace('$', '')
    # str = str.replace(',', '')
    # str = str.replace('BTC', '')
    # str = str.replace('第', '')
    # str = str.replace('名', '')
    str = re.sub(r'[^-.0-9]', '', str)
    if str == '':
        return 0

    return str


# main 函数嵌套运行计数
mainNest = 0


def main(currencies=None):

    # 记录开始时间
    startDate = datetime.datetime.now()

    db = mysqlutil.init()
    cursor = db.cursor()

    # 记录获取失败的币种
    errorCurrencies = []

    global mainNest

    try:

        if currencies == None:

            # 重置嵌套值。currencies 为 None 表示 main 处于非嵌套运行的状态。
            mainNest = 0

            sql = 'SELECT * FROM xcm_vxn_currency'
            cursor.execute(sql)
            currencies = cursor.fetchall()

        if len(currencies) == 0:
            print(len(currencies))
            return

        # print(currencies)
        # ((1, 'btc', 'bitcoin', 'BTC,比特币', None),...)

        count = 0
        success = 0
        total = len(currencies)

        for c in currencies:

            if type(c) == str: # 嵌套获取出现错误的币种列表
                fullname = c
            else: # 获取数据库表的币种清单
                fullname = c[2]
            ci = get_feixiaohao_currency_info(fullname)

            # 如果获取失败，重试 5 次。
            if len(ci) == 0:
                retry = 0
                while retry < 5:
                    print('\033[0;30;41m fetch failure retry >>> \033[0m', c[2])
                    ci = get_feixiaohao_currency_info(c[2])
                    if len(ci) != 0:
                        break
                    retry += 1
                    time.sleep(2)

            if len(ci) == 0:
                errorCurrencies.append(c[2])
                print('\033[0;30;41m fetch failure >>> \033[0m', c[2])
                continue

            # 查询币种是否已经存在
            sql = 'SELECT _id FROM `xcm_vxn_currency_info` WHERE currency=%s'
            cursor.execute(sql, (c[1]))
            rows = cursor.fetchall()

            # 币种的属性
            param = (
                c[1], c[2], c[3], c[4],
                ci['price_cny'], ci['price_scope'], ci['high'], ci['low'],
                ci['circulating_cny_value'], ci['ranking'], ci['circulating_usd_value'], ci[
                    'circulating_btc_value'], ci['circulating_value_percent'], ci['circulating_volume'],
                ci['total_volume'], ci['circulating_rate'], ci['turn_volume'], ci['turn_volume_ranking'], ci['turnover_rate']
            )

            # 不存在，则插入新数据
            if len(rows) == 0:
                sql = '''INSERT INTO 
                `xcm_vxn_currency_info`
                    (currency, fullname, cnname, description, 
                    price_cny, price_scope, high, low, 
                    circulating_cny_value, ranking, circulating_usd_value, circulating_btc_value, circulating_value_percent, circulating_volume, 
                    total_volume, circulating_rate, turn_volume, turn_volume_ranking, turnover_rate, 
                    create_time, update_time) 
                VALUES 
                    (%s, %s, %s, %s, 
                    %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, 
                    %s, %s)'''
                now = time.time()
                param = param + (now, now)
            else:  # 已存在，则更新数据
                sql = '''UPDATE `xcm_vxn_currency_info` SET
                currency=%s, fullname=%s, cnname=%s, description=%s, 
                price_cny=%s, price_scope=%s, high=%s, low=%s, 
                circulating_cny_value=%s, ranking=%s, circulating_usd_value=%s, circulating_btc_value=%s, circulating_value_percent=%s, circulating_volume=%s, 
                total_volume=%s, circulating_rate=%s, turn_volume=%s, turn_volume_ranking=%s, turnover_rate=%s, 
                update_time=%s
                WHERE currency=%s'''
                param = param + (time.time(), c[1])

            cursor.execute(sql, param)
            rowcount = cursor.rowcount
            if rowcount == 0:
                print('\033[0;30;41m save currency info',
                      c[2], 'result >>> \033[0m', rowcount)
                print(sql % param)
            else:
                print('\033[0;30;42m save currency info',
                      c[2], 'result >>> \033[0m', rowcount)
                db.commit()
                success += 1

            print('start date >>>', startDate)
            print('now date   >>>', datetime.datetime.now())
            print('process >>> \033[0;30;41m', len(
                errorCurrencies), '\033[0m/\033[0;30;42m', success, '\033[0m/', total)

            time.sleep(1)

        # main 可嵌套 2 次
        if len(errorCurrencies) > 0 and mainNest < 2:
            mainNest += 1
            tmp = tuple(errorCurrencies)
            print('mainNext errorCurrencies tuple >>>', tmp)
            main(tmp)

    except:
        print('\033[0;30;41m main except >>> \033[0m')
        filename = os.path.basename(sys.argv[0]).split(".")[0]
        util.printExcept(filename)
    finally:
        cursor.close()
        db.close()

    if len(errorCurrencies) > 0:
        print('\033[0;30;41m errorCurrencies >>> \033[0m',
              len(errorCurrencies), errorCurrencies)
    else:
        print('\033[0;30;42m all success \033[0m')

    # 打印开始与结束时间
    finishNotice = 'start date >>> %s\nend date   >>> %s'%(startDate, datetime.datetime.now())
    print('start date >>>', startDate)
    print('end date   >>>', datetime.datetime.now())
    util.logToFile(finishNotice)


def main_timer():
    thread.start_new_thread(main, ())
    timer = threading.Timer(60*60*1.2, main_timer)
    timer.start()


def test_error_currency():

    f = open('feixiaohao-error-currency-2.json')
    content = f.read()
    f.close()

    currencies = json.loads(content)

    total = len(currencies)
    errorCurrencies = []
    success = 0

    for c in currencies:

        ci = get_feixiaohao_currency_info(c)

        # 如果获取失败，重试 5 次。
        if len(ci) == 0:
            retry = 0
            while retry < 5:
                ci = get_feixiaohao_currency_info(c)
                if len(ci) != 0:
                    break
                retry += 1
                time.sleep(2)

        if len(ci) == 0:
            print('\033[0;30;41m fetch failure >>> \033[0m', c)
            errorCurrencies.append(c)
        else:
            print('\033[0;30;42m fetch successed >>> \033[0m', c)
            success += 1

        print('process >>> \033[0;30;41m', len(
            errorCurrencies), '\033[0m/\033[0;30;42m', success, '\033[0m/', total)

        time.sleep(2)

    if len(errorCurrencies) > 0:
        print('\033[0;30;41m errorCurrencies \033[0m',
              len(errorCurrencies), errorCurrencies)
    else:
        print('\033[0;30;42m all success \033[0m')


if __name__ == '__main__':
    # main()
    # get_feixiaohao_currency_info('ors-group')
    # test_error_currency()
    util.daemonize(main_timer)

