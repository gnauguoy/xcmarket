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
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("\n### binance closed ###\n")


def on_open(ws):
    print('\n### binance connected ###\n')


def init():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/stream?streams=bnbbtc@aggTrade/ethbtc@aggTrade",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


if __name__ == "__main__":
    init()
