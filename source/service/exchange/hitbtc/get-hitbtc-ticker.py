import re
import sys

import fcoin
import pymysql
from chengutil import mysqlutil, util, hitbtc as chitbtc
import time, datetime

api = fcoin.authorize('key', 'secret')
startDate = datetime.datetime.now()
exCount = 0
runCount = 0
primaries = []
dupCount = 0
timeErrCount = 0

TABLE = 'hitbtc'


def save_ticker():
    global exCount, dupCount, timeErrCount

    startTimestamp = time.time()

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        nowTime = time.time() * 10000000

        symbols = chitbtc.get_symbols('dict')
        tickers = chitbtc.get_ticker()

        # 访问太过频繁，超过了每 1 秒钟 100 次的限制，先暂停休眠 1 秒钟。
        if 'error' in tickers and tickers['error']['code'] == 429:
            time.sleep(1)
        if 'error' in tickers:
            # 打印请求返回的错误信息
            mysqlutil.log(TABLE, startDate, 'save_ticker error >>>', tickers)
            exCount += 1

        sql = '''
            INSERT INTO xcm_hitbtc_ticker (
                _id, symbol, base, quote, 
                ask, bid, open, high, low, last, 
                volume, volumeQuote, ts)
            VALUES (
                %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s)
            '''

        tickerCount = 0
        dupCurCount = 0

        for t in tickers:
            symbol = t['symbol']
            base = symbols[symbol]['base']
            quote = symbols[symbol]['quote']

            # 转换时间为时间戳
            ts = util.getTimeStampReturn13(t['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if ts == False:
                timeErrCount += 1
                util.printExcept(target='get-' + TABLE + '-kline > get_last_timestamp', msg=str(t))
                continue
            regex = r'.+?\.([0-9]{3})Z';
            matchObj = re.search(regex, t['timestamp'], re.I);
            ms = matchObj.group(1)
            ts += int(ms)

            primary = symbol + '-' + str(ts) + '-' + base + '-' + quote + '-'
            if primary in primaries:
                dupCount += 1
                dupCurCount += 1
                continue

            primaries.append(primary)

            param = (nowTime, symbol, base, quote,
                     t['ask'], t['bid'], t['open'], t['high'], t['low'], t['last'],
                     t['volume'], t['volumeQuote'], ts)
            try:
                cursor.execute(sql, param)
                db.commit()
            except pymysql.err.IntegrityError:
                # ex_type, ex_val, ex_stack = sys.exc_info()
                # print('EX_VAL: ' + str(ex_val))
                dupCount += 1
                dupCurCount += 1
                exCount += 1
                continue

            tickerCount += 1
            util.dprint(startDate, symbol, 'tickerCount:', tickerCount, '/ len:', len(tickers), '/ dupCurCount:', dupCurCount, '/ dupCount:', dupCount)

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
        save_ticker()
        runCount += 1
