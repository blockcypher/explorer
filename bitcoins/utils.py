SATOSHIS_PER_BTC = 10**8
SATOSHIS_PER_MILLIBITCOIN = 10**5


def satoshis_to_btc(satoshis, decimals=4):

    btc = float(satoshis) / float(SATOSHIS_PER_BTC)

    if decimals:
        return round(btc, decimals)
    else:
        return btc
