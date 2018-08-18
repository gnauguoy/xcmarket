SELECT currency, count(_id) FROM xcmarket.xcm_vxn_currency group by currency having count(currency) > 1;

select * from xcm_vxn_currency;
-- where currency = 'bt2';

select count(_id) from xcm_vxn_currency;

select x.currency, h.currency 
-- select count(x._id)
from xcm_vxn_currency x left join xcm_huobi_currency h on x.currency = h.currency;

select * from xcm_vxn_currency where fullname = 'komodo';