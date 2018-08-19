# version 2018-08-19 17:53
import gzip
import io
import json
import time
import sys
import traceback
import os
import platform
from chengutil import mysqlutil


# 解压缩
def gzip_uncompress(c_data):
    buf = io.BytesIO(c_data)
    f = gzip.GzipFile(mode='rb', fileobj=buf)
    try:
        r_data = f.read()
    finally:
        f.close()
    return r_data


# 将日期字符串转换为时间戳
# 示例：dateStr = '2018-1-1 00:00:00'
def getTimeStamp(dateStr, format="%Y-%m-%d %H:%M:%S"):

    try:
        # 转为时间数组
        timeArray = time.strptime(dateStr, format)
        # 转为时间戳
        timeStamp = int(time.mktime(timeArray))
        return timeStamp
    except:
        printExcept(target='util > getTimeStamp', msg="dateStr: " + dateStr)
        # ex_type, ex_val, ex_stack = sys.exc_info()
        # raise Exception("Exception in util > getTimeStamp dateStr: " + dateStr + "\n EX_VAL: " + str(ex_val))
        return False


def getTimeStampReturn13(dateStr, format="%Y-%m-%d %H:%M:%S"):
    timeStamp = getTimeStamp(dateStr, format)
    return timeStamp * 1000


# 将时间戳转换为日期字符串
def getLocaleDateStr(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp/1000))


def getLocaleDateStrBy16(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp/1000000))


def getLocaleDateStrBy13(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp/1000))


def getLocaleDateStrBy10(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))


def getLocaleDateStrDefault(timestamp, sep=' '):
    return time.strftime('%Y-%m-%d'+sep+'%H:%M:%S', time.localtime(timestamp))


# 打印抛出错误信息，并记录日志。
def printExcept(filename='', logdir='/tmp/xcmarket_log/', target='', msg=''):

    if logdir == '/tmp/exlog/' and platform.system() == 'Windows':
        logdir = 'C:\\Windows\\Temp\\xcmarket_log\\'

    if filename == '':
        filename = os.path.basename(sys.argv[0]).split(".")[0]

    ex_type, ex_val, ex_stack = sys.exc_info()

    log = 'EXCEPTION \n'
    log += '    EX_TYPE  : ' + str(ex_type) + ' \n'
    log += '    EX_VAL   : ' + str(ex_val) + ' \n'
    log += '    EX_TRACK : \n'
    for stack in traceback.extract_tb(ex_stack):
        log += '        ' + str(stack) + ' \n'

    prefix = 'EX_LOG_'
    if filename != '':
        prefix += filename + '_'
    logToFile(log, prefix, logdir)

    mysqlutil.logToExcept(log, target, msg)


# 将日志信息记录在文件中
def logToFile(logStr, prefix='log_', dir='/tmp/xcmarket_log/'):

    if dir == '/tmp/exlog/' and platform.system() == 'Windows':
        dir = 'C:\\Windows\\Temp\\xcmarket_log\\'

    if os.path.exists(dir) == False:
        os.makedirs(dir)

    fileName = getLocaleDateStrDefault(time.time(), '_')
    fileName = fileName.replace(':', '')
    fileName = dir + prefix + fileName
    f = open(fileName, 'w')
    f.write(logStr)
    f.close()


def getCurrentFilename():
    return os.path.basename(sys.argv[0]).split(".")[0]


# 启动守护进程
def daemonize(func):

    # 从父进程fork一个子进程出来
    pid = os.fork()
    # 子进程的pid一定为0，父进程大于0
    if pid:
        # 退出父进程，sys.exit()方法比os._exit()方法会多执行一些刷新缓冲工作
        # mysqlutil.log('binance', 'fork pid >>>',pid)
        pidStr = 'RUN_' + getCurrentFilename() + '_pid_' + str(pid)
        logToFile(pidStr, pidStr + '_')
        sys.exit(0)

    # 子进程默认继承父进程的工作目录，最好是变更到根目录，否则回影响文件系统的卸载
    os.chdir('/')
    # 让子进程成为新的会话组长和进程组长
    os.setsid()
    # 子进程默认继承父进程的umask（文件权限掩码），重设为0（完全控制），以免影响程序读写文件
    os.umask(0)

    # 注意了，这里是第2次fork，也就是子进程的子进程，我们把它叫为孙子进程
    _pid = os.fork()
    if _pid:
        # 退出子进程
        pidStr = 'RUN_' + getCurrentFilename() + '_pid_' + str(_pid)
        logToFile(pidStr, pidStr + '_')
        sys.exit(0)

    # 此时，孙子进程已经是守护进程了，接下来重定向标准输入、输出、错误的描述符(是重定向而不是关闭, 这样可以避免程序在 print 的时候出错)

    # 刷新缓冲区先，小心使得万年船
    sys.stdout.flush()
    sys.stderr.flush()

    # dup2函数原子化地关闭和复制文件描述符，重定向到/dev/nul，即丢弃所有输入输出
    with open('/dev/null') as read_null, open('/dev/null', 'w') as write_null:
        os.dup2(read_null.fileno(), sys.stdin.fileno())
        os.dup2(write_null.fileno(), sys.stdout.fileno())
        os.dup2(write_null.fileno(), sys.stderr.fileno())

    # 执行被守护的函数
    func()


# 休眠并打印休眠时间
def sleep(sec, show = True):
    if sec < 1:
        return
    count = 0
    while count < sec:
        count += 1
        if show:
            print('sleep >>>', count)
        time.sleep(1)


def timeElapsed(startTimestamp):
    sSpan = time.time() - startTimestamp
    span = str(int(round(sSpan, 0))) + 's'

    # 将耗时时长格式化为分钟数
    mSpan = sSpan / 60
    if mSpan < 1:
        return span

    span = str(int(round(mSpan, 0))) + 'm'

    # 将耗时时长格式化为小时数
    hSpan = mSpan / 60
    if hSpan < 1:
        return span

    span = str(int(round(hSpan, 0))) + 'h'

    # 将耗时时长格式化为天数
    dSpan = hSpan / 24
    if dSpan < 1:
        return span

    span = str(int(round(dSpan, 0))) + 'd'

    return span


def dprint(*param):
    msg = ''
    for m in param:
        msg += str(m) + ' '
    msg = bytes("\r" + msg, encoding="utf8")
    os.write(1, msg)
    sys.stdout.flush()

