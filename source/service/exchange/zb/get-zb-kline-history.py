import socket
from urllib import request
import json
from chengutil import mysqlutil, util
import time, datetime
import _thread

total = 0
runCount = 0


def request_kline_rest(symbol, period, since=0, size=1000):
    try:

        url = 'http://api.zb.cn/data/v1/kline?market=%s&type=%s&since=%s&size=%s' % (symbol, period, since, size)
        mysqlutil.log('zb', url)
        socket.setdefaulttimeout(20)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0",
        }
        req = request.Request(url, None, headers)
        response = request.urlopen(req)
        mysqlutil.log('zb', 'response code >>>', response.code)
        content = response.read().decode('utf-8')

        # mysqlutil.log('zb', 'content >>>', content)
        content = json.loads(content)
        data = content['data']
        mysqlutil.log('zb', 'data symbol >>>', content['symbol'])
        mysqlutil.log('zb', 'data moneyType >>>', content['moneyType'])
        mysqlutil.log('zb', 'data len >>>', len(data))
        if len(data) > 0:
            mysqlutil.log('zb', 'data >>>')
            mysqlutil.log('zb', '   ', '[' + str(data[0]) + ', ...]')
            mysqlutil.log('zb', 'data start >>>', util.getLocaleDateStrBy13(data[0][0]))
            mysqlutil.log('zb', 'data end >>>', util.getLocaleDateStrBy13(data[len(data) - 1][0]))
        return content
    except:
        util.printExcept()
        time.sleep(61)
        return False


# 测试 K 线数据可获取的最大时间跨度
# request_kline_rest('btc_usdt', '1min', util.getTimeStampReturn13('2018-08-05 00:00:00'))
# request_kline_rest('btc_usdt', '1min', util.getTimeStampReturn13('2018-01-01 00:00:00'))
# request_kline_rest('btc_usdt', '5min', util.getTimeStampReturn13('2017-12-01 00:00:00'))
# request_kline_rest('btc_usdt', '15min', util.getTimeStampReturn13('2017-12-01 00:00:00'))
# request_kline_rest('btc_usdt', '30min', util.getTimeStampReturn13('2017-12-01 00:00:00'))
# request_kline_rest('btc_usdt', '1hour', util.getTimeStampReturn13('2017-12-01 00:00:00'))
# request_kline_rest('btc_usdt', '1min', util.getTimeStampReturn13('2017-11-01 00:00:00'))
# request_kline_rest('btc_usdt', '1min', util.getTimeStampReturn13('2017-10-01 00:00:00'))
# request_kline_rest('btc_usdt', '1min', util.getTimeStampReturn13('2017-08-01 00:00:00'))
# while True:
#     request_kline_rest('btc_usdt', '1min', util.getTimeStampReturn13('2017-07-14 00:00:00'))
#     time.sleep(1)
# 可获取 1min K 线数据的最大时间跨度为 1 天 5 小时
# 可获取 5min K 线数据的最大时间跨度为 3 天 20 小时

runThreadLock = {
    '1min': {'time':0,'lock':0}, '3min': {'time':0,'lock':0}, '5min': {'time':0,'lock':0}, '15min': {'time':0,'lock':0}, '30min': {'time':0,'lock':0},
    '1hour': {'time':0,'lock':0}, '2hour': {'time':0,'lock':0}, '4hour': {'time':0,'lock':0}, '6hour': {'time':0,'lock':0}, '12hour': {'time':0,'lock':0},
    '1day': {'time':0,'lock':0}, '3day': {'time':0,'lock':0},
    '1week': {'time':0,'lock':0}
}
runThreadTime = []

def get_kline_history(period):
    global runCount, count, total, done, doneToken, pendingPeriods

    startDate = str(datetime.datetime.now())

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        sql = 'SELECT symbol, base, quote FROM xcm_zb_symbol'
        cursor.execute(sql)
        symbols = cursor.fetchall()

        symbolCount = 0

        nowTime13 = int(time.time() * 1000)

        # 初始化线程标签
        threadLock = _thread.allocate_lock()
        threadLock.acquire()
        runThreadLock[period]['lock'] = threadLock
        threadTime = int(time.time() * 1000)
        runThreadTime.append(threadTime)
        runThreadLock[period]['time'] = threadTime

        while wait_all_thread_running() == False:
            time.sleep(5)

        print('ready to run >>>', period)

        for r in symbols:

            symbol = r[0]
            base = r[1]
            quote = r[2]

            symbolCount += 1
            mysqlutil.log('zb', startDate, period, 'symbol >>>', symbol, symbolCount, '/', len(symbols))

            # 获取最近的一条数据的时间戳
            sql = '''
                SELECT ts FROM xcm_zb_kline_history 
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
                # mysqlutil.log('zb', startDate, period, 'last timestamp >>>', str(rows[0][0]))
                mysqlutil.log('zb', startDate, period, 'last datetime >>>', util.getLocaleDateStrBy13(rows[0][0]))
                since = rows[0][0] + get_period_interval_return_min(period) * 1000

            mysqlutil.log('zb', startDate, period, 'period >>>', period)
            mysqlutil.log('zb', startDate, period, 'since datetime >>>', util.getLocaleDateStrBy13(int(since)))

            while True:
                print('thread period lock >>>', period, runThreadLock[period]['lock'].locked())
                if (runThreadLock[period]['lock'].locked() == True) and (lock_and_run(period, threadTime)):
                    kdata = request_kline_rest(symbol, period, since)
                    print('\033[1;31;42m thread release >>>', period, '\033[0m')
                    runThreadLock[period]['lock'].release()
                    # 更新线程时间
                    runThreadTime.remove(threadTime)
                    threadTime = int(time.time() * 1000)
                    runThreadTime.append(threadTime)
                    runThreadLock[period]['time'] = threadTime
                    print('runThreadTime >>>', runThreadTime)
                    break
                else:
                    # 给线程重新加锁
                    if runThreadLock[period]['lock'].locked() == False:
                        threadLock = _thread.allocate_lock()
                        threadLock.acquire()
                        runThreadLock[period]['lock'] = threadLock
                    time.sleep(10)

            if kdata is False:
                continue
            elif 'code' in kdata:
                mysqlutil.log('zb', startDate, period, '\033[0;30;41m error code >>>', kdata['code'], 'message >>>',
                              kdata['message'], '\033[0m\n')
                continue
            elif 'error' in kdata:
                mysqlutil.log('zb', startDate, period, '\033[0;30;41m error >>>', kdata['error'], '\033[0m\n')
                continue
            elif 'result' in kdata:
                mysqlutil.log('zb', startDate, period, '\033[0;30;41m result >>>', kdata['result'], 'message >>>',
                              kdata['message'], '\033[0m\n')
                continue
            elif 'data' in kdata:
                kdata = kdata['data']
                mysqlutil.log('zb', startDate, period, 'kdata len >>>', len(kdata))
                if len(kdata) > 0:
                    mysqlutil.log('zb', startDate, period, 'kdata >>>')
                    mysqlutil.log('zb', '   ', '[' + str(kdata[0]) + ', ...]')
                    mysqlutil.log('zb', startDate, period, 'kdata start datetime >>>',
                                  util.getLocaleDateStrBy13(kdata[0][0]))
            else:
                mysqlutil.log('zb', startDate, period, 'kdata >>>', kdata)

            newTimestamps = []

            for k in kdata:

                newTimestamp = k[0]
                # mysqlutil.log('zb', 'newTimestamp >>>', newTimestamp)
                if lastTimestamp == newTimestamp or newTimestamp in newTimestamps:
                    mysqlutil.log('zb', startDate, period, '\033[0;30;47m duplicated timestamp >>>', k[0], '\033[0m')
                    mysqlutil.log('zb', startDate, period, '\033[0;30;47m duplicated timestamp >>>',
                                  util.getLocaleDateStrBy13(k[0]), '\033[0m')
                    continue

                newTimestamps.append(newTimestamp)

                nowTime = time.time()
                nowTime *= 10000000

                sql = '''
                    INSERT INTO xcm_zb_kline_history (
                        _id, symbol, base, quote, period,
                        ts, open, high, low, close, amount)
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s)'''
                param = (
                    nowTime, symbol, base, quote, period,
                    k[0], k[1], k[2], k[3], k[4], k[5])
                # print('sql >>>', sql%param)
                cursor.execute(sql, param)

                count += 1
                total += 1

            db.commit()

            mysqlutil.log('zb', '\033[0;30;43m', startDate, period, 'begin date >>>', beginDate, '\033[0m')
            mysqlutil.log('zb', '\033[0;30;43m', startDate, period, 'start date >>>', startDate, '\033[0m')
            mysqlutil.log('zb', '\033[0;30;43m', startDate, period, 'current date >>>', str(datetime.datetime.now()),
                          '\033[0m')
            mysqlutil.log('zb', startDate, period, 'insert done >>> {:,}'.format(count))
            mysqlutil.log('zb', startDate, period, 'period done >>>', str(done))
            mysqlutil.log('zb', startDate, period, 'period doneToken >>>', str(doneToken))
            mysqlutil.log('zb', startDate, period, 'period pending >>>', str(pendingPeriods))
            mysqlutil.log('zb', '\033[0;30;42m', startDate, period, 'total >>> {:,}'.format(total), '\033[0m')
            mysqlutil.log('zb', 'runCount >>>', runCount, '\n')

        done.append(period)
        doneToken[period] = 1
        pendingPeriods.discard(period)

    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()

    mysqlutil.log('zb', '\033[0;30;43m', startDate, period, 'begin date >>>', beginDate, '\033[0m')
    mysqlutil.log('zb', '\033[0;30;43m', startDate, period, 'start date >>>', startDate, '\033[0m')
    mysqlutil.log('zb', '\033[0;30;43m', startDate, period, 'end date >>>', str(datetime.datetime.now()), '\033[0m')
    mysqlutil.log('zb', startDate, period, 'period done >>>', done)
    mysqlutil.log('zb', startDate, period, 'period doneToken >>>', str(doneToken))
    mysqlutil.log('zb', startDate, period, 'period pending >>>', str(pendingPeriods))
    mysqlutil.log('zb', '\033[0;30;42m', startDate, period, 'total >>> {:,}'.format(total), ' \033[0m')

    if len(done) == len(periods):
        runCount += 1

    mysqlutil.log('zb', 'runCount >>>', runCount, '\n')


def wait_all_thread_running():
    for p in runThreadLock:
        if type(runThreadLock[p]['lock']) == int:
            return False
    return True


def lock_and_run(period, threadTime):

    global runThreadTime, runThreadLock

    # print('\033[1;31;43m thread period >>>', period, '\033[0m')

    # 如果处在第一位，返回 True。
    if runThreadTime[0] == threadTime:
        # print('\033[1;31;44m thread period >>>', period, threadTime, '\033[0m')
        return True
    # 判断自己所在的线程时间是否排在第二个，如果不是退出返回 False。
    runThreadTime.sort()
    # print('thread time >>>', threadTime)
    # print('runThreadLock >>>', runThreadLock)
    # print('runThreadTime >>>', runThreadTime)
    if runThreadTime[1] != threadTime:
        return False
    # 按升序排序 runThreadTime，取第一个线程时间所在的线程，
    firstThreadTime = runThreadTime[0]
    # print('\033[1;31;43m thread period >>>', period, 'thread time check success \033[0m')
    # 判断是否已经执行完毕，
    for p in runThreadLock:
        # print('runThreadLock p time lock >>>', p, runThreadLock[p]['time'], runThreadLock[p]['lock'].locked())
        if runThreadLock[p]['time'] == firstThreadTime and runThreadLock[p]['lock'].locked() == False:
            # # 如果执行完毕，则清除第一个线程时间，
            # runThreadTime.pop(0)
            # 设置锁定自己的线程，返回 True。
            # print('\033[1;30;41m thread lock prepare  >>>', period, '\033[0m')
            # if runThreadLock[period]['lock'].locked() == False:
            #     runThreadLock[period]['lock'].acquire()
            # lock_all_thread()
            # print('\033[1;30;41m thread lock complete >>>', period, '\033[0m')
            return True
    # print('thread period >>>', period, threadTime)
    # print('runThreadTime >>>', len(runThreadTime), runThreadTime)
    # 否则返回 False。
    return False


# 不能给自身以外的线程加锁
# def lock_all_thread():
#     for p in runThreadLock:
#         if runThreadLock[p]['lock'].locked() == False:
#             runThreadLock[p]['lock'].acquire()

# 计算获取数据的时间间隔
# 时间间隔为当前最新数据的两倍时间
# 返回时间的单位为秒
def get_period_interval_return_min(period):
    interval = 0
    if period.find('min') > -1:
        num = int(period.replace('min', ''))
        interval = num * 60
    elif period.find('hour') > -1:
        num = int(period.replace('hour', ''))
        interval = num * 60 * 60
    elif period.find('day') > -1:
        num = period.replace('day', '')
        num = int(num)
        interval = num * 24 * 60 * 60
    elif period.find('week') > -1:
        num = period.replace('week', '')
        num = int(num)
        interval = num * 7 * 24 * 60 * 60

    return interval


def get_kline_history_by_peroid():
    init()

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        global total

        if total == 0:
            sql = 'SELECT count(_id) FROM xcm_zb_kline_history'
            cursor.execute(sql)
            rows = cursor.fetchall()
            if len(rows) != 0:
                total = rows[0][0]

        mysqlutil.log('zb', '\ntotal >>> {:,}'.format(total))
    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()

    for p in periods:
        mysqlutil.log('zb', 'start period thread >>>', p)
        _thread.start_new_thread(get_kline_history, (p,))


def init():
    global count, done, doneToken, pendingPeriods, periods

    mysqlutil.log('zb', str(datetime.datetime.now()), 'init')

    count = 0
    done = []
    doneToken = {
        '1min': 0, '3min': 0, '5min': 0, '15min': 0, '30min': 0,
        '1hour': 0, '2hour': 0, '4hour': 0, '6hour': 0, '12hour': 0,
        '1day': 0, '3day': 0,
        '1week': 0
    }
    pendingPeriods = {
        '1min', '3min', '5min', '15min', '30min', '1hour', '2hour', '4hour', '6hour', '12hour', '1day', '3day', '1week'
    }
    periods = [
        '1min', '3min', '5min', '15min', '30min', '1hour', '2hour', '4hour', '6hour', '12hour', '1day', '3day', '1week'
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
            mysqlutil.log('zb', str(datetime.datetime.now()), 'over')
            currentRunCount = runCount
            get_kline_history_by_peroid()
            # break
