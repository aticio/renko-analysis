import json
from datetime import datetime
import requests
import time
from multiprocessing import Process
from datetime import datetime
from dateutil.relativedelta import relativedelta
from legitindicators import atr
from renko import Renko

EXCHANGE_INFO = "https://api.binance.com/api/v3/exchangeInfo"
KLINE_URL = "https://api.binance.com/api/v3/klines"

KLINE_INTERVAL = "1m"
KLINE_LIMIT = 1000


def main():
    kline_data = []
    startDate = datetime.now() - relativedelta(years=1)
    startTime = datetime.timestamp(startDate) * 1000
    startTimeString = str(startTime)
    startTimeString = startTimeString.split(".")[0]

    klines = []
    kline_count = 1000

    while kline_count == 1000: 
        klines = get_kline("BTCUSDT", KLINE_INTERVAL, KLINE_LIMIT, startTimeString)
        print(len(klines))
        kline_count = len(klines)
        startTimeString = klines[-1][0]
        if len(kline_data) != 0:
            klines.pop()
        kline_data.extend(klines)

    timestamp, opn, high, low, close = get_ohlc(kline_data)
    atr_data = []
    for i in range(0, len(kline_data)):
        ohlc = [opn[i], high[i], low[i], close[i]]
        atr_data.append(ohlc)
    atrng = atr(atr_data, 14)

    atrng = list(filter(lambda x: x != 0, atrng))
    atrng = [round(x,2) for x in atrng]

    atr_max = max(atrng)
    atr_min = min(atrng)

    # with open(r'atrng.txt', 'w') as fp:
    #     for a in atrng:
    #         # write each item on a new line
    #         fp.write("%s\n" % a)
    #     print('Done')

    print(atr_min, atr_max)

    start = int(atr_min * 100)
    end = int(atr_max * 100)

    for i in range(start, end):
        print(i)

    # exchange_info = get_exchange_info()
    # pairs = get_pairs(exchange_info)
    # busd_pairs = filter_busd_pairs(pairs)
    # for bp in busd_pairs:
    #     p = Process(target=init_ops, args=(bp,))
    #     p.start() 


def init_ops(pair):
    klines = get_kline(pair, KLINE_INTERVAL, KLINE_LIMIT)
    timestamp, open, high, low, close = get_ohlc(klines)


def get_ohlc(klines):
    timestamp = [float(t[0]) for t in klines]
    open = [float(o[1]) for o in klines]
    high = [float(h[2]) for h in klines]
    low = [float(l[3]) for l in klines]
    close = [float(c[4]) for c in klines]
    return timestamp, open, high, low, close


def get_kline(kline_symbol, kline_interval, kline_limit, startTime):
    try:
        params = {"symbol": kline_symbol, "interval": kline_interval, "limit": kline_limit, "startTime": startTime}
        response = requests.get(
            url=f"{KLINE_URL}", params=params)
        response.raise_for_status()
        kline = response.json()
        # kline = kline[:-1]
        return kline
    except requests.exceptions.RequestException as err:
        print(err)
        return None


def filter_busd_pairs(pairs):
    busd_paris = []
    for pair in pairs:
        if "BUSD" in pair and "USDT" not in pair and "USDC" not in pair and "USDC" not in pair:
            busd_paris.append(pair)
    return busd_paris


def get_pairs(exchange_info):
    pairs = []
    for symbol in exchange_info["symbols"]:
        pairs.append(symbol["symbol"])
    return pairs


def get_exchange_info():
    response = requests.get(EXCHANGE_INFO)
    exchange_info = response.json()
    return exchange_info


if __name__ == "__main__":
    main()