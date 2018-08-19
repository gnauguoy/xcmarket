import socket
from urllib import request
import json
from chengutil import mysqlutil, util
import time, datetime
import _thread

total = 0
runCount = 0


def request_kline_rest(symbol, period, startTime=0, endTime=0, size=1000):
    try:

        url = 'https://api.binance.com/api/v1/klines?symbol=%s&interval=%s&limit=%d'
        if startTime == 0 or endTime == 0:
            url = url % (symbol, period, size)
        else:
            url = (url + '&startTime=%d&endTime=%d') % (symbol, period, size, startTime, endTime)
        # 测试接口是否正常
        # url = 'https://api.binance.com/api/v1/time'
        # url = 'http://ip.cn'
        mysqlutil.log('binance', url)
        socket.setdefaulttimeout(20)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0",
        }
        req = request.Request(url, None, headers)
        response = request.urlopen(req)
        mysqlutil.log('binance', 'response code >>>', response.code)
        content = response.read().decode('utf-8')

        content = json.loads(content)
        mysqlutil.log('binance', 'data len >>>', len(content))
        if len(content) > 0:
            mysqlutil.log('binance', 'data >>>')
            mysqlutil.log('binance', '   ', '[' + str(content[0]) + ', ...]')
            mysqlutil.log('binance', 'data start >>>', util.getLocaleDateStrBy13(content[0][0]))
            mysqlutil.log('binance', 'data end >>>', util.getLocaleDateStrBy13(content[len(content) - 1][0]))
        return content
    except:
        util.printExcept()
        time.sleep(61)
        return False


# 测试 K 线数据可获取的最大时间跨度
# request_binance_kline_rest('BNBBTC', '1m', util.getTimeStampReturn13('2018-08-05 00:00:00'), util.getTimeStampReturn13('2018-08-06 00:00:00'))
# request_binance_kline_rest('BNBBTC', '1m', util.getTimeStampReturn13('2018-01-01 00:00:00'), util.getTimeStampReturn13('2018-01-02 00:00:00'))
# request_binance_kline_rest('BNBBTC', '1m', util.getTimeStampReturn13('2017-12-01 00:00:00'), util.getTimeStampReturn13('2017-12-02 00:00:00'))
# request_binance_kline_rest('BNBBTC', '1m', util.getTimeStampReturn13('2017-11-01 00:00:00'), util.getTimeStampReturn13('2017-11-02 00:00:00'))
# request_binance_kline_rest('BNBBTC', '1m', util.getTimeStampReturn13('2017-10-01 00:00:00'), util.getTimeStampReturn13('2017-10-02 00:00:00'))
# request_kline_rest('BNBBTC', '1m', util.getTimeStampReturn13('2017-08-01 00:00:00'), util.getTimeStampReturn13('2017-08-02 00:00:00'))
# while True:
#     request_binance_kline_rest('BNBBTC', '1m', util.getTimeStampReturn13('2017-07-14 00:00:00'), util.getTimeStampReturn13('2017-08-01 00:00:00'))
#     time.sleep(1)
# 可获取 K 线数据的最大时间跨度为 387 天


def get_kline_history(period):
    global runCount, count, total, done, doneToken, pendingPeriods

    startDate = str(datetime.datetime.now())

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        sql = 'SELECT symbol, base_asset, quote_asset FROM xcm_binance_symbol'
        cursor.execute(sql)
        symbols = cursor.fetchall()

        symbolCount = 0

        nowTime13 = int(time.time() * 1000)

        for r in symbols:

            symbol = r[0]
            base = r[1]
            quote = r[2]

            symbolCount += 1
            mysqlutil.log('binance', startDate, period, 'symbol >>>', symbol, symbolCount, '/', len(symbols))

            # 获取最近的一条数据的时间戳
            sql = '''
                SELECT open_time FROM xcm_binance_kline_history 
                WHERE symbol=%s AND period=%s 
                ORDER BY open_time DESC LIMIT 0,1
            '''
            cursor.execute(sql, (symbol, period))
            rows = cursor.fetchall()
            lastTimestamp = 0
            if len(rows) == 0:
                since = 1
            else:
                lastTimestamp = rows[0][0]
                # mysqlutil.log('binance', startDate, period, 'last timestamp >>>', str(rows[0][0]))
                mysqlutil.log('binance', startDate, period, 'last datetime >>>', util.getLocaleDateStrBy13(rows[0][0]))
                since = rows[0][0] + get_period_interval(period) * 1000

            mysqlutil.log('binance', startDate, period, 'period >>>', period)
            if since != '':
                mysqlutil.log('binance', startDate, period, 'since datetime >>>', util.getLocaleDateStrBy13(int(since)))
            kdata = request_kline_rest(symbol, period, since, nowTime13)
            if kdata is False:
                continue
            elif 'error_code' in kdata:
                mysqlutil.log('binance', startDate, period, '\033[0;30;41m error_code >>>', kdata['error_code'], '\033[0m\n')
                continue
            else:
                mysqlutil.log('binance', startDate, period, 'kdata len >>>', len(kdata))
                if len(kdata):
                    mysqlutil.log('binance', startDate, period, 'kdata >>>')
                    mysqlutil.log('binance', '   ', '[' + str(kdata[0]) + ', ...]')
                    mysqlutil.log('binance', startDate, period, 'kdata start datetime >>>', util.getLocaleDateStrBy13(kdata[0][0]))

            newTimestamps = []

            for k in kdata:

                newTimestamp = k[0]
                # mysqlutil.log('binance', 'newTimestamp >>>', newTimestamp)
                if lastTimestamp == newTimestamp or newTimestamp in newTimestamps:
                    mysqlutil.log('binance', startDate, period, '\033[0;30;47m duplicated timestamp >>>', k[0], '\033[0m')
                    mysqlutil.log('binance', startDate, period, '\033[0;30;47m duplicated timestamp >>>', util.getLocaleDateStrBy13(k[0]),
                          '\033[0m')
                    continue

                newTimestamps.append(newTimestamp)

                nowTime = time.time()
                nowTime *= 10000000

                sql = '''
                    INSERT INTO xcm_binance_kline_history (
                        _id, symbol,base_asset,quote_asset,period,
                        open_time,open,high,low,close,volume,close_time,
                        quote_asset_volume,num_of_trades,buy_base_asset,buy_quote_asset,f_ignore)
                    VALUES (
                        %s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s)'''
                param = (
                    nowTime, symbol, base, quote, period,
                    k[0], k[1], k[2], k[3], k[4], k[5], k[6],
                    k[7], k[8], k[9], k[10], k[11])
                # print('binance', 'sql >>>', sql%param)
                cursor.execute(sql, param)

                count += 1
                total += 1

            db.commit()

            mysqlutil.log('binance', '\033[0;30;43m', startDate, period, 'begin date >>>', beginDate, '\033[0m')
            mysqlutil.log('binance', '\033[0;30;43m', startDate, period, 'start date >>>', startDate, '\033[0m')
            mysqlutil.log('binance', '\033[0;30;43m', startDate, period, 'current date >>>', str(datetime.datetime.now()), '\033[0m')
            mysqlutil.log('binance', startDate, period, 'insert done >>> {:,}'.format(count))
            mysqlutil.log('binance', startDate, period, 'period done >>>', str(done))
            mysqlutil.log('binance', startDate, period, 'period doneToken >>>', str(doneToken))
            mysqlutil.log('binance', startDate, period, 'period pending >>>', str(pendingPeriods))
            mysqlutil.log('binance', '\033[0;30;42m', startDate, period, 'total >>> {:,}'.format(total), '\033[0m')
            mysqlutil.log('binance', 'runCount >>>', runCount, '\n')

        done.append(period)
        doneToken[period] = 1
        pendingPeriods.discard(period)

    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()

    mysqlutil.log('binance', '\033[0;30;43m', startDate, period, 'begin date >>>', beginDate, '\033[0m')
    mysqlutil.log('binance', '\033[0;30;43m', startDate, period, 'start date >>>', startDate, '\033[0m')
    mysqlutil.log('binance', '\033[0;30;43m', startDate, period, 'end date >>>', str(datetime.datetime.now()), '\033[0m')
    mysqlutil.log('binance', startDate, period, 'period done >>>', done)
    mysqlutil.log('binance', startDate, period, 'period doneToken >>>', str(doneToken))
    mysqlutil.log('binance', startDate, period, 'period pending >>>', str(pendingPeriods))
    mysqlutil.log('binance', '\033[0;30;42m', startDate, period, 'total >>> {:,}'.format(total), ' \033[0m')

    if len(done) == len(periods):
        runCount += 1

    mysqlutil.log('binance', 'runCount >>>', runCount, '\n')


# 计算获取数据的时间间隔
# 返回时间的单位为秒
def get_period_interval(period):
    interval = 0
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
            sql = 'SELECT count(_id) FROM xcm_binance_kline_history'
            cursor.execute(sql)
            rows = cursor.fetchall()
            if len(rows) != 0:
                total = rows[0][0]

        mysqlutil.log('binance', '\ntotal >>> {:,}'.format(total))
    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()

    for p in periods:
        mysqlutil.log('binance', 'start period thread >>>', p)
        _thread.start_new_thread(get_kline_history, (p,))


def init():
    global count, done, doneToken, pendingPeriods, periods

    mysqlutil.log('binance', str(datetime.datetime.now()), 'init')

    count = 0
    done = []
    doneToken = {
        '1m': 0, '3m': 0, '5m': 0, '15m': 0, '30m': 0,
        '1h': 0, '2h': 0, '4h': 0, '6h': 0, '8h': 0, '12h': 0,
        '1d': 0, '3d': 0, '1w': 0, '1M': 0
    }
    pendingPeriods = {
        '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'
    }
    periods = [
        '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'
    ]


if __name__ == '__main__':

    global beginDate
    beginDate = str(datetime.datetime.now())

    currentRunCount = runCount
    get_kline_history_by_peroid()

    while True:
        if currentRunCount == runCount:
            time.sleep(60)
        else:
            mysqlutil.log('binance', str(datetime.datetime.now()), 'over')
            currentRunCount = runCount
            get_kline_history_by_peroid()
            # break
