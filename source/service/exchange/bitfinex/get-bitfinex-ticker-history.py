import socket
from urllib import request
import json
from chengutil import mysqlutil, util
import time, datetime
import _thread

total = 0
symbolCount = 0
runTime = 0


def request_ticker_rest(symbol):
    url = 'https://api.bitfinex.com/v1/pubticker/%s' % (symbol)
    content = request_rest(url, 'bitfinex')
    return content


def request_rest(url, logTable):
    try:

        mysqlutil.log(logTable, url)
        socket.setdefaulttimeout(20)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0",
        }
        req = request.Request(url, None, headers)
        response = request.urlopen(req)
        mysqlutil.log(logTable, 'response code >>>', response.code)
        content = response.read().decode('utf-8')

        content = json.loads(content)

        if 'message' in content:
            mysqlutil.log(logTable, '\033[0;30;41m', 'content >>>', content, '\033[0m')
            return False
        else:
            mysqlutil.log(logTable, 'content >>>', content)
            mysqlutil.log(logTable, 'data len >>>', len(content))
            return content
    except:
        util.printExcept()
        sleep(30)
        return False

def sleep(sec):
    if sec < 1:
        return
    count = 0
    while count < sec:
        count += 1
        print('sleep >>>', count)
        time.sleep(1)


def get_ticker_history():
    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        sql = 'SELECT pair FROM xcm_bitfinex_symbol'
        cursor.execute(sql)
        symbols = cursor.fetchall()

        global symbolCount, runTime
        symbolCount = 0
        runTime = 0

        for r in symbols:
            symbol = r[0]

            mysqlutil.log('bitfinex', symbol, '          runTime >>>', runTime)
            # if runTime == 5:
            #     runTime = 0
            #     sleep(10)
            ticker = request_ticker_rest(symbol)
            if ticker == False:
                ticker = request_ticker_rest(symbol)
            # runTime += 1
            sleep(3)

            symbolCount += 1

            mysqlutil.log('bitfinex', symbol, 'symbol precentage >>>', symbolCount, '/', len(symbols))
            mysqlutil.log('bitfinex', symbol, 'ticker  timestamp >>>', ticker['timestamp'])
            mysqlutil.log('bitfinex', symbol, 'ticker  timestamp >>>',
                          util.getLocaleDateStrDefault(int(float(ticker['timestamp']))))

            nowTime = time.time() * 10000000

            sql = '''
            INSERT INTO xcm_bitfinex_ticker_history
            (
              _id, pair, 
              mid, bid, ask, last_price, low, 
              high, volume, ts
            )
            VALUES
            (
              %s, %s, 
              %s, %s, %s, %s, %s, %s, %s, %s
            )'''
            param = (nowTime, symbol,
                     ticker['mid'], ticker['bid'], ticker['ask'], ticker['last_price'], ticker['low'],
                     ticker['high'], ticker['volume'], ticker['timestamp'])

            cursor.execute(sql, param)
            db.commit()

            global total
            total += 1

            mysqlutil.log('bitfinex', '\033[0;30;43m', symbol, '  begin date >>>', beginDate, '\033[0m')
            mysqlutil.log('bitfinex', '\033[0;30;43m', symbol, 'current date >>>', str(datetime.datetime.now()), ' \033[0m')
            mysqlutil.log('bitfinex', '\033[0;30;42m', symbol, '       total >>> {:,}'.format(total), '\033[0m')

    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()

def get_total(tableName):

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        global total

        if total == 0:
            sql = 'SELECT count(_id) FROM %s'%(tableName)
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



if __name__ == '__main__':
    global beginDate
    beginDate = str(datetime.datetime.now())

    get_total('xcm_bitfinex_ticker_history')

    while True:
        get_ticker_history()
