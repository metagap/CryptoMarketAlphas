import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import pandas as pd

def plot_the_result(closes,Checking,Date,FactorName):
    APY_coin = closes[-1]/closes[0]
    APY_strategeis = Checking[-1]/10000
    print('The Strategy alpha is {:.4f}'.format(APY_strategeis-APY_coin))

    if APY_coin <= APY_strategeis:
        print('The chosen period of holding coins yield is {:.4f}'.format(APY_coin))
        print('The chosen period of strategies yield is {:.4f}'.format(APY_strategeis))
        print('The strategy is great.')
    else:
        print('The chosen period of holding coins yield is {:.4f}'.format(APY_coin))
        print('The chosen period of strategies yield is {:.4f}'.format(APY_strategeis))
        print('The strategy is not good enough.')

    new_closes = np.array(closes)/closes[0]
    new_checking = np.array(Checking)/Checking[0]
    plt.figure()
    plt.plot(Date,new_closes,'b-',label = 'eth.yield')
    plt.plot(Date,new_checking,'r-',label = 'strategy.yield')
    plt.legend()
    plt.title('Metalpha Strategies')
    plt.xlabel('Time')
    plt.ylabel('Weekly APY')
    new_date = [Date[0],Date[math.floor(len(Date)/3)],Date[math.floor(len(Date)/3*2)],Date[len(Date)-1]]
    plt.xticks(new_date,rotation = 10)
    plt.savefig(FactorName)


def cal_alpha(closes, Checking):
    alpha = Checking[-1]/Checking[0] - closes[-1]/closes[0]
    return alpha

def arr_pct(arr, time_gap=1440):
    #timegap = 720 for 12hrs window 1440 for 1 day time window.
    new_len = int((len(arr)-1)/time_gap)
    new_arr = []
    for i in range(new_len):
        new_arr_ele = (arr[(i+1)*time_gap-1] - arr[i*time_gap])/arr[i*time_gap]
        new_arr.append(new_arr_ele)
    return new_arr

def cal_sharpe_ratio(closes, Checking):
    df_closes_pct = arr_pct(closes)
    df_Checking_pct = arr_pct(Checking)
    df_closes_pct_mean = np.mean(df_closes_pct)
    df_Checking_pct_mean = np.mean(df_Checking_pct)
    df_Checking_pct_std = np.std(df_Checking_pct)
    sharpe_ratio = (df_Checking_pct_mean - df_closes_pct_mean)/df_Checking_pct_std
    return sharpe_ratio

def cal_max_drawdown(Checking):
    mdd = 0
    peak = Checking[0]
    for x in Checking:
        if x > peak: 
            peak = x
        dd = (peak - x) / peak
        if dd > mdd:
            mdd = dd
    return mdd

def cal_win_rate(closes,Checking,time_window = 100):
    df_closes_pct = arr_pct(closes,time_window)
    df_Checking_pct = arr_pct(Checking,time_window)

    win,lose = 0,0
    for i in range(len(df_closes_pct)):
        dif = df_Checking_pct[i] - df_closes_pct[i]
        if dif > 0.0001 :
            win += 1
        elif dif < -0.0001 :
            lose += 1
    win_rate = win/(win + lose)
    return win_rate

