import json
import socket
import time
from urllib import request

from chengutil import mysqlutil, util


TABLE = 'hitbtc'


# 获取最近的一条数据的时间戳
def get_last_timestamp(symbol, period):
    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        sql = '''
            SELECT ts FROM xcm_%s_kline 
            WHERE symbol='%s' AND period='%s'
            ORDER BY ts DESC LIMIT 0,1
        ''' % (TABLE, symbol, period)
        cursor.execute(sql)
        rows = cursor.fetchall()
        if len(rows) == 0:
            since = util.getTimeStamp('2018-01-01 00:00:00')
        else:
            lastTimestamp = rows[0][0]
            # 打印最近一条数据的时间
            # mysqlutil.log(TABLE, startDate, period, 'last timestamp >>>', lastTimestamp)
            mysqlutil.log(TABLE, period, 'last datetime >>>', util.getLocaleDateStrBy10(lastTimestamp))
            since = rows[0][0]

        return since
    except:
        util.printExcept(target='get-' + TABLE + '-kline > get_last_timestamp')
    finally:
        cursor.close()
        db.close()

    return False


def get_symbols(format='tuple'):

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        sql = 'SELECT symbol, base, quote FROM xcm_%s_symbol' % (TABLE)
        cursor.execute(sql)
        symbols = cursor.fetchall()
        if format == 'dict':
            dict = {}
            for s in symbols:
                dict[s[0]] = {'base': s[1], 'quote': s[2]}
            symbols = dict
        return symbols
    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()

    return False


def get_candle_info(symbol, period, limit=1000):
    try:
        url = 'https://api.hitbtc.com/api/2/public/candles/%s?period=%s&limit=%s' % (symbol, period, limit)
        # print(url)
        socket.setdefaulttimeout(20)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0"
        }
        req = request.Request(url, None, headers)
        response = request.urlopen(req)
        content = response.read().decode('utf-8')

        # print(content)
        content = json.loads(content)
        # print('data len >>>', len(content))
        return content
    except:
        util.printExcept(target='hitbtc > get_candle_info')
        return False


def save_kline_record(symbol, base, quote, period, krecord, table, insertSql, klineFields):
    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        nowTime = time.time() * 10000000

        sql = insertSql
        param = (nowTime, symbol, base, quote, period)
        for f in klineFields:
            if type([f]) == list and len(f) == 2:
                param += (util.getTimeStamp(krecord[f[0]], f[1]),)
            else:
                param += (krecord[f],)
        cursor.execute(sql, param)
        db.commit()

        return True

    except:
        util.printExcept(target='get-' + table + '-kline > save_krecord')
        return False
    finally:
        cursor.close()
        db.close()


def get_ticker():
    try:
        url = 'https://api.hitbtc.com/api/2/public/ticker'
        # print(url)
        socket.setdefaulttimeout(20)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0"
        }
        req = request.Request(url, None, headers)
        response = request.urlopen(req)
        content = response.read().decode('utf-8')

        # print(content)
        content = json.loads(content)
        # print('data len >>>', len(content))
        return content
    except:
        util.printExcept(target='hitbtc > get_ticker')
        return False
