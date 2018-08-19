import time, datetime
from chengutil import mysqlutil, util, hitbtc as chitbtc


startDate = datetime.datetime.now()
exCount = 0
errCount = 0
runCount = 0


TABLE = 'hitbtc'
PERIODS = ['M1', 'M3', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'D7', '1M']
INSERT_SQL = '''
INSERT INTO xcm_hitbtc_kline (
    _id, symbol, base, quote, period,
    open, max, min, close, volume, volumeQuote, ts)
VALUES (
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s)
'''
KLINE_FIELDS = ['open', 'max', 'min', 'close', 'volume', 'volumeQuote', ['timestamp', '%Y-%m-%dT%H:%M:%S.000Z']]


def save_kline_data(symbol, base, quote, period, kdata):
    startTimestamp = time.time()
    lastTimestamp = chitbtc.get_last_timestamp(symbol, period)
    if lastTimestamp == False:
        global exCount
        exCount += 1

    # 从K线数据的末尾开始处理
    index = len(kdata) - 1
    count = len(kdata)
    newCount = count

    while 0 < index:

        k = kdata[index]
        index -= 1
        count -= 1

        # 不保存已存在的数据
        if util.getTimeStamp(k['timestamp'], "%Y-%m-%dT%H:%M:%S.000Z") <= lastTimestamp:
            newCount -= 1
            continue

        # 打印K线数据的处理进度
        util.dprint(startDate, period, symbol, 'kdata count >>>', len(kdata), '/', newCount, '/', count)

        success = chitbtc.save_kline_record(symbol, base, quote, period, k, TABLE, INSERT_SQL, KLINE_FIELDS)
        if success == False:
            exCount += 1

    timeSpan = util.timeElapsed(startTimestamp)
    totalSpan = util.timeElapsed(startDate.timestamp())
    util.dprint(startDate, period, symbol, 'newCount:', newCount, 'completed', '\ntimeSpan:', timeSpan, ' exCount:',
                exCount, ' errCount:', errCount, ' runCount:', runCount, ' totalSpan:', totalSpan)
    mysqlutil.logWithList(table=TABLE,
                          list=[startDate, period, symbol, 'newCount:', newCount, 'completed', '\ntimeSpan:', timeSpan,
                                ' exCount:', exCount, ' errCount:', errCount, ' runCount:', runCount, ' totalSpan:',
                                totalSpan])
    print()


def save_kline(period):
    global exCount, errCount

    startTimestamp = time.time()
    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        symbols = chitbtc.get_symbols()

        symbolCount = 0

        for s in symbols:

            symbol = s[0]
            base = s[1]
            quote = s[2]

            # 打印当前处理的交易对和处理进度
            symbolCount += 1
            mysqlutil.logWithList(table=TABLE,
                                  list=['\033[0;30;42m', startDate, period, 'symbol >>>', symbol, symbolCount, '/',
                                        len(symbols), '\033[0m'], show=True)


            kdata = chitbtc.get_candle_info(symbol, period)
            if kdata == False:
                errCount += 1
                time.sleep(10)
                continue

            # 访问太过频繁，超过了每 1 秒钟 100 次的限制，先暂停休眠 1 秒钟。
            if 'error' in kdata and kdata['error']['code'] == 429:
                time.sleep(1)
            if 'error' in kdata:
                # 打印请求返回的错误信息
                mysqlutil.log(TABLE, startDate, period, symbol, 'get_candle_info error >>>', kdata)
                errCount += 1
                continue

            save_kline_data(symbol, base, quote, period, kdata)

        mysqlutil.log(TABLE, period, 'complete datetime >>>', datetime.datetime.now())
        mysqlutil.log(TABLE, period, '     time elapsed >>>', util.timeElapsed(startTimestamp))

    except:
        exCount += 1
        util.printExcept(target='get-' + TABLE + '-kline > save_kline')
    finally:
        cursor.close()
        db.close()


def get_kline():
    for p in PERIODS:
        save_kline(p)
    mysqlutil.log(TABLE, 'get_kline', 'time elapsed >>>', util.timeElapsed(startDate.timestamp()))


if __name__ == '__main__':

    while True:
        get_kline()
        runCount += 1
