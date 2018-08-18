from history.OkcoinSpotAPI import OKCoinSpot

rest = OKCoinSpot('www.okex.com', 'dc89d175-45a1-41e0-b389-8317a8316fed', 'F400ED032C507D0E53F5AA836A12DCCC')
print(rest.ticker('ltc_btc'))

