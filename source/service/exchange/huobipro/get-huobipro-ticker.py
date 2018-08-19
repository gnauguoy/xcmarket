# version 2018-08-19 17:53
import pymysql
from chengutil import mysqlutil, util, CommonApi
import time, datetime

startDate = datetime.datetime.now()
exCount = 0
runCount = 0
primaries = []
dupCount = 0
timeErrCount = 0

TABLE = 'huobipro'


def save_ticker():
    global exCount, dupCount, timeErrCount

    startTimestamp = time.time()

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        nowTime = time.time() * 10000000

        symbols = CommonApi.get_symbols(TABLE, 'dict')
        tickers = CommonApi.get_ticker('https://api.huobi.pro/market/tickers')

        if tickers['status'] == 'error':
            # 打印请求返回的错误信息
            mysqlutil.log(TABLE, startDate, 'save_ticker error >>>', tickers)
            exCount += 1

        sql = 'INSERT INTO xcm_' + TABLE + '_ticker ('
        sql += '''
                _id, symbol, base, quote, 
                open, high, low, close, amount, vol, count, ts)
            VALUES (
                %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s)
            '''

        tickerCount = 0
        dupCurCount = 0

        ts = tickers['ts']
        tickers = tickers['data']

        for t in tickers:
            symbol = t['symbol']

            # 去除非正常的交易对 huobi10/hb10
            if symbol == 'huobi10' or symbol == 'hb10':
                continue

            base = symbols[symbol]['base']
            quote = symbols[symbol]['quote']

            primary = symbol + '-' + str(ts) + '-' + base + '-' + quote + '-'
            if primary in primaries:
                dupCount += 1
                dupCurCount += 1
                continue

            primaries.append(primary)

            param = (nowTime, symbol, base, quote,
                     t['open'], t['high'], t['low'], t['close'], t['amount'], t['vol'], t['count'], ts)
            try:
                cursor.execute(sql, param)
                db.commit()
            except pymysql.err.IntegrityError:
                dupCount += 1
                dupCurCount += 1
                exCount += 1
                continue

            tickerCount += 1
            util.dprint(startDate, symbol, 'tickerCount:', tickerCount, '/ len:', len(tickers), '/ dupCurCount:',
                        dupCurCount, '/ dupCount:', dupCount)

        util.dprint(startDate, datetime.datetime.now(), 'completed',
                    '\nnewCount:', tickerCount, ' duplicateCurrentCount:', dupCurCount, ' exCount:', exCount,
                    ' timeErrCount:', timeErrCount, ' runCount:', runCount, ' timeSpan:',
                    util.timeElapsed(startTimestamp), ' totalSpan:', util.timeElapsed(startDate.timestamp()))
        print()

        return True

    except:
        exCount += 1
        util.printExcept(target='get-' + TABLE + '-kline > save_ticker')
    finally:
        cursor.close()
        db.close()

    return False


if __name__ == '__main__':

    while True:
        runCount += 1
        save_ticker()
