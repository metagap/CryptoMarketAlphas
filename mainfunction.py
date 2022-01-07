import sys
import os
import pandas as pd
import numpy as np
import datetime as dt
from myfunctionpool import *
from strategies_tester import *
from data_require import acquire_data
 
print(os.getcwd())
path_cur = os.getcwd() 
os.chdir(path_cur)

symbol = 'ETHUSDT'
date_start = "27 Dec, 2021"
date_end = "2 Jan, 2022"

acquire_data(date_start,date_end,symbol)

factor_name_list =['Factor001','Factor002','Factor003','Factor004','Factor005','Factor006'] 
# factor_name_list =['Factor006']

str_inputDir = '/Users/yueliang/FIND CRYPTO ALPHAS/'
str_outputDir = '/Users/yueliang/FIND CRYPTO ALPHAS/output/'
filename = 'data_{} to {}.csv'.format(date_start,date_end)

df = pd.read_csv(str_inputDir + filename)
closes = df['close'].to_numpy()
Date = df['open_time'].to_numpy()
gen = cryptoalphs(df)


sharpe_ratio =[]
mdd = []
win_rate = []
t = 0

print('The starting price is {:.2f}'.format(closes[0]))
print('The ending price is {:.2f}'.format(closes[-1]))

for tFactorName in factor_name_list:
    print("-------------------------------------------------------------------")
    print("we are testing the factor {}".format(tFactorName))
    tFactor = eval('gen.'+tFactorName +'()')
    plot_the_result(closes,tFactor,Date,tFactorName)
    sharpe_ratio.append(cal_sharpe_ratio(closes, tFactor))
    mdd.append(cal_max_drawdown(tFactor))
    win_rate.append(cal_win_rate(closes,tFactor))
    print('The strategy sharpe ratio: {:.3f}, max drawdown: {:.2f}%, win_rate: {:.3f}'.format(sharpe_ratio[t],-mdd[t]*100,win_rate[t]))
    t += 1
    print("-------------------------------------------------------------------")

