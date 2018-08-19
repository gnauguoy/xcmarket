import fcoin
from chengutil import mysqlutil, util, fcoin as cfcoin
import time, datetime

api = fcoin.authorize('key', 'secret')
startDate = datetime.datetime.now()
exCount = 0
runCount = 0


def save_ticker_record(symbol, base, quote, t):
    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        nowTime = time.time() * 10000000
        ts = api.server_time()
        if ts['status'] != 0:
            return False

        ts = ts['data']
        sql = '''
            INSERT INTO xcm_fcoin_ticker (
                _id, symbol, base, quote, ts, 
                last, last_volume, max_bid, max_bid_volume, min_ask, min_ask_volume, 
                24h_ago_last, high, low, 24h_base_volume, 24h_quote_volume)
            VALUES (
                %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s)'''
        param = (
            nowTime, symbol, base, quote, ts,
            t[0], t[1], t[2], t[3], t[4], t[5],
            t[6], t[7], t[8], t[9], t[10])
        cursor.execute(sql, param)
        db.commit()

        return True

    except:
        global exCount
        exCount += 1
        util.printExcept(target='get-fcoin-kline > save_ticker')
    finally:
        cursor.close()
        db.close()

    return False


def save_ticker():

    startTimestamp = time.time()

    symbols = cfcoin.get_symbols()
    count = 0

    symbolCount = 0

    for s in symbols:

        symbol = s[0]
        base = s[1]
        quote = s[2]

        # 打印当前处理的交易对和处理进度
        symbolCount += 1
        # mysqlutil.log('fcoin', '\033[0;30;42m', startDate, 'symbol >>>', symbol, symbolCount, '/', len(symbols),
        #               '\033[0m')
        util.dprint('\033[0;30;42m', startDate, 'symbol >>>', symbol, symbolCount, '/', len(symbols), '\033[0m')

        try:
            ticker = api.market.get_ticker(symbol)
        except:
            util.printExcept(target='get-fcoin-ticker > get_ticker')
            time.sleep(10)
            continue

        # 访问太过频繁，超过了每 10 秒钟 100 次的限制，先暂停休眠 10 秒钟。
        if ticker['status'] == 429:
            time.sleep(10)
        if ticker['status'] != 0:
            # 打印请求返回的错误信息
            mysqlutil.log('fcoin', startDate, symbol, 'get_ticker error >>>', ticker)
            continue

        ticker = ticker['data']['ticker']
        save_ticker_record(symbol, base, quote, ticker)

        count += 1
        if count % 10 == 0:
            util.sleep(1, False)

    print()
    mysqlutil.log('fcoin', 'complete datetime >>>', datetime.datetime.now())
    mysqlutil.log('fcoin', '     time elapsed >>>', util.timeElapsed(startTimestamp))
    mysqlutil.log('fcoin', '          exCount >>>', exCount, 'runCount >>>', runCount)
    mysqlutil.log('fcoin', '        startDate >>>', startDate)
    mysqlutil.log('fcoin', '    total elapsed >>>', util.timeElapsed(startDate.timestamp()))


if __name__ == '__main__':

    while True:
        save_ticker()
        runCount += 1
