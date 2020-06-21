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

from DataUtils import get_day_return, get_day_ff5
from config import config

"""
1、首先使用Fama-French三因子模型的残差来计算异常特质波动率（AIV）

=> Step1 先估计出每只股票的日度β_(mkt,t)、β_(smb,t)和β_(hml,t)值。
使用过去1年滚动窗口（至少180日）的日收益率数据来估计的以上三个beta系数，
因为使用过去1年的日数据，因而个股数据从2012年开始

Step 2 使用Fama-french 3因子模型估计条件预期收益率μ_t

Step 3 基于以上Step 2得出的μ_t，以及每只股票的已实现收益率（即日个股回报率）ri,t，计算每日残差收益率

"""


def gen_day_sequenece(start_day, end_day):
    data_ranges = pd.Series(pd.date_range(start=start_day, end=end_day, freq='d'))

    data_ranges['Trddt'] = data_ranges.apply(lambda x: x.strftime("%Y%m%d"))
    data_ranges['index'] = data_ranges['Trddt']
    data = pd.DataFrame({'index': data_ranges['index'], 'Trddt': data_ranges['Trddt']}, dtype='str')
    day_sequence = data.set_index(keys='index')
    return day_sequence


def __ols_day_beta__(rdata, regModel, max_day, NWlag):
    max_day_str = datetime.datetime.strftime(max_day, '%Y%m%d')
    if rdata['Trddt'].max() != max_day:
        return pd.Series(
            data=[datetime.datetime.strftime(rdata['Trddt'].max(), '%Y%m%d'), np.NAN, np.NAN, np.NAN, max_day_str],
            index=['Intercept', 'mkt_rf', 'smb', 'hml', 'Trddt'])
    if rdata.shape[0] < 180:
        return pd.Series(data=[rdata.shape[0], np.NAN, np.NAN, np.NAN, max_day_str],
                         index=['Intercept', 'mkt_rf', 'smb', 'hml', 'Trddt'])

    try:
        ols = smf.ols(formula=regModel, data=rdata).fit(cov_type='HAC',
                                                        cov_kwds={'maxlags': NWlag, 'use_correction': True})
        params = ols.params
        params['Trddt'] = max_day_str
        return params
    except Exception as e:
        print(e)


def __roll_day_beta__(day_return_index, regModel, save_file, max_day, NWlag):
    max_day = max_day
    # 对每只股票回归
    ols_res = day_return_index.groupby('Stkcd').apply(__ols_day_beta__, regModel, max_day, NWlag).reset_index(
        drop=False)
    print(ols_res.head(10))
    ols_res.to_csv(config[save_file], mode='a', index=False, header=0)  # df.to_csv, 参数mode='a'表示追加
    return 1.0



def calc_day_beta(start_day, end_day, reg_model, save_file, NWlag=1):
    day_sequence = gen_day_sequenece(start_day, end_day)
    day_return = get_day_return()
    day_ff5 = get_day_ff5()
    day_ff5 = day_ff5[['Trddt', 'mkt_rf', 'smb', 'hml']].copy()
    day_data = pd.merge(day_return, day_ff5, on=['Trddt'], how='inner')

    day_data = day_data[['Stkcd', 'Trddt', 'close_2_close_day_return_rf', 'mkt_rf', 'smb', 'hml']].copy()
    day_data = day_data.sort_values(['Stkcd', 'Trddt'], ascending=[1, 1]).reset_index(drop=True)

    regModel = reg_model
    if os.access(config[save_file], os.F_OK):
        os.remove(config[save_file])  ###若文件存在，先删除
    day_beta = pd.DataFrame(columns=['Stkcd', 'Intercept', 'mkt_rf', 'smb', 'hml', 'Trddt'], dtype=object)
    day_beta.to_csv(config[save_file], header=True, index=False)
    # 对每一天回归
    for now_day_str in day_sequence['Trddt']:
        try:
            now_day = pd.datetime.strptime(now_day_str, "%Y%m%d")

            last_year_day = (now_day - datetime.timedelta(days=365))
            # 取得过去一年的数据
            data_pd = day_data[(day_data['Trddt'] >= last_year_day) & (day_data['Trddt'] <= now_day)]
            # 对数据集中的每只股票回归
            __roll_day_beta__(data_pd, regModel, save_file, now_day, NWlag)
        except Exception as e:
            print(e)


def get_day_betas_ff3():
    day_betas_ff3 = pd.read_csv(config["day_betas_ff3"], header=0, parse_dates=['Trddt'], dtype={'Stkcd': str})
    # day_beta=day_beta.fillna(method='ffill')#对于不符合条件的填充
    day_betas_ff3 = day_betas_ff3.dropna().reset_index(drop=True)  # 对于不符合条件的删除
    return day_betas_ff3


if __name__ == "__main__":
    pass
    #save_file = 'close_2_close_day_return_rf_beta'
    #reg_model = 'close_2_close_day_return_rf ~1+mkt_rf+smb+hml'  # 当期收益 与当期市场因子
    # 1.计算每只股票的day beta
    # calc_day_beta(start_day='20100101', end_day='20200101', reg_model=reg_model, save_file=save_file, NWlag=12)
    #print(get_day_betas_ff3().head(1000))
    #print(gen_day_sequenece('20120101', '20201231'))
