from binance.client import Client
import config, pprint
import pandas as pd
import numpy as np
from datetime import datetime
from myfunctionpool import *

client = Client(config.API_KEY, config.API_SECRET_KEY)


def acquire_data(date_start,date_end,symbol):
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, date_start, date_end)

    open_times = []
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    quote_asset_volumes = []
    numberoftrades = []
    taker_buy_base_volumes =[]
    maker_buy_base_volumes = []
    taker_buy_quote_volumes = []
    maker_buy_quote_volumes = []

    for kline in klines:
        open_time, open, high, low, close, volume, quote_volume, numberoftrade= int(kline[0]),float(kline[1]),float(kline[2]),float(kline[3]),float(kline[4]),float(kline[5]),float(kline[7]),float(kline[8])
        taker_buy_base, taker_buy_quote = float(kline[9]),float(kline[10])
        maker_buy_base, maker_buy_quote = float(volume - taker_buy_base),float(quote_volume - taker_buy_quote)
        open_time = datetime.fromtimestamp(open_time/1000)
        open_times.append(open_time)
        opens.append(open)
        highs.append(high)
        lows.append(low)
        closes.append(close)
        volumes.append(volume)
        quote_asset_volumes.append(quote_volume)
        numberoftrades.append(numberoftrade)
        taker_buy_base_volumes.append(taker_buy_base)
        maker_buy_base_volumes.append(maker_buy_base)
        taker_buy_quote_volumes.append(taker_buy_quote)
        maker_buy_quote_volumes.append(maker_buy_quote)

    df = pd.DataFrame(np.column_stack([open_times,opens,highs,lows,closes,volumes,quote_asset_volumes,\
                numberoftrades,taker_buy_base_volumes,maker_buy_base_volumes,taker_buy_quote_volumes,\
                maker_buy_quote_volumes]),\
                columns=['open_time','open','high','low','close','volume','quote_asset_volume',\
                'numberoftrade','taker_buy_base_volume','maker_buy_base_volume','taker_buy_quote_volume',\
                'maker_buy_quote_volume'])

    df.set_index('open_time')
    df.to_csv('data_{} to {}.csv'.format(date_start,date_end),index =True)

    return True

def acquire_datah(date_start,date_end,symbol):
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_8HOUR, date_start, date_end)

    open_times = []
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    quote_asset_volumes = []
    numberoftrades = []
    taker_buy_base_volumes =[]
    maker_buy_base_volumes = []
    taker_buy_quote_volumes = []
    maker_buy_quote_volumes = []

    for kline in klines:
        open_time, open, high, low, close, volume, quote_volume, numberoftrade= int(kline[0]),float(kline[1]),float(kline[2]),float(kline[3]),float(kline[4]),float(kline[5]),float(kline[7]),float(kline[8])
        taker_buy_base, taker_buy_quote = float(kline[9]),float(kline[10])
        maker_buy_base, maker_buy_quote = float(volume - taker_buy_base),float(quote_volume - taker_buy_quote)
        open_time = datetime.fromtimestamp(open_time/1000)
        open_times.append(open_time)
        opens.append(open)
        highs.append(high)
        lows.append(low)
        closes.append(close)
        volumes.append(volume)
        quote_asset_volumes.append(quote_volume)
        numberoftrades.append(numberoftrade)
        taker_buy_base_volumes.append(taker_buy_base)
        maker_buy_base_volumes.append(maker_buy_base)
        taker_buy_quote_volumes.append(taker_buy_quote)
        maker_buy_quote_volumes.append(maker_buy_quote)

    df = pd.DataFrame(np.column_stack([open_times,opens,highs,lows,closes,volumes,quote_asset_volumes,\
                numberoftrades,taker_buy_base_volumes,maker_buy_base_volumes,taker_buy_quote_volumes,\
                maker_buy_quote_volumes]),\
                columns=['open_time','open','high','low','close','volume','quote_asset_volume',\
                'numberoftrade','taker_buy_base_volume','maker_buy_base_volume','taker_buy_quote_volume',\
                'maker_buy_quote_volume'])

    df.set_index('open_time')
    df.to_csv('data_{} to {}.csv'.format(date_start,date_end),index =True)

    return True

