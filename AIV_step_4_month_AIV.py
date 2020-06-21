# -*- coding: utf-8 -*-
from __future__ import division  ###小数除法

import numpy as np

default_encoding = "utf-8"
import pandas as pd
import os
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)
year_month_parse = lambda x: pd.datetime.strptime(x, '%Y%m')
from config import config
from AIV_step_3_residual_return import get_day_residual_return
from DataUtils import get_IAR_Rept


def __gen_pea_nea__(labels):
    pea = []
    double_pea = []
    for label in labels:
        pea.extend(list(range(label - 60, label)))  # [-60,-1]
        double_pea.extend(list(range(label - 60, label + 6)))  # [-60,+5]
    pea_pd = pd.DataFrame(data=pea, columns=['pea'])
    double_pea_pd = pd.DataFrame(data=double_pea, columns=['double_pea'])
    return pea_pd, double_pea_pd


def calc_day_esidual_return_pea_nea():
    day_residual_return = get_day_residual_return()
    day_Annodt = get_IAR_Rept()
    day_data = pd.merge(day_residual_return, day_Annodt, left_on=['Stkcd', 'Trddt'], right_on=['Stkcd', 'Annodt'],
                        how='left')
    day_data = day_data.sort_values(['Stkcd', 'Trddt'], ascending=[1, 1]).reset_index(drop=True)
    day_data['label'] = range(len(day_data))
    day_data_Annodt = day_data.dropna().reset_index(drop=True)
    labels = day_data_Annodt['label'].values
    pea_pd, double_pea_pd = __gen_pea_nea__(labels)

    day_residual_return_pea = pd.merge(day_data, pea_pd, left_on=['label'], right_on=['pea'], how='inner')
    day_residual_return_nea = pd.merge(day_data, double_pea_pd, left_on=['label'], right_on=['double_pea'], how='left')
    day_residual_return_nea = day_residual_return_nea[day_residual_return_nea['double_pea'].isna()]  # 去除不为空的，留下的即为nea
    day_residual_return_pea['Trdmn'] = day_residual_return_pea['Trddt'].apply(lambda x: x.strftime('%Y%m'))
    day_residual_return_nea['Trdmn'] = day_residual_return_nea['Trddt'].apply(lambda x: x.strftime('%Y%m'))
    day_residual_return_pea = day_residual_return_pea[['Stkcd', 'Trddt', 'Trdmn', 'day_residual_return']].copy()
    day_residual_return_nea = day_residual_return_nea[['Stkcd', 'Trddt', 'Trdmn', 'day_residual_return']].copy()

    # 重新设置索引
    day_residual_return_pea = day_residual_return_pea.reset_index(drop=True)
    day_residual_return_nea = day_residual_return_nea.reset_index(drop=True)

    day_residual_return_pea.to_csv(config['day_residual_return_pea'], header=True, index=False)
    day_residual_return_nea.to_csv(config['day_residual_return_nea'], header=True, index=False)


def gen_year_month_sequenece():
    data_ranges = pd.Series(pd.date_range('20110101', end='20171231', freq='M'))

    data_ranges['year_month'] = data_ranges.apply(lambda x: x.strftime("%Y%m"))
    data_ranges['index'] = data_ranges['year_month']
    data = pd.DataFrame({'index': data_ranges['index'], 'year_month': data_ranges['year_month']}, dtype='str')
    year_month_sequence = data.set_index(keys='index')
    return year_month_sequence


def __calc_month_indicator__(rdata, max_year_month):
    if rdata['Trdmn'].max() != max_year_month:
        return pd.Series({'Trdmn': max_year_month, 'res': np.NAN})
    try:
        res = np.log(np.sqrt((252 * np.sum(rdata['day_residual_return'] ** 2)) / (rdata.shape[0] - 1)))
        result = pd.Series({'Trdmn': max_year_month, 'res': res})
        return result
    except Exception as e:
        print(e)


def __roll_month_indicator__(data_range, day_data, save_file):
    year_month_pd = data_range.to_frame()
    year_month_pd.columns = ['Trdmn']
    max_year_month = year_month_pd['Trdmn'].max()
    max_year_month = str(int(max_year_month))
    year_month_pd['Trdmn'] = year_month_pd['Trdmn'].apply(lambda x: str(int(x)))
    # 从数据集中筛选出12个月数据，
    day_trade_data_rf = pd.merge(year_month_pd, day_data, on='Trdmn', how='inner')  # float转字符串
    # 对每只股票做回归
    res = day_trade_data_rf.groupby('Stkcd').apply(__calc_month_indicator__, max_year_month).reset_index(drop=False)
    print(res.head(5))
    res.to_csv(config[save_file], mode='a', index=False, header=0)  # df.to_csv, 参数mode='a'表示追加
    return 1.0


def calc_month_indicator(day_data, save_file, rolling_months):
    year_month_sequence = gen_year_month_sequenece()

    day_return = day_data[['Stkcd', 'Trddt', 'Trdmn', 'day_residual_return']].copy()
    if os.access(config[save_file], os.F_OK):
        os.remove(config[save_file])  ###若文件存在，先删除
    month_ivol = pd.DataFrame(columns=['Stkcd', 'Trdmn', 'res'], dtype=object)
    month_ivol.to_csv(config[save_file], header=True, index=False)
    # 12个月一次rolling
    # 计算过程：每12个月滚动一次，每一次对每只股票的12个月数据做回归
    year_month_sequence.rolling(rolling_months).apply(
        lambda data_range: __roll_month_indicator__(data_range, day_return, save_file), raw=False)


def calc_year_AIV():
    day_residual_return_iv_pea = pd.read_csv(config['day_residual_return_iv_pea'],dtype={'Stkcd': str, 'Trdmn': str}, sep=',')
    day_residual_return_iv_pea = day_residual_return_iv_pea.sort_values(['Stkcd','Trdmn'], ascending=[1,1]).reset_index(drop=True)
    day_residual_return_iv_pea = day_residual_return_iv_pea.fillna(method='ffill').reset_index(drop=True)
    day_residual_return_iv_pea = day_residual_return_iv_pea.rename(columns={'res': 'month_pea_iv'})
    day_residual_return_iv_nea = pd.read_csv(config['day_residual_return_iv_nea'],dtype={'Stkcd': str, 'Trdmn': str}, sep=',')
    day_residual_return_iv_nea = day_residual_return_iv_nea.sort_values(['Stkcd','Trdmn'],ascending=[1,1]).reset_index(drop=True)
    day_residual_return_iv_nea = day_residual_return_iv_nea.fillna(method='ffill').reset_index(drop=True)
    day_residual_return_iv_nea = day_residual_return_iv_nea.rename(columns={'res': 'month_nea_iv'})

    month_data = pd.merge(day_residual_return_iv_pea, day_residual_return_iv_nea, on=['Stkcd','Trdmn'], how='inner')
    month_data['month_aiv'] = month_data['month_pea_iv']-month_data['month_nea_iv']
    month_aiv = month_data[['Stkcd','Trdmn','month_aiv']].copy()
    month_aiv['month_aiv_lead4'] = month_aiv.groupby('Stkcd')['month_aiv'].shift(-4).reset_index(drop=True)
    month_aiv = month_aiv.dropna().reset_index(drop=True)
    month_aiv['Trdyear'] = month_aiv['Trdmn'].apply(lambda x:x[:4])#取得年份
    year_AIV = month_aiv.groupby(['Stkcd', 'Trdyear'])['month_aiv_lead4'].apply(np.mean).reset_index(drop=False).rename(columns={'month_aiv_lead4':"year_AIV"})
    print(year_AIV.head(10))
    year_AIV.to_csv(config['year_AIV'], index=False, header=True)

    return year_AIV



if __name__ == "__main__":
    pass
    #calc_day_esidual_return_pea_nea()
    # 滚动回归求iv_pea,iv_nea
    #day_residual_return_pea = pd.read_csv(config['day_residual_return_pea'], parse_dates=['Trddt'], dtype={'Stkcd': str, 'Trdmn': str}, sep=',')

    #day_residual_return_nea = pd.read_csv(config['day_residual_return_nea'], parse_dates=['Trddt'], dtype={'Stkcd': str, 'Trdmn': str}, sep=',')

    #calc_month_indicator(day_data=day_residual_return_pea, save_file='day_residual_return_iv_pea', rolling_months=12)
    #calc_month_indicator(day_data=day_residual_return_nea, save_file='day_residual_return_iv_nea', rolling_months=12)
    calc_year_AIV()
