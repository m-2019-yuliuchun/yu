#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import division  ###小数除法
import numpy as np
from config import config

default_encoding = "utf-8"
import pandas as pd
import os
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import datetime
import numpy as np
from scipy.stats.mstats import winsorize
from linearmodels.datasets import jobtraining
from linearmodels import PanelOLS

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

from DataUtils import get_MNMAPR_Accruals

def gen_year_sequenece(start_day, end_day):
    data_ranges = pd.Series(pd.date_range(start=start_day, end=end_day, freq='Y'))

    data_ranges['Trdyear'] = data_ranges.apply(lambda x: x.strftime("%Y"))
    data_ranges['index'] = data_ranges['Trdyear']
    data = pd.DataFrame({'index': data_ranges['index'], 'Trdyear': data_ranges['Trdyear']}, dtype='str')
    day_sequence = data.set_index(keys='index')
    return year_sequence


def __ols_year_alpha__(rdata, regModel, max_year, NWlag):
    max_year_str = datetime.datetime.strftime(max_year, '%Y')
    if rdata['Trdyear'].max() != max_day:
        return pd.Series(
            data=[np.NAN, np.NAN, np.NAN, max_year_str],
            index=['b_one', 'b_two', 'b_three', 'Trdyear'])
    if rdata.shape[0] < 4:
        return pd.Series([np.NAN, np.NAN, np.NAN, max_day_str],
                         index=['b_one', 'b_two', 'b_three', 'Trdyear'])

    try:
        ols = smf.ols(formula=regModel, data=rdata).fit(cov_type='HAC',
                                                        cov_kwds={'maxlags': NWlag, 'use_correction': True})
        params = ols.params
        params['Trdyear'] = max_year_str
        return params
    except Exception as e:
        print(e)


# def __roll_year_beta__(dacc_indicators, regModel, max_year, NWlag):
#     max_year = max_year
#     # 对每只股票回归
#     ols_res = dacc_indicators.groupby('Stkcd').apply(__ols_year_beta__, regModel, max_year, NWlag).reset_index(
#         drop=False)
#     print(ols_res.head(10))
#     ols_res.to_csv(config['dacc_betas'], mode='a', index=False, header=0)  # df.to_csv, 参数mode='a'表示追加
#     return 1.0


def calc_day_beta(start_day, end_day, reg_model, NWlag=1):
    year_sequence = gen_year_sequenece(start_day, end_day)
    dacc_indicators = get_MNMAPR_Accruals()
    data = dacc_indicators[['Stkcd', 'Trdyear', 'TA_M', 'A', 'D_REV', 'PPE']].copy()
    data = data.sort_values(['Stkcd', 'Trdyear'], ascending=[1, 1]).reset_index(drop=True)

    regModel = reg_model
    if os.access(config['dacc_betas'], os.F_OK):
        os.remove(config['dacc_betas'])  ###若文件存在，先删除
    dacc_beta = pd.DataFrame(columns=['Stkcd', 'b_one', 'b_two', 'b_three', 'Trdyear'], dtype=object)
    day_beta.to_csv(config['dacc_betas'], header=True, index=False)

            data_pd = day_data[(day_data['Trddt'] >= last_year_day) & (day_data['Trddt'] <= now_day)]
            # 对数据集中的每只股票回归
            __roll_day_beta__(data_pd, regModel, save_file, now_day, NWlag)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    pass
    dacc_indicators = get_MNMAPR_Accruals()
    #MNMAPR_Accruals = MNMAPR_Accruals[['Stkcd', 'Trdyear', 'TA_M', 'A', 'D_REV_REC', 'PPE', 'TA_R', 'ROE']].copy()
    reg1 = 'TA_M~A + D_REV +PPE '
    ols = smf.ols(data=year_indicators, formula=reg1).fit()