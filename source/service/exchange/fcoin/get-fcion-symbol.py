import fcoin
from chengutil import mysqlutil, util


api = fcoin.authorize('key', 'secret')
print(api.server_time())

symbol = api.symbols()
symbol = symbol['data']
print('symbols len >>>', len(symbol))


db = mysqlutil.init()
cursor = db.cursor()

try:

    for s in symbol:
        sql = '''
            SELECT COUNT(_id) FROM `xcm_fcoin_symbol` WHERE symbol=%s'''
        cursor.execute(sql, (s['name']))
        rows = cursor.fetchall()
        if rows[0][0] > 0:
            continue

        print('symbol >>>', s['name'])
        sql = '''
            INSERT INTO `xcm_fcoin_symbol` 
            (symbol, base, quote, price_decimal, amount_decimal) 
            VALUES (%s, %s, %s, %s, %s)'''
        param = (s['name'], s['base_currency'], s['quote_currency'], s['price_decimal'], s['amount_decimal'])
        print(param)
        cursor.execute(sql, param)

    db.commit()
    print('\n### successed ###\n')
except:
    util.printExcept()
finally:
    cursor.close()
    db.close()
