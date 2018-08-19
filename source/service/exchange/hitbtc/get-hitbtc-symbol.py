import socket
from urllib import request
import json
from chengutil import mysqlutil, util

def request_hitbtc_symbol():
    try:
        url = 'https://api.hitbtc.com/api/2/public/symbol'
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


symbol = request_hitbtc_symbol()


db = mysqlutil.init()
cursor = db.cursor()

try:

    for s in symbol:
        sql = '''
            SELECT COUNT(_id) FROM `xcm_hitbtc_symbol` WHERE symbol=%s'''
        cursor.execute(sql, (s['id']))
        rows = cursor.fetchall()
        if rows[0][0] > 0:
            continue

        print('symbol >>>', s['id'])
        sql = '''
            INSERT INTO `xcm_hitbtc_symbol` 
            (symbol, base, quote, quantityIncrement, tickSize, 
            takeLiquidityRate, provideLiquidityRate, feeCurrency) 
            VALUES 
            (%s, %s, %s, %s, %s, 
            %s, %s, %s)'''
        param = (s['id'], s['baseCurrency'], s['quoteCurrency'], s['quantityIncrement'], s['tickSize'],
                 s['takeLiquidityRate'], s['provideLiquidityRate'], s['feeCurrency'])
        print(param)
        cursor.execute(sql, param)

    db.commit()
    print('\n### successed ###\n')
except:
    util.printExcept()
finally:
    cursor.close()
    db.close()
