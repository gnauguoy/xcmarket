from urllib import request, parse
import json
import re
import mysqlutil
import sys


def get_feixiaohao_currency_fullname():

    db = mysqlutil.init()
    cursor = db.cursor()

    index = 1
    currencies = {}

    while index <= 13:

        print(index)

        url = 'https://www.feixiaohao.com/currencies/list_%d.html'%(index)
        response = request.urlopen(url)
        content = response.read().decode('utf-8')

        # print('\n', content, '\n')

        regex = r'\<td\>\<a href="\/currencies\/(.+?)\/" target=_blank\>.*?\<img.*?alt=(.*?)\>'
        # matchObj = re.search(regex, content, re.I)
        # fullname = matchObj.group(1)
        # print(fullname)
        # cnname = matchObj.group(2)
        # cnname = cnname.split('-')
        # print(cnname)

        matchObj = re.findall(regex, content, re.I)
        print(len(matchObj))

        for c in matchObj:
            currencies[c[0]] = c[1]

        index += 1

    try:

        for k in currencies:
            tempCnName = currencies[k].split('-')
            currency = tempCnName[0].lower()
            cnname = tempCnName[0]
            if len(tempCnName) > 1:
                cnname += ',' + tempCnName[1]
            fullname = k
            
            sql = 'INSERT INTO xcm_vxn_currency (currency, fullname, cnname) VALUES (%s, %s, %s)'
            cursor.execute(sql, (currency, fullname, cnname))
            # db.commit()
    except:
        print(sys.exc_info()[0])
    finally:
        pass

    cursor.close()
    db.close()
    # print(currencies)
    print(len(currencies))


get_feixiaohao_currency_fullname()