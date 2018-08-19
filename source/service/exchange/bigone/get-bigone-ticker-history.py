import socket
from urllib import request
import json
from chengutil import mysqlutil, util
import time, datetime
import _thread

total = 0


def request_ticker_rest(symbol):
    url = 'https://big.one/api/v2/markets/%s/ticker' % (symbol)
    content = request_rest(url, 'bigone')
    if type(content) == dict and 'data' in content:
        content = content['data']
    return content


def request_ping_rest():
    url = 'https://big.one/api/v2/ping'
    content = request_rest(url, 'bigone')
    if type(content) == dict and 'timestamp' in content:
        content = content['timestamp']
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

        if 'errors' in content:
            mysqlutil.log(logTable, '\033[0;30;41m', 'content >>>', content, '\033[0m')
            return False
        else:
            mysqlutil.log(logTable, 'content >>>', content)
            mysqlutil.log(logTable, 'data len >>>', len(content))
            return content
    except:
        util.printExcept()
        time.sleep(3)
        return False


def get_ticker_history():

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        sql = 'SELECT symbol, base, quote FROM xcm_bigone_symbol'
        cursor.execute(sql)
        symbols = cursor.fetchall()

        symbolCount = 0

        for r in symbols:
            symbol = r[0]
            base = r[1]
            quote = r[2]

            symbolCount += 1

            ticker = request_ticker_rest(symbol)
            timestamp = request_ping_rest()

            mysqlutil.log('bigone', symbol, 'symbol precentage >>>', symbolCount, '/', len(symbols))
            mysqlutil.log('bigone', symbol, '        timestamp >>>', util.getLocaleDateStrDefault(timestamp/1000000000))

            nowTime = time.time() * 10000000

            sql = '''
            INSERT INTO xcm_bigone_ticker_history
            (
              _id, symbol, base, quote, 
              ts, open, high, low, close, volume, daily_change, daily_change_perc
            )
            VALUES
            (
              %s, %s, %s, %s, 
              %s, %s, %s, %s, %s, %s, %s, %s
            )'''
            param = (nowTime, symbol, base, quote,
                     timestamp, ticker['open'], ticker['high'], ticker['low'], ticker['close'], ticker['volume'],
                     ticker['daily_change'], ticker['daily_change_perc'])

            cursor.execute(sql, param)
            db.commit()

            global total
            total += 1

            mysqlutil.log('bigone', '\033[0;30;43m', symbol, '  begin date >>>', beginDate, '\033[0m')
            mysqlutil.log('bigone', '\033[0;30;43m', symbol, 'current date >>>', str(datetime.datetime.now()), ' \033[0m')
            mysqlutil.log('bigone', '\033[0;30;42m', symbol, '       total >>> {:,}'.format(total), ' \033[0m')

    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    global beginDate
    beginDate = str(datetime.datetime.now())

    while True:
        get_ticker_history()

