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
from scipy.stats.mstats import winsorize
from linearmodels.datasets import jobtraining
from linearmodels import PanelOLS
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix


#model = LogisticRegression(solver='liblinear', random_state=0).fit(x, y)

from DataUtils import get_STK_MKTLink_StockInfo, get_year_QFII, get_MNMAPR_Accruals, get_industry_type, get_STK_HKEXtoSSE_Top10

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)


def __ols_effect__():
    """
    忽略此函数
    :return:
    """
    reg1 = 'AIV_lead1~1+ hkex + after +hkex*after + bm +lev + size + cfo +inshold + + AnaAttention + year_return'
    ols = smf.ols(data=year_indicators, formula=reg1).fit()
    result = ols.summary()
    return result


def get_reslut_one():
    year_indicators = pd.read_csv(config['year_indicators'], dtype={'Stkcd': str, 'Trdyear': str})
    year_indicators['AIV_lead1'] = winsorize(year_indicators['AIV_lead1'], (0.01, 0.01))
    STK_MKTLink_StockInfo = get_STK_MKTLink_StockInfo()
    STK_MKTLink_StockInfo['Stkcd'] = STK_MKTLink_StockInfo['Stkcd'].astype(str)
    year_QFII = get_year_QFII()
    year_QFII['Stkcd'] = year_QFII['Stkcd'].astype(str)
    year_indicators = pd.merge(year_indicators, STK_MKTLink_StockInfo, on='Stkcd', how='left')
    year_indicators = year_indicators[year_indicators['WhetherAandH'] != 'Y']
    year_indicators = pd.merge(year_indicators, year_QFII, on=['Stkcd','Trdyear'], how='inner') #剔除境外投资者持股影响
    print(year_indicators)
    print(year_indicators.describe())
    reg1 = 'AIV_lead1~1+ hkex + after +hkex*after + bm +lev + size + cfo +inshold + AnaAttention + year_return'
    #reg1 = 'year_AIV~1+ hkex + after +hkex*after + bm +lev + size + cfo +inshold + AnaAttention + year_return'
    ols = smf.ols(data=year_indicators, formula=reg1).fit()
    return ols.summary()

def get_reslut_two():
    """
    香港资金参与程度分组
    :return:
    """
    year_indicators = pd.read_csv(config['year_indicators'], dtype={'Stkcd': str, 'Trdyear': str})
    year_indicators['AIV_lead1'] = winsorize(year_indicators['AIV_lead1'], (0.01, 0.01))
    year_indicators['year_AIV'] = winsorize(year_indicators['year_AIV'], (0.01, 0.01))
    STK_HKEXtoSSE_Top10 = get_STK_HKEXtoSSE_Top10()
    year_indicators = pd.merge(year_indicators, STK_HKEXtoSSE_Top10, on='Stkcd', how='left')
    print(year_indicators)
    year_indicators = year_indicators.fillna({'top_ten': 'low'})  # 对top_ten列填充
    year_indicators_high = year_indicators[year_indicators['top_ten'] == 'high']
    year_indicators_low = year_indicators[year_indicators['top_ten'] == 'low']
    # print(year_indicators_high)
    # print(year_indicators_high.describe())
    # print(year_indicators_low)
    # print(year_indicators_low.describe())
    reg1 = 'AIV_lead1~1+ hkex + after +hkex*after + bm +lev + size + cfo +inshold + AnaAttention + year_return'
    #reg1 = 'year_AIV~1+ hkex + after +hkex*after + bm +lev + size + cfo +inshold + AnaAttention + year_return'
    ols_high = smf.ols(data=year_indicators_high, formula=reg1).fit()
    ols_low = smf.ols(data=year_indicators_low, formula=reg1).fit()
    return ols_high.summary(), ols_low.summary()






def get_dacc_sigma():
    MNMAPR_Accruals = get_MNMAPR_Accruals()
    industry_type = get_industry_type()
    dacc_sigma = pd.merge(MNMAPR_Accruals, industry_type, on='Stkcd', how='left')
    dacc_sigma = dacc_sigma.dropna()

    return dacc_sigma


def __alpha_betas__(rdata, regModel, NWlag=12):
    """
    忽略此文件
    :param rdata:
    :param regModel:
    :param NWlag:
    :return:
    """
    ols = smf.ols(formula=regModel, data=rdata) \
        .fit(cov_type='HAC', cov_kwds={'maxlags': NWlag, 'use_correction': True})
    params=ols.params
    t_stats=ols.tvalues
    p_values=ols.pvalues
    t_stats.index=t_stats.index.to_series().apply(lambda x:x+"_t").values
    p_values.index=p_values.index.to_series().apply(lambda x:x+"_p").values
    output=pd.concat([params, t_stats, p_values], axis=0)#数据合并
    output['Num.Obs.']=ols.nobs
    output['R-squared-adj']=ols.rsquared_adj
    output=pd.DataFrame(data=output.values.reshape([1,-1]),columns=output.index.to_series().values)
    output = output.apply(lambda x: __alpha_betas_significant__(x, params.index, p_values.index), axis=1)
    return output




if __name__ == "__main__":
    pass
    # year_indicators = pd.read_csv(config['year_indicators'], dtype={'Stkcd': str, 'Trdyear': str})
    # year_indicators['AIV_lead1'] = winsorize(year_indicators['AIV_lead1'], (0.01, 0.01))
    # STK_MKTLink_StockInfo = get_STK_MKTLink_StockInfo()
    # STK_MKTLink_StockInfo['Stkcd'] = STK_MKTLink_StockInfo['Stkcd'].astype(str)
    # year_QFII = get_year_QFII()
    # year_QFII['Stkcd'] = year_QFII['Stkcd'].astype(str)
    # year_indicators = pd.merge(year_indicators, STK_MKTLink_StockInfo, on='Stkcd', how='left')
    # year_indicators = year_indicators[year_indicators['WhetherAandH'] != 'Y']
    # year_indicators = pd.merge(year_indicators, year_QFII, on=['Stkcd','Trdyear'], how='inner') #剔除境外投资者持股影响
    # print(year_indicators)
    # print(year_indicators.describe())
    # reg1 = 'AIV_lead1~1+ hkex + after +hkex*after + bm +lev + size + cfo +inshold + + AnaAttention + year_return'
    #reg1 = 'year_AIV~1+ hkex + after +hkex*after + bm +lev + size + cfo +inshold + + AnaAttention + year_return'
    # ols = smf.ols(data=year_indicators, formula=reg1).fit()
    # print(ols.summary())
    # print(year_indicators)
    # print(get_reslut_one())
    # print(get_dacc_sigma())
    #print(get_reslut_two())
