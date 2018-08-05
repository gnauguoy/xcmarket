import websocket

try:
    import thread
except ImportError:
    import _thread as thread
import time, datetime, json
import threading
from chengutil import mysqlutil, util


class OKExWebSocket:

    count = 0
    ws = 0
    timer = 0
    myPeriod = 0

    def on_message(self, ws, message):
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

                # 将K线数据（kline）保存在数据库中
                if 'channel' in d and d['channel'].find('_kline_') != -1:

                    self.count += 1
                    print('count >>>', self.myPeriod, self.count)

                    channel = d['channel']
                    channel = channel.split('_')
                    base = channel[3]
                    quote = channel[4]
                    symbol = base + '_' + quote
                    period = channel[6]

                    nowTime = time.time()
                    nowTime *= 1000000

                    klines = d['data']

                    for k in klines:
                        sql = '''
                        INSERT INTO xcm_okex_kline (
                            _id, symbol,base_currency,quote_currency,period,
                            timestamp,open,high,low,close,vol) 
                        VALUES (
                            %s,%s,%s,%s,%s,
                            %s,%s,%s,%s,%s,%s)'''
                        param = (
                            nowTime, symbol, base, quote, period,
                            k[0], k[1], k[2], k[3], k[4], k[5])
                        cursor.execute(sql, param)
                        print('insert >>>', symbol)
                        # print(sql)
                    db.commit()
            except:
                util.printExcept()
            finally:
                cursor.close()
                db.close()

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("\n### okex closed ###\n")
        self.timer.cancel()

    def on_open(self, ws):
        print('\n### okex connected ###\n')

        def run(*args):

            # 批量订阅所有的交易对K线数据
            subscribe = []

            db = mysqlutil.init()
            cursor = db.cursor()

            try:

                sql = 'SELECT symbol FROM xcm_okex_symbol'
                cursor.execute(sql)
                rows = cursor.fetchall()
                for r in rows:
                    subscribe.append({'event': 'addChannel', 'channel': 'ok_sub_spot_' + r[0] + '_kline_' + self.myPeriod})
            except:
                util.printExcept()
            finally:
                cursor.close()
                db.close()

            print('subscribe >>>', json.dumps(subscribe))
            print('send subscribe')
            ws.send(json.dumps(subscribe))

        thread.start_new_thread(run, ())

        self.ping_timer(ws)

    # 发送心跳
    def ping_timer(self, ws):

        if not ws.sock:
            self.timer.cancel()
            return

        print('send ping')
        print('date >>>', datetime.datetime.now())
        ping = '{"event":"ping"}'
        ws.send(ping)

        def run():
            self.timer = threading.Timer(20, self.ping_timer, (ws,))
            self.timer.start()

        thread.start_new_thread(run, ())

    def init(self, period):

        self.myPeriod = period

        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://real.okex.com:10441/websocket",
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()


def get_kline(period):
    okexWs = OKExWebSocket()
    okexWs.init(period)
