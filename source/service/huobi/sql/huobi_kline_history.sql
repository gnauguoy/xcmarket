SELECT FROM_UNIXTIME(id, '%Y-%m-%d %H:%i:%S') FROM xcmarket.xcm_huobi_kline_history where symbol='appceth' order by _id desc limit 1;

-- 获取第一条数据
SELECT * FROM xcmarket.xcm_huobi_kline_history order by _id asc limit 1;

-- 数据总量
SELECT COUNT(_id) FROM xcmarket.xcm_huobi_kline_history;

-- 检查是否重复
SELECT _id, id, period, symbol, vol, count(id) FROM xcmarket.xcm_huobi_kline_history group by id, symbol, period having count(*) > 1;

-- 获取重复数据的总数
select count(_id) from
(SELECT _id, id, period, symbol, vol, count(id) FROM xcmarket.xcm_huobi_kline_history group by id, symbol, period having count(*) > 1) as t;

-- 查看重复的数据
select *, FROM_UNIXTIME(id, '%Y-%m-%d %H:%i:%S') as locale_date 
from xcmarket.xcm_huobi_kline_history where id=1531596660 and period='1min' and symbol='bchusdt';


-- 将重复 _id 存入临时表
insert into xcm_temp SELECT min(_id) as _id FROM xcmarket.xcm_huobi_kline_history group by id, symbol, period having count(*) > 1;

-- 删除重复数据
delete from xcmarket.xcm_huobi_kline_history where _id in (select * from xcm_temp);

-- 删除临时表数据
delete from xcm_temp;


SELECT min(_id) FROM xcmarket.xcm_huobi_kline_history group by id, symbol, period having count(*) > 1;

SELECT id, symbol, period, count(id) FROM xcmarket.xcm_huobi_kline_history group by id, symbol, period having count(*) > 1;

SELECT symbol, count(id) FROM xcmarket.xcm_huobi_kline_history group by symbol having count(*) > 1;

SELECT * FROM xcmarket.xcm_huobi_kline_history where period='5min' order by id desc limit 1;


-- 删除数据库
insert into xcm_huobi_kline_history1 select * FROM xcmarket.xcm_huobi_kline_history;

delete from xcm_huobi_kline_history;

rename table xcm_huobi_kline_history1 to xcm_huobi_kline_history;