# -*- coding: utf-8 -*-
from __future__ import division  ###小数除法

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import config

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)
from DataUtils import get_day_ff5
from AIV_step_1_day_betas_regression import get_day_betas_ff3

"""

1.	估计个股的日度预期收益率
"""

def calc_day_expected_return():
    """
    求日预期超额收益
    :return:
    """
    day_betas_ff3 = get_day_betas_ff3()
    day_ff5 = get_day_ff5()
    day_ff5 = day_ff5[day_ff5['Trddt'] >= '20090101'].reset_index(drop=True)
    day_ff5 = day_ff5.sort_values(['Trddt']).reset_index(drop=True)
    day_ff5 = day_ff5[['Trddt', 'mkt_rf', 'smb', 'hml', 'rf']].copy()
    day_ff5.columns = ['Trddt', 'E_mkt_rf', 'E_smb', 'E_hml', 'E_rf']
    day_expected_return = pd.merge(day_betas_ff3, day_ff5, on=['Trddt'], how='inner')
    day_expected_return['day_expected_return'] = day_expected_return['mkt_rf'] * day_expected_return['E_mkt_rf'] + \
                                                 day_expected_return['smb'] * day_expected_return['E_smb'] + \
                                                 day_expected_return['hml'] * day_expected_return['E_hml']
    day_expected_return = day_expected_return[['Stkcd', 'Trddt', 'day_expected_return']].copy()
    day_expected_return.to_csv(config['day_expected_return'], header=True, index=False)
    return day_expected_return

def get_day_expected_return():
    return pd.read_csv(config['day_expected_return'],parse_dates=['Trddt'], dtype={"Stkcd": str}, sep=',')



if __name__ == "__main__":
    pass
    #print(calc_day_expected_return())
    #print(get_day_expected_return().head(100))
