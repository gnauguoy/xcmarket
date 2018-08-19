from chengutil import mysqlutil, util


def get_symbols():

    db = mysqlutil.init()
    cursor = db.cursor()

    try:

        sql = 'SELECT symbol, base, quote FROM xcm_fcoin_symbol'
        cursor.execute(sql)
        symbols = cursor.fetchall()
        return symbols
    except:
        util.printExcept()
    finally:
        cursor.close()
        db.close()

    return False
