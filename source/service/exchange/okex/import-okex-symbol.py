import csv
from chengutil import mysqlutil,util


def import_okex_symbol(csvFile):
    db = mysqlutil.init()
    cursor = db.cursor()


    try:

        count = 0

        with open(csvFile,'r',encoding='UTF-8') as f:
            symbol = csv.reader(f)
            header = next(symbol)
            for s in symbol:
                # print(s)
                sql = '''
                    SELECT COUNT(_id) FROM `xcm_okex_symbol` WHERE symbol=%s'''
                cursor.execute(sql, (s[1]))
                rows = cursor.fetchall()
                # print(rows[0][0])
                if rows[0][0] > 0:
                    continue

                sql = '''
                INSERT INTO `xcm_okex_symbol` 
                (product_id,symbol,base_min_size,base_increment,quote_increment,base,quote) 
                VALUES (%s,%s,%s,%s,%s,%s,%s)'''
                c = s[1].split('_')
                cursor.execute(sql, (s[0], s[1], s[2], s[3], s[4], c[0], c[1]))

                db.commit()
                count += 1

        print('insert >>>', count)
        print('\n### successed ###\n')
    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    import_okex_symbol('okex_symbol.csv')