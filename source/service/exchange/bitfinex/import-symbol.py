import socket
from urllib import request
import json
from chengutil import mysqlutil, util


def request_symbol():
    try:
        url = 'https://api.bitfinex.com/v1/symbols_details'
        print('url >>>', url)
        socket.setdefaulttimeout(20)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0"
        }
        req = request.Request(url, None, headers)
        response = request.urlopen(req)
        content = response.read().decode('utf-8')

        print('content >>>', content)
        symbol = json.loads(content)
        # symbol = symbol['data']
        print('data len >>>', len(symbol))
        return symbol
    except:
        util.printExcept()
        return False


db = mysqlutil.init()
cursor = db.cursor()

try:

    symbol = request_symbol()
    for s in symbol:
        sql = '''
        SELECT COUNT(id) FROM `xcm_bitfinex_symbol` WHERE pair=%s'''
        cursor.execute(sql, (s['pair']))
        rows = cursor.fetchall()
        if rows[0][0] > 0:
            continue

        print('symbol >>>', s)
        sql = '''
        INSERT INTO `xcm_bitfinex_symbol` 
        (pair, price_precision, initial_margin, minimum_margin, maximum_order_size, 
        minimum_order_size, expiration, margin) 
        VALUES 
        (%s, %s, %s, %s, %s, 
        %s, %s, %s)'''
        param = (s['pair'], s['price_precision'], s['initial_margin'], s['minimum_margin'], s['maximum_order_size'],
                 s['minimum_order_size'], s['expiration'], str(s['margin']))
        print(param)
        cursor.execute(sql, param)

    db.commit()
    print('\n### successed ###\n')
except:
    util.printExcept()
finally:
    cursor.close()
    db.close()
