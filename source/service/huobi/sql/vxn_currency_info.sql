SELECT *, FROM_UNIXTIME(update_time, '%Y-%m-%d %H:%i:%S') as locale_date FROM xcmarket.xcm_vxn_currency_info;

SELECT * FROM xcmarket.xcm_vxn_currency_info order by update_time desc;

SELECT * FROM xcmarket.xcm_vxn_currency_info where fullname='g';

SELECT count(_id) FROM xcmarket.xcm_vxn_currency_info;

SELECT currency, count(_id) FROM xcmarket.xcm_vxn_currency_info group by currency having count(_id) > 1;

insert into xcm_temp select _id FROM xcmarket.xcm_vxn_currency_info group by currency having count(_id) > 1;
delete from xcm_vxn_currency_info where _id in (select _id from xcm_temp);
delete from xcm_temp;

update xcm_vxn_currency_info set create_time = 1531152000;

SELECT * FROM xcmarket.xcm_vxn_currency_info where currency='btc';