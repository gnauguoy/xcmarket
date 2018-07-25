import pymysql, json, sys
import mysqlutil
 
db = mysql.init()
cursor = db.cursor()

f = open('huobi_symbol.json')
content = f.read()
# print(content)
f.close()

symbol = json.loads(content)
symbol = symbol['data']
print(len(symbol))

try:
    for s in symbol:
        sql = '''
        INSERT INTO `xcm_huobi_symbol` 
        (base_currency,quote_currency,price_precision,
        amount_precision,symbol,symbol_partition) 
        VALUES (%s,%s,%s,%s,%s,%s)'''
        cursor.execute(sql, (
            s['base-currency'],s['quote-currency'],s['price-precision'],
            s['amount-precision'],s['symbol'],s['symbol-partition']))

    db.commit()
except:
    print(sys.exc_info()[0])

db.close()
