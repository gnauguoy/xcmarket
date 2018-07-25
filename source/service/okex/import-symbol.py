import pymysql, json, sys, csv
from chengutil import mysqlutil,util
 
db = mysqlutil.init()
cursor = db.cursor()


try:

    with open('okex_symbol.csv') as f:
        symbol = csv.reader(f)
        header = next(symbol)
        for s in symbol:
            # print(s)
            sql = '''
            INSERT INTO `xcm_okex_symbol` 
            (product_id,symbol,base_min_size,base_increment,quote_increment,base_currency,quote_currency) 
            VALUES (%s,%s,%s,%s,%s,%s,%s)'''
            c = s[1].split('_')
            cursor.execute(sql, (s[0], s[1], s[2], s[3], s[4], c[0], c[1]))

    db.commit()
    print('\n### successed ###\n')
except:
    util.printExcept()
finally:
    cursor.close()
    db.close()
