import time, sys, os
from chengutil import util

# f = open('log-'+str(int(time.time()*1000000)), 'w')
# f = open('log-'+util.getLocaleDateStrDefault(time.time(),'_'), 'w')
# f.write(str(time.time())+'\nHello file write')
# f.close()

try:
    raise NameError('test log')
except:
    print(sys.exc_info()[0])
    filename = os.path.basename(sys.argv[0]).split(".")[0]
    util.printExcept(filename)

# print(os.path.basename(sys.argv[0]).split(".")[0])
# print(sys.argv[0])