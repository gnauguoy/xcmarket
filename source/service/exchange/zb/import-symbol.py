import socket
from urllib import request
import json
from chengutil import mysqlutil, util


def request_zb_symbol():
    try:
        url = 'http://api.zb.cn/data/v1/markets'
        print(url)
        socket.setdefaulttimeout(20)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0"
        }
        req = request.Request(url, None, headers)
        response = request.urlopen(req)
        content = response.read().decode('utf-8')

        # print(content)
        symbol = json.loads(content)
        print('data len >>>', len(symbol))
        return symbol
    except:
        util.printExcept()
        return False


db = mysqlutil.init()
cursor = db.cursor()

try:

    symbol = request_zb_symbol()
    for s in symbol:
        sql = '''
        SELECT COUNT(_id) FROM `xcm_zb_symbol` WHERE symbol=%s'''
        cursor.execute(sql, (s))
        rows = cursor.fetchall()
        if rows[0][0] > 0:
            continue

        print('symbol >>>', s)
        ary = s.split('_')
        base = ary[0]
        quote = ary[1]
        sql = '''
        INSERT INTO `xcm_zb_symbol` 
        (symbol,base,quote,amount_scale,price_scale) 
        VALUES (%s,%s,%s,%s,%s)'''
        cursor.execute(sql, (
            s, base, quote, symbol[s]['amountScale'], symbol[s]['priceScale']))

    db.commit()
    print('\n### successed ###\n')
except:
    util.printExcept()
finally:
    cursor.close()
    db.close()
