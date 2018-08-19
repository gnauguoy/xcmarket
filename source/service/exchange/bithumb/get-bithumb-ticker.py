import socket
from urllib import request
import json
from chengutil import mysqlutil, util
import time, datetime
import _thread

total = 0


def request_ticker_rest():
    url = 'https://api.bithumb.com/public/ticker/ALL'
    content = request_rest(url, 'bithumb')
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


def get_ticker():
    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        tickers = request_ticker_rest()
        if tickers['status'] != '0000':
            mysqlutil.log('bithumb', '\033[0;30;41m', 'content >>>', tickers, '\033[0m')
            return False
        else:
            # mysqlutil.log('bithumb', 'content >>>', tickers)
            tickers = tickers['data']
            mysqlutil.log('bithumb', 'data len >>>', len(tickers))

        for c in tickers:

            if c == 'date':
                continue

            nowTime = time.time() * 10000000

            sql = '''
            INSERT INTO xcm_bithumb_ticker
            (
              _id, currency, 
              opening_price, closing_price, min_price, max_price, average_price, 
              units_traded, volume_1day, volume_7day, buy_price, sell_price, 
              24H_fluctate, 24H_fluctate_rate, ts
            )
            VALUES
            (
              %s, %s, 
              %s, %s, %s, %s, %s, 
              %s, %s, %s, %s, %s, 
              %s, %s, %s
            )'''
            ticker = tickers[c]
            # mysqlutil.log('bithumb', '\033[0;30;43m', c, '              ticker >>>', ticker)
            param = (nowTime, c,
                     ticker['opening_price'], ticker['closing_price'], ticker['min_price'], ticker['max_price'], ticker['average_price'],
                     ticker['units_traded'], ticker['volume_1day'], ticker['volume_7day'], ticker['buy_price'], ticker['sell_price'],
                     ticker['24H_fluctate'], ticker['24H_fluctate_rate'], tickers['date'])

            cursor.execute(sql, param)
            db.commit()

            global total
            total += 1

        mysqlutil.log('bithumb', '\033[0;30;43m', '  begin date >>>', beginDate, '\033[0m')
        mysqlutil.log('bithumb', '\033[0;30;43m', 'current date >>>', str(datetime.datetime.now()), ' \033[0m')
        mysqlutil.log('bithumb', '\033[0;30;42m', '       total >>> {:,}'.format(total), '\033[0m')

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

        mysqlutil.log('bithumb', '\ntotal >>> {:,}'.format(total))
    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()



if __name__ == '__main__':
    global beginDate
    beginDate = str(datetime.datetime.now())

    get_total('xcm_bithumb_ticker')

    while True:
        get_ticker()
        # sleep(3)
