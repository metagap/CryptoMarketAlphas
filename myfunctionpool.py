from numpy.lib.arraysetops import isin
from numpy.lib.function_base import corrcoef
from pandas.io.parsers import read_csv
import talib as ta
from talib import MA_Type
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

global init_cash_balance, init_eth_balance, tx_fee, init_position

init_cash_balance =  10000
init_eth_balance = 0
tx_fee = 0
init_position = False

def rsi(data_arrlike, Period):
    data = data_arrlike.to_numpy()
    rsi_result = ta.RSI(data,Period)
    return rsi_result

def bollingerBand(data_arrlike):
    data = data_arrlike.to_numpy()
    upper, middle, lower = ta.BBANDS(data, matype=MA_Type.T3)
    return upper, middle, lower

def init_condition():
    Checking = []
    cash_account = init_cash_balance
    eth_account = init_eth_balance
    position = init_position
    tx_time = 0
    return Checking, cash_account, eth_account, position,tx_time

def MA(data_arrlike, Period):
    if isinstance(data_arrlike,np.ndarray):
        result = ta.SMA(data_arrlike,Period)
    else:
        data = data_arrlike.to_numpy()
        result = ta.SMA(data,Period)
    return result

def MACD(data_arrlike):
    data = data_arrlike.to_numpy()
    macd, macdsignal, macdhist = ta.MACD(data, fastperiod = 12, slowperiod = 26, signalperiod = 9)
    return macd, macdsignal,macdhist 

def ADX(high,low,close,timeperiod = 14):
    if isinstance(high,np.ndarray) and isinstance(low,np.ndarray) and isinstance(close,np.ndarray):
        result = ta.ADX(high, low, close, timeperiod)
    else:
        data_high = high.to_numpy()
        data_low = low.to_numpy()
        data_close = close.to_numpy()
        result = ta.ADX(data_high, data_low, data_close, timeperiod)
    return result

def supertrend(close,high,low,period=7,atr_multiplier=3):
    tr = [math.nan]
    upperband = [math.nan]
    lowerband = [math.nan]
    trend = [False]
    tr_ad = [math.nan]

    for i in range(1,len(close)):
        tr_add = max((high[i]-low[i]),abs(high[i]-close[i-1]),abs(low[i]-close[i-1]))
        tr_ad.append(tr_add)
        if i<period+1:
            tr.append(math.nan)
            upperband.append(math.nan)
            lowerband.append(math.nan)
            trend.append(False)
            # print(close[i],tr_ad[i],upperband[i],lowerband[i],trend[i])
        else:
            atr = np.mean(tr_ad[-period:])
            upperband.append(low[i]/2+high[i]/2 + (atr_multiplier * atr))
            lowerband.append(low[i]/2+high[i]/2 - (atr_multiplier * atr))
            tr.append(atr)
            
            if close[i] > upperband[i-1]:
                trend.append(True)
            elif close[i] < lowerband[i-1]:
                trend.append(False)
            else:
                trend.append(trend[i-1])
                if trend[i] and lowerband[i]<lowerband[i-1]:
                    lowerband[i] = lowerband[i-1]
                if not trend[i] and upperband[i] > upperband[i-1]:
                    upperband[i] = upperband[i-1]
            # print(close[i],tr_ad[i],upperband[i],lowerband[i],trend[i])
    return trend

def BarUpDn(closes,opens):
    Flag = ['hold']
    for i in range(1,len(closes)):
        if opens[i] > closes[i-1] and closes[i-1] > opens[i-1]:
            Flag.append('buy')
        elif opens[i] < closes[i-1] and closes[i-1] < opens[i-1]:
            Flag.append('sell')
        else:
            Flag.append('hold')
    
    return Flag

def ts_rank(x,d):
    rollrank = lambda data: data.size - data.argsort().argsort().iloc[-1] 
    result = x.rolling(d).apply(rollrank)
    return result

def OutsideBar(lows,highs,opens,closes):
    Flag = ['hold']
    for i in range(1,len(lows)):
        if (lows[i] < lows[i-1]) and (highs[i] > highs[i-1]):
            if opens[i] < closes[i]:
                Flag.append('buy')
            else:
                Flag.append('sell')
        else:
            Flag.append('hold')
    return Flag

def Trend_detector(closes,high,low,vol,window = 10):
    trend = ['NOTREND']
    max_high = high.rolling(window).max()
    min_low = low.rolling(window).min()
    vol_rank = ts_rank(vol,10)
    adx = ADX(high,low,closes,timeperiod = 10)

    for i in range(1,len(closes)):
        if trend[i-1] == 'NOTREND':
            if closes[i] > max_high[i-1] and vol_rank[i]<=4:
                trend.append('UPTREND')
            elif closes[i] < min_low[i-1] and vol_rank[i]<=4:
                trend.append('DOWNTREND')
            else:
                trend.append('NOTREND')
        elif trend[i-1] == 'UPTREND':
            if adx[i]>=adx[i-1]:
                trend.append('UPTREND')
            else:
                trend.append('NOTREND')
        elif trend[i-1] == 'DOWNTREND':
            if adx[i]>=adx[i-1]:
                trend.append('DOWNTREND')
            else:
                trend.append('NOTREND')
    return trend

class cryptoalphs(object):
    def __init__(self,df) -> None:
        self.open = df.open
        self.close = df.close
        self.high = df.high
        self.low = df.low
        self.vol = df.volume
        self.quote_asset_volume = df.quote_asset_volume
        self.numberoftrade = df.numberoftrade
        self.taker_buy_base_volume = df.taker_buy_base_volume
        self.maker_buy_base_volume = df.maker_buy_base_volume
        self.taker_buy_quote_volume = df.taker_buy_quote_volume
        self.maker_buy_quote_volume = df.maker_buy_quote_volume
    
    def Factor001(self):
        print("RSI Trading Strategy")
        #rsi strategies rsi > 30 sell, rsi < 70 buy.
        closes = self.close
        Checking = []
        account = init_cash_balance
        eth_account = init_eth_balance
        close_rsi = rsi(closes,14)
        position =  init_position
        for i in range(len(close_rsi)):
            if close_rsi[i] > 75:
                if position:
                    trade = eth_account*closes[i]
                    account = trade * (1 - tx_fee)
                    # print("You have sold {} eth at {}, the rsi is {}".format(eth_account,closes[i],close_rsi[i]))
                    eth_account = 0
                    position = False

                
            if close_rsi[i] < 25 :
                if not position:
                    trade = account/closes[i]
                    # print("You have bought {} eth at {}, the rsi is {}".format(trade,closes[i],close_rsi[i]))
                    eth_account = trade * (1 - tx_fee)
                    account = 0
                    position = True

            Checking.append(closes[i]*eth_account + account)      
        
        return Checking

    def Factor002(self):
        print("Bolling Bands Strategy")
        #Bollinger Band strategies: Buy @ price lower than 5% of lower band; Sell @ price higher than 5% of the upper band.
        closes = self.close
        Checking, cash_account, eth_account, position,tx_time = init_condition()
        Checking = [cash_account]
        upper, middle, lower = bollingerBand(closes)
        TH = 0
        tx_time = 0
        MA_close = MA(closes,6)

        for i in range(1,len(closes)):
            
            if (MA_close[i - 1] < upper[i - 1]) and (MA_close[i - 1] > middle[i - 1]):

                if closes[i] > upper[i]*(1 + TH) :
                    if position:
                        trade_cash = eth_account*closes[i]
                        cash_account = trade_cash * (1 - tx_fee)
                        # print("You have sold {} eth at {}, the upper band is {}".format(eth_account,closes[i],upper[i]))
                        eth_account = 0
                        position = False
                        tx_time += 1
                
                if closes[i] < middle[i] * (1 + TH):
                    if not position:
                        trade_vol = cash_account/closes[i]
                        # print("You have bought {} eth at {}, the middle band is {}".format(trade_vol,closes[i],middle[i]))
                        eth_account = trade_vol * (1 - tx_fee)
                        cash_account = 0
                        position = True
                        tx_time += 1

            if (MA_close[i - 1] > lower[i - 1]) and (MA_close[i - 1] < middle[i - 1]):

                if closes[i] < lower[i] * (1 - TH):
                    if not position:
                        trade_vol = cash_account/closes[i]
                        # print("You have bought {} eth at {}, the lower band is {}".format(trade_vol,closes[i],lower[i]))
                        eth_account = trade_vol * (1 - tx_fee)
                        cash_account = 0
                        position = True
                        tx_time += 1

                if closes[i] > middle[i] * (1 - TH):
                    if position:
                        trade_cash = eth_account*closes[i]
                        cash_account = trade_cash * (1 - tx_fee)
                        # print("You have sold {} eth at {}, the middle band is {}".format(eth_account,closes[i],middle[i]))
                        eth_account = 0
                        position = False
                        tx_time += 1

            Checking.append(closes[i]*eth_account + cash_account)
        # print(tx_time)
        return Checking

    def Factor003(self):
        print("MACD Trading Strategy")
        #macd factor timing.
        closes = self.close
        opens = self.open
        Checking, cash_account, eth_account, position,tx_time = init_condition()
        Checking = [cash_account]
        macd,macdsignal,macdhist = MACD(closes)
        MA_macdhist = MA(macdhist,2)
        for i in range(1,len(macd)-1):
            if macdhist[i-1] * macdhist[i] < 0:
                iscross = True
                if macd[i-1] < macdsignal[i-1]:
                    if not position:
                        trade_vol = cash_account/opens[i+1]
                        # print("You have bought {} eth at {}".format(trade_vol,closes[i]))
                        eth_account = trade_vol * (1 - tx_fee)
                        cash_account = 0
                        position = True
                        tx_time += 1

                
                if macd[i-1] > macdsignal[i-1]:
                    if position:
                        trade_cash = eth_account*opens[i+1]
                        cash_account = trade_cash * (1 - tx_fee)
                        # print("You have sold {} eth at {}".format(eth_account,closes[i]))
                        eth_account = 0
                        position = False
                        tx_time += 1
            
            else:
                iscross = False

                if macdhist[i] > MA_macdhist[i-1] and MA_macdhist[i-1] != math.nan:
                    if not position:
                        trade_vol = cash_account/opens[i+1]
                        # print("You have bought {} eth at {}".format(trade_vol,closes[i]))
                        eth_account = trade_vol * (1 - tx_fee)
                        cash_account = 0
                        position = True
                        tx_time += 1

                if macdhist[i] < MA_macdhist[i-1] and MA_macdhist[i-1] != math.nan:
                    if position:
                        trade_cash = eth_account*opens[i+1]
                        cash_account = trade_cash * (1 - tx_fee)
                        # print("You have sold {} eth at {}".format(eth_account,closes[i]))
                        eth_account = 0
                        position = False
                        tx_time += 1
        
            Checking.append(closes[i]*eth_account + cash_account)
        # print(tx_time)
        Checking.append(closes[len(closes)-1]*eth_account + cash_account)
        return Checking

    def Factor004(self,box_window = 10):
        print("Grid Trading Strategy")
        highs = self.high
        closes = self.close
        opens = self.open
        low = self.low
        vol = self.vol
        vol_rank = ts_rank(vol,d=box_window)
        cash_account = 10000
        eth_account = 0
        tx_time = 0
        Checking = [cash_account]
        trend = Trend_detector(closes,highs,low,vol,window = 10)
        for i in range(1,len(trend)):
            if trend[i-1] == "NOTREND" and trend[i] == 'UPTREND':
                trade_vol = cash_account/opens[i+1]
                # print("You have bought {} eth at {}".format(trade_vol,closes[i]))
                eth_account += trade_vol * (1 - tx_fee)
                cash_account = 0
                tx_time += 1
            elif trend[i-1] == "NOTREND" and trend[i] == 'DOWNTREND':
                trade_eth = -cash_account/opens[i+1]
                cash_account += cash_account * (1 - tx_fee)
                # print("You have sold {} eth at {}".format(eth_account,closes[i]))
                eth_account += trade_eth
                tx_time += 1

            elif trend[i-1] == "UPTREND" and trend[i] == 'UPTREND':
                pass
            elif trend[i-1] == "UPTREND" and trend[i] == 'NOTREND':
                trade_cash = eth_account*opens[i+1]
                cash_account += trade_cash * (1 - tx_fee)
                # print("You have sold {} eth at {}".format(eth_account,closes[i]))
                eth_account = 0
                tx_time += 1
            elif trend[i-1] == "DOWNTREND" and trend[i] == 'NOTREND':
                trade_vol = eth_account*opens[i+1]
                # print("You have bought {} eth at {}".format(trade_vol,closes[i]))
                eth_account = 0
                cash_account += trade_vol
                tx_time += 1
            elif trend[i-1] == "DOWNTREND" and trend[i] == 'DOWNTREND':
                pass

            Checking.append(closes[i]*eth_account + cash_account)
        return Checking
        
        

    def Factor005(self):
        #Follow the suppertrend
        print("Suppertrend Strategy")
        closes = self.close
        highs = self.high
        lows = self.low
        opens = self.open
        Checking, cash_account, eth_account, position,tx_time = init_condition()
        Checking = [10000]
        trend = supertrend(closes,highs,lows,period=7,atr_multiplier=3)
        for i in range(1,len(trend)):
            if trend[i] and not trend[i-1]:
                if not position:
                    trade_vol = cash_account/opens[i+1]
                    # print("You have bought {} eth at {}".format(trade_vol,closes[i]))
                    eth_account = trade_vol * (1 - tx_fee)
                    cash_account = 0
                    position = True
                    tx_time += 1
            elif not trend[i] and trend[i-1]:
                if position:
                    trade_cash = eth_account*opens[i+1]
                    cash_account = trade_cash * (1 - tx_fee)
                    # print("You have sold {} eth at {}, the middle band is {}".format(eth_account,closes[i],middle[i]))
                    eth_account = 0
                    position = False
                    tx_time += 1
            
            Checking.append(closes[i]*eth_account + cash_account)
        # print(tx_time)

        return Checking

    def Factor006(self):
        # If not in position and FastSMA > SLOWSMA ->BUY
        # If in position and SlowSMA > FastSMA -> Sell
        print("Slow&Fast SMA Strategy")
        closes = self.close
        opens = self.open
        Checking, cash_account, eth_account, position,tx_time = init_condition()
        sma_slow = MA(closes,14)
        sma_fast = MA(closes,7)
        for i in range(len(closes)):
            if not position:
                if sma_fast[i] > sma_slow[i]:
                    trade_vol = cash_account/opens[i+1]
                    # print("You have bought {} eth at {}".format(trade_vol,closes[i]))
                    eth_account = trade_vol * (1 - tx_fee)
                    cash_account = 0
                    position = True
                    tx_time += 1
            
            if position:
                if sma_fast[i] < sma_slow[i]:
                    trade_cash = eth_account*opens[i+1]
                    cash_account = trade_cash * (1 - tx_fee)
                    # print("You have sold {} eth at {}, the middle band is {}".format(eth_account,closes[i],middle[i]))
                    eth_account = 0
                    position = False
                    tx_time += 1

            Checking.append(closes[i]*eth_account + cash_account)

        return Checking
        
    def Factor007(self):
        # if open[i] > close[i-1], close[i-1] > open[i-1] enter long
        # if open[i] < close[i-1], close[i-1] < open[i-1] enter short
        print("BarUpDn Strategy")
        closes = self.close
        opens = self.open
        Checking, cash_account, eth_account, position, tx_time = init_condition()
        Flag = BarUpDn(closes,opens)
        Checking = [10000]
        for i in range(1,len(closes)):
            if Flag[i] == 'buy':
                if not position:
                    trade_vol = cash_account/opens[i]
                    # print("You have bought {} eth at {}".format(trade_vol,closes[i]))
                    eth_account = trade_vol * (1 - tx_fee)
                    cash_account = 0
                    position = True
                    tx_time += 1

            if Flag[i] == 'sell':
                if position:
                    trade_cash = eth_account*opens[i]
                    cash_account = trade_cash * (1 - tx_fee)
                    # print("You have sold {} eth at {}, the middle band is {}".format(eth_account,closes[i],middle[i]))
                    eth_account = 0
                    position = False
                    tx_time += 1
            
            Checking.append(closes[i]*eth_account + cash_account)
        print(tx_time)
        return Checking

    def Factor008(self):
        #if low[i] < low[i-1], high[i] > high[i-1] : outside bar strategy
        # red bar sell, green bar buy
        print("OutSide Bar Strategy")
        closes = self.close
        lows = self.low
        highs = self.high
        opens = self.open
        Checking, cash_account, eth_account, position, tx_time = init_condition()
        Checking = [10000]
        Flag = OutsideBar(lows,highs,opens,closes)
        for i in range(len(opens)-1):
            if Flag[i] == 'buy':
                if not position:
                    trade_vol = cash_account/opens[i+1]
                    # print("You have bought {} eth at {}".format(trade_vol,closes[i]))
                    eth_account = trade_vol * (1 - tx_fee)
                    cash_account = 0
                    position = True
                    tx_time += 1

            if Flag[i] == 'sell':
                if position:
                    trade_cash = eth_account*opens[i+1]
                    cash_account = trade_cash * (1 - tx_fee)
                    # print("You have sold {} eth at {}, the middle band is {}".format(eth_account,closes[i],middle[i]))
                    eth_account = 0
                    position = False
                    tx_time += 1
            
            Checking.append(closes[i]*eth_account + cash_account)
        print(tx_time)
        return Checking
