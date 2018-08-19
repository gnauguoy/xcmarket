import websocket

try:
    import thread
except ImportError:
    import _thread as thread
import time, datetime, json
import threading
from chengutil import mysqlutil, util

count = 0


def on_message(ws, message):
    # print('date >>>', datetime.datetime.now())
    # print(message)

    data = json.loads(message)
    if 'event' not in data:
        pass

    db = mysqlutil.init()
    cursor = db.cursor()

    # print('data len >>>', len(data))

    for d in data:

        try:

            # 将行情数据（ticker）保存在数据库中
            if 'channel' in d and d['channel'].find('_ticker') != -1:

                global count
                count += 1
                # print('count >>>', count)

                channel = d['channel']
                channel = channel.split('_')
                base = channel[3]
                quote = channel[4]
                symbol = base + '_' + quote

                t = d['data']

                sql = 'SELECT _id FROM xcm_okex_ticker WHERE symbol=%s'
                cursor.execute(sql, (symbol))
                rows = cursor.fetchall()

                if len(rows) == 0:
                    sql = '''
                    INSERT INTO xcm_okex_ticker (
                        symbol,base_currency,quote_currency,
                        buy,high,last,low,sell,timestamp,vol) 
                    VALUES (
                        %s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s)'''
                    param = (
                        symbol, base, quote,
                        t['buy'], t['high'], t['last'], t['low'], t['sell'], t['timestamp'], t['vol'])
                    cursor.execute(sql, param)
                    # print('insert >>>', symbol)
                else:
                    sql = '''
                    UPDATE xcm_okex_ticker SET 
                        buy=%s,high=%s,last=%s,low=%s,sell=%s,timestamp=%s,vol=%s
                    WHERE symbol=%s'''
                    param = (
                        t['buy'], t['high'], t['last'], t['low'], t['sell'], t['timestamp'], t['vol'],
                        symbol)
                    cursor.execute(sql, param)
                    # print('update >>>', symbol)
                # print(sql)
                db.commit()
        except:
            util.printExcept()
        finally:
            cursor.close()
            db.close()


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("\n### okex closed ###\n")
    # timer.cancel()


def on_open(ws):
    print('\n### okex connected ###\n')

    def run(*args):

        # 批量订阅所有的交易对行情
        subscribe = []

        db = mysqlutil.init()
        cursor = db.cursor()

        try:

            sql = 'SELECT symbol FROM xcm_okex_symbol'
            cursor.execute(sql)
            rows = cursor.fetchall()
            for r in rows:
                subscribe.append({'event': 'addChannel', 'channel': 'ok_sub_spot_' + r[0] + '_ticker'})
        except:
            util.printExcept()
        finally:
            cursor.close()
            db.close()

        # print('subscribe >>>', json.dumps(subscribe))
        print('send subscribe')
        ws.send(json.dumps(subscribe))
        # ws.send("["+
        # "{'event':'addChannel','channel':'ok_sub_spot_bch_btc_kline_1min'}, "+
        # "{'event':'addChannel','channel':'ok_sub_spot_bch_btc_kline_5min'}]")

    thread.start_new_thread(run, ())

    ping_timer(ws)


ws = 0
timer = 0


# 发送心跳
def ping_timer(ws):

    global timer

    if not ws.sock:
        timer.cancel()
        return

    print('send ping')
    print('date >>>', datetime.datetime.now())
    ping = '{"event":"ping"}'
    ws.send(ping)

    def run():
        timer = threading.Timer(20, ping_timer, (ws,))
        timer.start()

    thread.start_new_thread(run, ())


def init():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://real.okex.com:10441/websocket",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


if __name__ == "__main__":
    init()
