# final date: 2018-07-14 09:14
# desc: 此版本已经可以定时获取 btcusdt 交易对 1min 的K线数据，并保存在数据库中。
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import threading
import time
import json
import util
import mysqlutil


def on_open(ws):

    print('\n### connected ###\n')
    nowTime = int(time.time() * 1000000)

    def run(*args):
        # print(nowTime)
        # ws.send(
        #     '{"sub": "market.btcusdt.kline.1min","id": "kline_' + str(nowTime) + '"}')
        # ws.send('{"sub": "market.btcusdt.kline.5min","id": "kline_'+nowTime+'"}')

        fromTimeStamp = util.getTimeStamp('2018-1-1 00:00:01')
        toTimeStamp = util.getTimeStamp('2018-1-1 00:10:00')
        ws.send('{"req": "market.btcusdt.kline.1min","id": "kline_' + str(nowTime) + '","from":'+str(fromTimeStamp)+',"to":'+str(toTimeStamp)+'}')

        # ws.send(
        #     '{"req": "market.btcusdt.kline.1min","id": "kline_' + str(nowTime) + '"}')

    # thread.start_new_thread(run, ())

    ts = util.getTimeStamp('2018-1-1 00:00:00')
    # get1MinKline(ws, timestamp)
    get1MinKlineTimer(1*60, ws, ts)


global timer

# 定时获取 1min K线数据
def get1MinKlineTimer(interval, ws, initTimestamp):
    
    global timer

    # 检查 websocket 是否已经关闭
    if not ws.sock:
        print('\n### websocket was closed. ###\n')
        timer.cancel()
        return

    get1MinKline(ws, initTimestamp)
    timer = threading.Timer(interval, get1MinKlineTimer, [interval, ws, initTimestamp])
    timer.start()


# 获取 1min K线数据
def get1MinKline(ws, initTimestamp):

    # 获取数据表中最后一条记录，获取它的时间戳，作为请求的开始时间戳。
    cursor = mysqlutil.getCursor()
    cursor.execute("SELECT id FROM xcm_huobi_kline_history WHERE period='1min' ORDER BY id DESC LIMIT 1")
    rows = cursor.fetchall()
    if len(rows) != 0:
        print('get1MinKline rows:', rows)
        fromTimeStamp = rows[0][0] + 1
    else:
        fromTimeStamp = initTimestamp

    nowTime = int(time.time() * 1000000)
    req = '{"req": "market.btcusdt.kline.1min","id": "kline_' + str(nowTime) + '","from":' + str(fromTimeStamp) + '}'
    print('get1MinKline req:', req)
    ws.send(req)

historySaveCount = 0

def on_message(ws, message):

    message = util.gzip_uncompress(message)
    message = message.decode('ascii')

    # print('==========> message ===> ' + message)

    jsonObj = json.loads(message)

    if ('ping' in jsonObj) == True:
        # 回应心跳检测
        pong = '{"pong":' + str(jsonObj['ping']) + '}'
        print('==========> ping ===> ' + str(jsonObj['ping']))
        ws.send(pong)
    elif ('ch' in jsonObj) == True:
        # 将交易对的实时 kline 写入数据表中
        result = mysqlutil.insertHuobiProKline(message)
        print(result, util.getLocaleDateStr(jsonObj['ts']))
    elif ('rep' in jsonObj) == True:

        data = jsonObj['data']
        print('on_message rep data len:', len(data))
        if len(data) == 0:
            return
        
        # 将交易对的历史 kline 写入表中
        result = mysqlutil.insertHuobiProKlineHistory(message)
        if type(result) == int:
            global historySaveCount
            historySaveCount += result
            print('historySaveCount:', historySaveCount)
        print('on_message insertHuobiProKlineHistory result:', result)

        # 获取最后一条K线的时间，继续发送请求，获取下一组数据。
        lastElemIndex = len(data) -1
        nextTimestamp = data[lastElemIndex]['id'] + 1
        # print(nextTimestamp)
        get1MinKline(ws, nextTimestamp)
    else:
        pass


def on_error(ws, error):
    print(error)


def on_close(ws):
    timer.cancel()
    print("\n### closed ###\n")


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "wss://api.huobi.pro/ws", on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
