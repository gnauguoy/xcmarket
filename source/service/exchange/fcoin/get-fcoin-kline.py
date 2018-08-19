import fcoin
import time, datetime
from chengutil import mysqlutil, util, fcoin as cfcoin

api = fcoin.authorize('key', 'secret')
startDate = datetime.datetime.now()
exCount = 0
errCount = 0
runCount = 0

periods = ['M1', 'M3', 'M5', 'M15', 'M30', 'H1', 'H4', 'H6', 'D1', 'W1', 'MN']


# 获取最近的一条数据的时间戳
def get_last_timestamp(symbol, period):
    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        sql = '''
            SELECT ts FROM xcm_fcoin_kline 
            WHERE symbol=%s AND period=%s 
            ORDER BY ts DESC LIMIT 0,1
        '''
        cursor.execute(sql, (symbol, period))
        rows = cursor.fetchall()
        if len(rows) == 0:
            since = util.getTimeStamp('2018-01-01 00:00:00')
        else:
            lastTimestamp = rows[0][0]
            # 打印最近一条数据的时间
            # mysqlutil.log('fcoin', startDate, period, 'last timestamp >>>', lastTimestamp)
            mysqlutil.log('fcoin', startDate, period, 'last datetime >>>', util.getLocaleDateStrBy10(rows[0][0]))
            since = rows[0][0]

        return since
    except:
        global exCount
        exCount += 1
        util.printExcept(target='get-fcoin-kline > get_last_timestamp')
    finally:
        cursor.close()
        db.close()

    return False


def save_krecord(symbol, base, quote, period, k):
    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        nowTime = time.time() * 10000000

        sql = '''
            INSERT INTO xcm_fcoin_kline (
                _id, symbol, base, quote, period,
                open, close, high, low, count, 
                base_vol, quote_vol, ts, seq)
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, 
                %s, %s, %s, %s)'''
        param = (
            nowTime, symbol, base, quote, period,
            k['open'], k['close'], k['high'], k['low'], k['count'],
            k['base_vol'], k['quote_vol'], k['id'], k['seq'])
        cursor.execute(sql, param)
        db.commit()

        return True

    except:
        global exCount
        exCount += 1
        util.printExcept(target='get-fcoin-kline > save_krecord')
    finally:
        cursor.close()
        db.close()

    return False


def save_kdata(symbol, base, quote, period, kdata):
    startTimestamp = time.time()
    lastTimestamp = get_last_timestamp(symbol, period)

    # 从K线数据的末尾开始处理
    index = len(kdata) - 1
    count = len(kdata)
    newCount = count

    while 0 < index:

        k = kdata[index]
        index -= 1
        count -= 1

        # 不保存已存在的数据
        if k['id'] <= lastTimestamp:
            newCount -= 1
            continue

        # 打印K线数据的处理进度
        util.dprint(startDate, period, symbol, 'kdata count >>>', len(kdata), '/', newCount, '/', count)

        save_krecord(symbol, base, quote, period, k)

    timeSpan = util.timeElapsed(startTimestamp)
    totalSpan = util.timeElapsed(startDate.timestamp())
    util.dprint(startDate, period, symbol, 'newCount:', newCount, 'completed', '\ntimeSpan:', timeSpan, 'exCount:', exCount,
                'errCount:', errCount, 'runCount:', runCount, 'totalSpan:', totalSpan)
    mysqlutil.logWithList(table='fcoin',
                          list=[startDate, period, symbol, 'newCount:', newCount, 'completed', '\ntimeSpan:', timeSpan, 'exCount:',
                                exCount, 'errCount:', errCount, 'runCount:', runCount, 'totalSpan:', totalSpan])
    print()


def save_kline(period):
    startTimestamp = time.time()
    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        symbols = cfcoin.get_symbols()

        symbolCount = 0

        for s in symbols:

            symbol = s[0]
            base = s[1]
            quote = s[2]

            # 打印当前处理的交易对和处理进度
            symbolCount += 1
            mysqlutil.logWithList(table='fcoin',
                                  list=['\033[0;30;42m', startDate, period, 'symbol >>>', symbol, symbolCount, '/',
                                        len(symbols), '\033[0m'], show=True)

            try:
                kdata = api.market.get_candle_info(period, symbol)
            except:
                util.printExcept(target='get-fcoin-ticker > get_ticker')
                time.sleep(10)
                continue

            # 访问太过频繁，超过了每 10 秒钟 100 次的限制，先暂停休眠 10 秒钟。
            if kdata['status'] == 429:
                time.sleep(10)
            if kdata['status'] != 0:
                # 打印请求返回的错误信息
                mysqlutil.log('fcoin', startDate, period, symbol, 'get_candle_info error >>>', kdata)
                global errCount
                errCount += 1
                continue

            kdata = kdata['data']
            save_kdata(symbol, base, quote, period, kdata)

        mysqlutil.log('fcoin', period, 'complete datetime >>>', datetime.datetime.now())
        mysqlutil.log('fcoin', period, '     time elapsed >>>', util.timeElapsed(startTimestamp))

    except:
        global exCount
        exCount += 1
        util.printExcept(target='get-fcoin-kline > save_kline')
    finally:
        cursor.close()
        db.close()


def get_kline():
    for p in periods:
        save_kline(p)
    mysqlutil.log('fcoin', 'get_kline', 'time elapsed >>>', util.timeElapsed(startDate.timestamp()))


if __name__ == '__main__':

    while True:
        get_kline()
        runCount += 1
