import socket
from urllib import request
import json
from chengutil import mysqlutil, util
import time, datetime
import _thread
import math
import pymysql

total = 0
runCount = 0


def request_kline_rest(symbol, period, since):
    try:

        periodSec = get_period_interval(period)
        rangeHour = get_hour_span(since)
        url = 'https://data.gateio.io/api2/1/candlestick2/%s?group_sec=%s&range_hour=%s' % (
            symbol, periodSec, rangeHour)
        mysqlutil.log('gate', url)
        socket.setdefaulttimeout(20)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0",
        }
        req = request.Request(url, None, headers)
        response = request.urlopen(req)
        mysqlutil.log('gate', 'response code >>>', response.code)
        content = response.read().decode('utf-8')

        mysqlutil.log('gate', 'content >>>', content)
        content = json.loads(content)
        mysqlutil.log('gate', 'data len >>>', len(content))
        if 'code' in content:
            mysqlutil.log('gate', 'error url >>>', url)
            # 返回请求太频繁的错误
            if content['code'] == 40:
                time.sleep(60)
            return content
        data = content['data']
        if len(data) > 0:
            mysqlutil.log('gate', 'data >>>', '[' + str(data[0]) + ', ...]')
            mysqlutil.log('gate', 'data start >>>', util.getLocaleDateStrBy13(int(data[0][0])))
            mysqlutil.log('gate', 'data end >>>', util.getLocaleDateStrBy13(int(data[len(data) - 1][0])))
        return content
    except:
        util.printExcept()
        return False


def get_hour_span(timestamp):
    span = time.time() - timestamp
    if span == 0:
        return 1
    span = span / 1000 / 60 / 60
    if span < 1:
        return 1
    else:
        return math.ceil(span)


def get_kline_history(period):
    global runCount, count, total, done, doneToken, pendingPeriods

    startDate = str(datetime.datetime.now())

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        sql = 'SELECT symbol, base, quote FROM xcm_gate_symbol'
        cursor.execute(sql)
        symbols = cursor.fetchall()

        symbolCount = 0

        nowTime13 = int(time.time() * 1000)

        for r in symbols:

            symbol = r[0]
            base = r[1]
            quote = r[2]

            symbolCount += 1
            mysqlutil.log('gate', startDate, period, 'symbol >>>', symbol, symbolCount, '/', len(symbols))

            # 获取最近的一条数据的时间戳
            sql = '''
                SELECT ts FROM xcm_gate_kline_history 
                WHERE symbol=%s AND period=%s 
                ORDER BY ts DESC LIMIT 0,1
            '''
            cursor.execute(sql, (symbol, period))
            rows = cursor.fetchall()
            lastTimestamp = 0
            if len(rows) == 0:
                since = util.getTimeStampReturn13('2017-12-01 00:00:00')
            else:
                lastTimestamp = rows[0][0]
                # mysqlutil.log('gate', startDate, period, 'last timestamp >>>', str(rows[0][0]))
                mysqlutil.log('gate', startDate, period, 'last datetime >>>', util.getLocaleDateStrBy13(rows[0][0]))
                since = rows[0][0] + get_period_interval(period)

            mysqlutil.log('gate', startDate, period, 'period >>>', period)
            if since != '':
                mysqlutil.log('gate', startDate, period, 'since datetime >>>', util.getLocaleDateStrBy13(int(since)))
            kdata = request_kline_rest(symbol, period, since)
            if kdata is False:
                continue
            elif 'code' in kdata:
                mysqlutil.log('gate', startDate, period, '\033[0;30;41m code >>>', kdata['code'], kdata['message'],
                              '\033[0m\n')
                continue
            elif 'result' in kdata and kdata['result']:
                kdata = kdata['data']
                mysqlutil.log('gate', startDate, period, 'kdata len >>>', len(kdata))
                if len(kdata):
                    mysqlutil.log('gate', startDate, period, 'kdata >>>')
                    mysqlutil.log('gate', '   ', '[' + str(kdata[0]) + ', ...]')
                    mysqlutil.log('gate', startDate, period, 'kdata start datetime >>>',
                                  util.getLocaleDateStrBy13(int(kdata[0][0])))

            newTimestamps = []

            for k in kdata:

                newTimestamp = k[0]
                # mysqlutil.log('gate', 'newTimestamp >>>', newTimestamp)
                if lastTimestamp == newTimestamp or newTimestamp in newTimestamps:
                    mysqlutil.log('gate', startDate, period, '\033[0;30;47m duplicated timestamp >>>', k[0], '\033[0m')
                    mysqlutil.log('gate', startDate, period, '\033[0;30;47m duplicated timestamp >>>',
                                  util.getLocaleDateStrBy13(k[0]),
                                  '\033[0m')
                    continue

                newTimestamps.append(newTimestamp)

                nowTime = time.time()
                nowTime *= 10000000

                sql = '''
                    INSERT INTO xcm_gate_kline_history (
                        _id, symbol, base, quote, period,
                        ts, volume, close, high, low, open)
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s)'''
                param = (
                    nowTime, symbol, base, quote, period,
                    k[0], k[1], k[2], k[3], k[4], k[5])

                try:

                    # print('gate', 'sql >>>', sql%param)
                    cursor.execute(sql, param)

                    count += 1
                    total += 1
                except pymysql.err.IntegrityError:
                    # util.printExcept()
                    mysqlutil.log('gate', startDate, period, '\033[0;30;41m pymysql.err.IntegrityError', '\033[0m\n')
                    mysqlutil.log('gate', startDate, period, sql % param)

            db.commit()

            mysqlutil.log('gate', '\033[0;30;43m', startDate, period, 'begin date >>>', beginDate, '\033[0m')
            mysqlutil.log('gate', '\033[0;30;43m', startDate, period, 'start date >>>', startDate, '\033[0m')
            mysqlutil.log('gate', '\033[0;30;43m', startDate, period, 'current date >>>', str(datetime.datetime.now()),
                          '\033[0m')
            mysqlutil.log('gate', startDate, period, 'insert done >>> {:,}'.format(count))
            mysqlutil.log('gate', startDate, period, 'period done >>>', str(done))
            mysqlutil.log('gate', startDate, period, 'period doneToken >>>', str(doneToken))
            mysqlutil.log('gate', startDate, period, 'period pending >>>', str(pendingPeriods))
            mysqlutil.log('gate', '\033[0;30;42m', startDate, period, 'total >>> {:,}'.format(total), '\033[0m')
            mysqlutil.log('gate', 'runCount >>>', runCount, '\n')

        done.append(period)
        doneToken[period] = 1
        pendingPeriods.discard(period)

    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()

    mysqlutil.log('gate', '\033[0;30;43m', startDate, period, 'begin date >>>', beginDate, '\033[0m')
    mysqlutil.log('gate', '\033[0;30;43m', startDate, period, 'start date >>>', startDate, '\033[0m')
    mysqlutil.log('gate', '\033[0;30;43m', startDate, period, 'end date >>>', str(datetime.datetime.now()), '\033[0m')
    mysqlutil.log('gate', startDate, period, 'period done >>>', done)
    mysqlutil.log('gate', startDate, period, 'period doneToken >>>', str(doneToken))
    mysqlutil.log('gate', startDate, period, 'period pending >>>', str(pendingPeriods))
    mysqlutil.log('gate', '\033[0;30;42m', startDate, period, 'total >>> {:,}'.format(total), ' \033[0m')

    if len(done) == len(periods):
        runCount += 1

    mysqlutil.log('gate', 'runCount >>>', runCount, '\n')


# 计算获取数据的时间间隔
# 返回时间的单位为秒
def get_period_interval(period):
    interval = 0
    if period.find('s') > -1:
        num = int(period.replace('s', ''))
        interval = num
    if period.find('m') > -1:
        num = int(period.replace('m', ''))
        interval = num * 60
    elif period.find('h') > -1:
        num = int(period.replace('h', ''))
        interval = num * 60 * 60
    elif period.find('d') > -1:
        num = period.replace('d', '')
        num = int(num)
        interval = num * 24 * 60 * 60
    elif period.find('w') > -1:
        num = period.replace('w', '')
        num = int(num)
        interval = num * 7 * 24 * 60 * 60
    elif period.find('M') > -1:
        num = period.replace('M', '')
        num = int(num)
        interval = num * 365 * 7 * 24 * 60 * 60

    return interval


def get_kline_history_by_peroid():
    init()

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        global total

        if total == 0:
            sql = 'SELECT count(_id) FROM xcm_gate_kline_history'
            cursor.execute(sql)
            rows = cursor.fetchall()
            if len(rows) != 0:
                total = rows[0][0]

        mysqlutil.log('gate', '\ntotal >>> {:,}'.format(total))
    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()

    for p in periods:
        mysqlutil.log('gate', 'start period thread >>>', p)
        _thread.start_new_thread(get_kline_history, (p,))


def init():
    global count, done, doneToken, pendingPeriods, periods

    mysqlutil.log('gate', str(datetime.datetime.now()), 'init')

    count = 0
    done = []
    doneToken = {
        '1m': 0, '5m': 0, '10m': 0, '15m': 0, '20m': 0, '30m': 0,
        '1h': 0, '2h': 0, '3h': 0, '4h': 0, '6h': 0, '8h': 0,
        '1d': 0, '2d': 0, '3d': 0, '4d': 0, '5d': 0, '6d': 0, '7d': 0
    }
    pendingPeriods = {
        '1m', '5m', '10m', '15m', '20m', '30m', '1h', '2h', '3h', '4h', '6h', '8h', '1d', '2d', '3d', '4d', '5d',
        '6d', '7d'
    }
    periods = [
        '1m', '5m', '10m', '15m', '20m', '30m', '1h', '2h', '3h', '4h', '6h', '8h', '1d', '2d', '3d', '4d', '5d',
        '6d', '7d'
    ]


if __name__ == '__main__':

    global beginDate
    beginDate = str(datetime.datetime.now())

    currentRunCount = runCount
    get_kline_history_by_peroid()

    while True:
        if currentRunCount == runCount:
            time.sleep(60*60)
        else:
            mysqlutil.log('gate', str(datetime.datetime.now()), 'over')
            currentRunCount = runCount
            get_kline_history_by_peroid()

# request_kline_rest('btc_usdt', '1m', util.getTimeStamp('2018-01-01 00:00:00'))
