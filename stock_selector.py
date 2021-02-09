#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import os
import datetime as dt
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas_datareader.data as web

# from ta import add_all_ta_features
# from ta.utils import dropna
# from ta.volatility import BollingerBands

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# In[2]:


fn = 'stock.txt'

df_stock = pd.read_csv(fn,names = ['sym']).drop_duplicates()

ls_stock = df_stock['sym'].to_list()

df_stock = df_stock.reset_index()

df_stock.columns = ['sort','sym']

df_stock.head()


# In[3]:


start = dt.date.today() + relativedelta(days=-150)
end = dt.date.today() + relativedelta(days=-0)

ls_tickers = ls_stock

ls_df = []
for ticker in ls_tickers:
    try:
        df = web.DataReader(ticker, 'yahoo', start, end)
    except Exception as e:
        print(f'{str(e)}')
        continue
    df['sym'] = ticker
    ls_df.append(df.copy())


df_price = pd.concat(ls_df).reset_index()
df_price.columns = ['dte','hgh','low','opn','cls','vol','cls_adj','sym']
df_price.sort_values(['sym','dte'], inplace=True)

df_price = df_price[['dte','sym','hgh','low','cls','vol']].copy()

df_price['curr'] = end

df_price['curr'] = pd.to_datetime(df_price['curr'])
df_price['dte'] = pd.to_datetime(df_price['dte'])

df_price['ndays'] = (df_price['curr'] - df_price['dte']).dt.days

df_price['ndays'] = df_price.groupby(['sym'])['ndays'].rank()

df_price[df_price['sym']=='SPY'].head()


# In[4]:



from ta.volatility import BollingerBands
from ta.trend import MACD
from ta.momentum import RSIIndicator
# from ta.volume import put_call_ratio
from ta.trend import EMAIndicator
from ta.trend import SMAIndicator
from ta.trend import cci
from ta.volume import OnBalanceVolumeIndicator

ls_df = []
ls_tickers = ls_stock

for ticker in ls_tickers:

    #df = dropna(df_price[df_price['sym']==ticker])
    df = df_price[df_price['sym']==ticker].copy()
    
    indicator_bb = BollingerBands(close=df['cls'], window=20, window_dev=2)
    indicator_macd = MACD(close=df['cls'],window_fast=12,window_slow=26,window_sign=9)
    indicator_rsi14 = RSIIndicator(close=df['cls'],window=14)
    indicator_cci20 = cci(high=df['hgh'],low=df['low'],close=df['cls'],window=20,constant=0.015)
    indicator_obv = OnBalanceVolumeIndicator(close=df['cls'], volume=df['vol'],fillna=True)
    
    indicator_vol_sma20 = SMAIndicator(close=df['vol'],window=20)
    
    indicator_ema03 = EMAIndicator(close=df['cls'],window=3)
    indicator_ema05 = EMAIndicator(close=df['cls'],window=5)
    indicator_ema08 = EMAIndicator(close=df['cls'],window=8)
    indicator_ema10 = EMAIndicator(close=df['cls'],window=10)
    indicator_ema12 = EMAIndicator(close=df['cls'],window=12)
    indicator_ema15 = EMAIndicator(close=df['cls'],window=15)
    indicator_ema30 = EMAIndicator(close=df['cls'],window=30)
    indicator_ema35 = EMAIndicator(close=df['cls'],window=35)
    indicator_ema40 = EMAIndicator(close=df['cls'],window=40)
    indicator_ema45 = EMAIndicator(close=df['cls'],window=45)
    indicator_ema50 = EMAIndicator(close=df['cls'],window=50)
    indicator_ema60 = EMAIndicator(close=df['cls'],window=60)
    
    
    # Add Bollinger Bands features
    #df['bb_bbm'] = indicator_bb.bollinger_mavg()
    #df['bb_bbh'] = indicator_bb.bollinger_hband()
    #df['bb_bbl'] = indicator_bb.bollinger_lband()

    # Add Bollinger Band high indicator
    df['bb_bbhi'] = indicator_bb.bollinger_hband_indicator()

    # Add Bollinger Band low indicator
    df['bb_bbli'] = indicator_bb.bollinger_lband_indicator()
    
    #df['macd'] = indicator_macd.macd()
    df['macd'] = indicator_macd.macd_diff()
    #df['macd_signal'] = indicator_macd.macd_signal()
    
    df['obv'] = indicator_obv.on_balance_volume()
    
    df['vol_sma20'] = indicator_vol_sma20.sma_indicator()
    
    df['ema03'] = indicator_ema03.ema_indicator()
    df['ema05'] = indicator_ema05.ema_indicator()
    df['ema08'] = indicator_ema08.ema_indicator()
    df['ema10'] = indicator_ema10.ema_indicator()
    df['ema12'] = indicator_ema12.ema_indicator()
    df['ema15'] = indicator_ema15.ema_indicator()
    df['ema30'] = indicator_ema30.ema_indicator()
    df['ema35'] = indicator_ema35.ema_indicator()
    df['ema40'] = indicator_ema40.ema_indicator()
    df['ema45'] = indicator_ema45.ema_indicator()
    df['ema50'] = indicator_ema50.ema_indicator()
    df['ema60'] = indicator_ema60.ema_indicator()
    
    df['rsi14'] = indicator_rsi14.rsi()
    df['cci20'] = indicator_cci20

    ls_df.append(df.copy())
    
df = pd.concat(ls_df)

#df['cls'] = df['cls'].apply(lambda x: round(x,0))
#df['macd'] = df['macd_diff'].apply(lambda x: round(x,1))
#df['bb_bbhi'] = df['bb_bbhi'].apply(lambda x: round(x,0))
#df['bb_bbli'] = df['bb_bbli'].apply(lambda x: round(x,0))
#df['rsi'] = df['rsi'].apply(lambda x: round(x,0))

df['score_vol_sma20'] = df[['vol','vol_sma20']].apply(lambda x: x[0]/x[1],axis=1)

df['emash_min'] = df[['ema03','ema05','ema08','ema10','ema12','ema15']].min(axis=1)
df['emash_max'] = df[['ema03','ema05','ema08','ema10','ema12','ema15']].max(axis=1)
df['emash_avg'] = df[['ema03','ema05','ema08','ema10','ema12','ema15']].mean(axis=1)

#df['score_short'] = df[['cls','emash_min','emash_max','emash_min']].apply(lambda x: 100 * (x[0]-x[1])/(x[2]-x[3]),axis=1)


df['emalg_min'] = df[['ema30','ema35','ema40','ema45','ema50','ema60']].min(axis=1)
df['emalg_max'] = df[['ema30','ema35','ema40','ema45','ema50','ema60']].max(axis=1)
df['emalg_avg'] = df[['ema30','ema35','ema40','ema45','ema50','ema60']].mean(axis=1)

#df['score_long'] = df[['cls','emalg_min','emalg_max','emalg_min']].apply(lambda x: 100 * (x[0]-x[1])/(x[2]-x[3]),axis=1)

df['ema_min'] = df[['ema03','ema05','ema08','ema10','ema12','ema15','ema30','ema35','ema40','ema45','ema50','ema60']].min(axis=1)
df['ema_max'] = df[['ema03','ema05','ema08','ema10','ema12','ema15','ema30','ema35','ema40','ema45','ema50','ema60']].max(axis=1)

df['score_ovlp_ema'] = df[['emash_min','emalg_max','ema_max','ema_min']].apply(lambda x: 100 * (x[0]-x[1])/(x[2]-x[3]),axis=1)

df = pd.merge(df_stock, df, on =['sym'], how = 'inner').sort_values(['sort','ndays'])

decimals = pd.Series([1,0,0,2,0,0,2,0,0,0,0],index=['cls','ndays','vol','score_vol_sma20','bb_bbhi','bb_bbli','macd','obv','rsi14','cci20','score_ovlp_ema'])

cols = ['ndays','dte','sort','sym','cls','vol','score_vol_sma20','bb_bbhi','bb_bbli','macd','obv','rsi14','cci20','score_ovlp_ema']

df = df[df['ndays']<=10][cols].round(decimals).copy()

print(df['score_ovlp_ema'].min(),df['score_ovlp_ema'].max())

df[df['sym']=='QQQ'].head(50)


# In[5]:


df.to_csv('stock_selector_{}.csv'.format(end))


# In[ ]:




