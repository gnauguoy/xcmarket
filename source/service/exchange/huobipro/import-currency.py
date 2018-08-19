import pymysql, json, sys
import mysqlutil
 
# 打开数据库连接
db = mysql.init()
 
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

# 使用 execute()  方法执行 SQL 查询 
cursor.execute("SELECT VERSION()")
 
# 使用 fetchone() 方法获取单条数据.
data = cursor.fetchone()
 
print ("Database version : %s " % data)

# f = open('huobi_currency.json')
# content = f.read()
# print(content)
# f.close()

# currency = json.loads(content)
# currency = currency['data']
# print(len(currency))

# try:
#     for c in currency:
#         sql = 'INSERT INTO `xcm_huobi_currency` (currency) VALUES (%s)'
#         cursor.execute(sql, (c))

#     db.commit()
# except:
#     print(sys.exc_info()[0])

db.close()
