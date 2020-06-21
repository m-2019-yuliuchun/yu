# -*- coding: utf-8 -*-
from __future__ import division  ###小数除法
import numpy as np
from config import config

default_encoding = "utf-8"
import pandas as pd
import os
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import datetime

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

from DataUtils import get_year_return, get_STK_MKTLink_StockInfoChg, get_year_return, get_year_AF_CfeatureProfile, \
    get_year_inshold, get_year_SRFR_Finidx, get_year_FAR_Finidx
from config import config


def calc_indicators():
    year_AIV = pd.read_csv(config['year_AIV'], dtype={'Stkcd': str, 'Trdyear': str})
    year_AIV = year_AIV[['Stkcd', 'Trdyear', 'year_AIV']].copy()


    year_AnaAttention = get_year_AF_CfeatureProfile()
    year_AnaAttention=year_AnaAttention[['Stkcd','Trdyear','AnaAttention']].copy()

    year_inshold = get_year_inshold()
    year_inshold=year_inshold[['Stkcd','Trdyear','inshold']].copy()

    year_bm=get_year_SRFR_Finidx()
    year_bm=year_bm[['Stkcd','Trdyear','bm']].copy()

    year_far = get_year_FAR_Finidx()
    year_far = year_far[['Stkcd', 'Trdyear', 'lev', 'size', 'cfo']].copy()

    year_return=get_year_return()
    year_return=year_return[['Stkcd','Trdyear','year_return']].copy()

    year_indicators=pd.merge(year_AIV, year_bm, on=['Stkcd','Trdyear'], how='left')
    year_indicators=pd.merge(year_indicators, year_far, on=['Stkcd','Trdyear'],how='left')
    year_indicators=pd.merge(year_indicators, year_inshold, on=['Stkcd','Trdyear'],how='left')
    year_indicators=pd.merge(year_indicators, year_AnaAttention, on=['Stkcd','Trdyear'],how='left')
    year_indicators=pd.merge(year_indicators, year_return, on=['Stkcd','Trdyear'],how='left')

    hkex = get_STK_MKTLink_StockInfoChg()
    year_indicators = pd.merge(year_indicators, hkex, on='Stkcd', how='left')
    year_indicators = year_indicators.fillna({'hkex': 0})  # 对hkex列填充
    year_indicators['after'] = year_indicators['Trdyear'].apply(lambda x: 0.0 if x < '2015' else 1.0)
    year_indicators = year_indicators.sort_values(['Stkcd', 'Trdyear'],ascending=[1,1]).reset_index(drop=True)
    year_indicators['hkex*after'] = year_indicators['hkex']*year_indicators['after']
    year_indicators['AIV_lead1'] = year_indicators.groupby('Stkcd')['year_AIV'].shift(-1).reset_index(drop=True)
    year_indicators = year_indicators.dropna().reset_index(drop=True) #删除shift产生的nan
    #print(year_indicators.head(1000))
    year_indicators = year_indicators[(year_indicators['Trdyear'] >= '2012') & (year_indicators['Trdyear'] <= '2015')]
    year_indicators.to_csv(config['year_indicators'], index=False, header=True)

    return year_indicators


if __name__ == "__main__":
    pass
    #print(calc_indicators())
    # year_indicators=pd.read_csv(config['year_indicators'], dtype={'Stkcd': str, 'Trdyear': str})
    # #print(year_indicators)
    # #reg1='var_fama_lead1~1+ hkex + after +hkex*after + AnaAttention + inshold + bm + size +lev +year_return'
    # reg1 = 'AIV_lead1~1+ hkex + after +hkex*after + bm +lev + size + cfo +inshold + + AnaAttention + year_return'
    # #reg1 = 'year_AIV~1+ hkex + after +hkex*after + bm +lev + size + cfo +inshold + + AnaAttention + year_return'
    # ols = smf.ols(data=year_indicators, formula=reg1).fit()
    # print(ols.summary())

