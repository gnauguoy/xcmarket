import util
import time


def log():

    try:
        count = 0
        while count < 5:
            util.logToFile('', 'daemon_' + str(count) + '_', '/tmp/')
            count += 1
            time.sleep(1)
    except:
        util.printExcept()


util.daemonize(log)
# log()