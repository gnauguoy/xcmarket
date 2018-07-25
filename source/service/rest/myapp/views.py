from django.shortcuts import render
from django.http import HttpResponse
from myapp.models import *
import json
import pymysql
import sys
import traceback
from chengutil import mysqlutil, util


def hello(request, pageIndex=1, pageSize=10):

    # 传入页码
    # print(type(pageIndex), type(pageSize))
    # pageIndex = int(pageIndex)
    # pageSize = int(pageSize)
    # sites = mysite.objects.all()[pageIndex-1:pageSize]

    # 插入
    # m = mysite(title='baidu',num=1)
    # m.save()

    # m = mysite(title='google.com',num=3)
    # m.save()
    # m = mysite(title='twitter.com',num=2)
    # m.save()

    # 排序
    # sites = mysite.objects.all()
    # sites = mysite.objects.all().order_by('num')
    # print(sites[0].title)
    # str = ''
    # for s in sites:
    #     str += s.title + ','

    # 获取
    # s = mysite.objects.get(num=3)
    # str = s.title

    # 更新
    # s.title = 'python'
    # s.save()

    # 删除
    # s = mysite.objects.get(num=1)
    # s.delete()

    # return HttpResponse('Hello World<br>' + str)

    # 返回 json
    response_data = {'hello': 'django'}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


# 获取推荐币种
def get_recommend_currency(request):

    response_data = _get_recommend_currency()
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def _get_recommend_currency():

    db = mysqlutil.init()
    cursor = db.cursor()

    currencies = []

    try:

        sql = '''
        SELECT * FROM `xcm_vxn_currency_info`
        WHERE currency in ('btc','eth','xrp','bch','ltc','xlm')
        '''
        cursor.execute(sql, ())
        rows = cursor.fetchall()

        for r in rows:
            currencies.append(_convert_currency(r))

    except:
        util.printExcept()
    finally:
        db.close()
        cursor.close()

    return currencies


def _convert_currency(tupleObj):
    currency = {}
    currency['currency'] = tupleObj[1]
    currency['fullname'] = tupleObj[2]
    currency['cnname'] = tupleObj[3]
    currency['description'] = tupleObj[4]
    currency['price_cny'] = tupleObj[5]
    currency['price_scope'] = tupleObj[6]
    currency['high'] = tupleObj[7]
    currency['low'] = tupleObj[8]
    currency['circulating_cny_value'] = tupleObj[9]
    currency['ranking'] = tupleObj[10]
    currency['circulating_usd_value'] = tupleObj[11]
    currency['circulating_btc_value'] = tupleObj[12]
    currency['circulating_value_percent'] = tupleObj[13]
    currency['circulating_volume'] = tupleObj[14]
    currency['total_volume'] = tupleObj[15]
    currency['circulating_rate'] = tupleObj[16]
    currency['turn_volume'] = tupleObj[17]
    currency['turn_volume_ranking'] = tupleObj[18]
    currency['turnover_rate'] = tupleObj[19]
    return currency


# 获取风向标
# 统计每个涨跌幅度的百分比
def get_scope_percent(request):
    
    def get_scope_percent():

        db = mysqlutil.init()
        cursor = db.cursor()

        currencies = []

        try:

            sql = '''
            SELECT scope, count(scope) FROM
            (SELECT ROUND(price_scope, 0) scope FROM `xcm_vxn_currency_info`) AS t
            GROUP BY scope
            '''
            print(sql)
            cursor.execute(sql, ())
            rows = cursor.fetchall()

            for r in rows:
                currencies.append({'scope': r[0], 'count': r[1]})

        except:
            util.printExcept()
        finally:
            db.close()
            cursor.close()

        return currencies

    response_data = get_scope_percent()
    return HttpResponse(json.dumps(response_data), content_type="application/json")


# 获取币种列表
# orderField 排序字段
# orderBy    排序类型 desc|asc
def get_currency_list(request, orderField, orderBy, pageIndex=1, pageSize=10):

    response_data = _get_currency_list(orderField, orderBy, '', pageIndex, pageSize)
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def _get_currency_list(orderField, orderBy='DESC', searchKey='', pageIndex=1, pageSize=10):

    db = mysqlutil.init()
    cursor = db.cursor()

    currencies = []

    # 将页码转换为查询范围
    pageIndex = int(pageIndex)
    pageSize = int(pageSize)
    pageStart = (pageIndex - 1) * pageSize

    try:

        sql = 'SELECT * FROM `xcm_vxn_currency_info`'
        if searchKey != '':
            searchKey = "'%"+searchKey+"%'"
            sql += 'WHERE currency LIKE %s OR fullname LIKE %s OR cnname LIKE %s'%(searchKey, searchKey, searchKey)
        sql += 'ORDER BY %s %s LIMIT %s,%s'%(orderField, orderBy, pageStart, pageSize)
        print(sql)
        cursor.execute(sql)
        rows = cursor.fetchall()

        for r in rows:
            currencies.append(_convert_currency(r))

    except:
        util.printExcept()
    finally:
        db.close()
        cursor.close()

    return currencies


# 获取热门币种
def get_hot_currency(request):
    
    response_data = _get_hot_currency()
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def _get_hot_currency():

    db = mysqlutil.init()
    cursor = db.cursor()

    currencies = []

    try:

        sql = '''
        SELECT * FROM `xcm_vxn_currency_info`
        WHERE currency in ('btc','eos','eth','pai','rct','ada', 'doge', 'bch', 'ht')
        '''
        cursor.execute(sql, ())
        rows = cursor.fetchall()

        for r in rows:
            currencies.append(_convert_currency(r))

    except:
        util.printExcept()
    finally:
        db.close()
        cursor.close()

    return currencies


# 搜索币种
def search_currency(request, searchKey, pageIndex=1, pageSize=10):

    response_data = _get_currency_list('currency', 'asc', searchKey, pageIndex, pageSize)
    return HttpResponse(json.dumps(response_data), content_type="application/json")
