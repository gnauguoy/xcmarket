# final date: 2018-07-14
# desc: 此版本已经可以获取 1min K线，进而保存到数据库表。
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
import json
import util,mysqlutil


def on_open(ws):

    print('### connected ###')

    def run(*args):
        nowTime = int(time.time() * 1000000)
        ws.send(
            '{"sub": "market.btcusdt.kline.1min","id": "kline_' + str(nowTime) + '"}')
        # ws.send('{"sub": "market.btcusdt.kline.5min","id": "kline_'+nowTime+'"}')

        # fromTimeStamp = getTimeStamp('2018-1-1 00:00:01')
        # toTimeStamp = getTimeStamp('2018-1-1 00:10:00')
        # print timeStamp
        # ws.send('{"req": "market.btcusdt.kline.1min","id": "kline_' + str(nowTime) + '","from":'+str(fromTimeStamp)+',"to":'+str(toTimeStamp)+'}')

        # ws.send(
        #     '{"req": "market.btcusdt.kline.1min","id": "kline_' + str(nowTime) + '"}')
    thread.start_new_thread(run, ())


def on_message(ws, message):

    message = util.gzip_uncompress(message)
    message = message.decode('ascii')

    # print('==========> message ===> ' + message)

    jsonObj = json.loads(message)

    if ('ping' in jsonObj) == True:
        pong = '{"pong":' + str(jsonObj['ping']) + '}'
        ws.send(pong)
    elif ('ch' in jsonObj) == True:
        # 将交易对的实时 kline 写入表中
        result = mysqlutil.insertHuobiProKline(message)
        print(result, util.getLocaleDateStr(jsonObj['ts']))
    elif ('rep' in jsonObj) == True:
        print(len(jsonObj['data']))
    else:
        pass


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "wss://api.huobi.pro/ws", on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
