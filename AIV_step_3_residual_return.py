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
from DataUtils import get_day_ff5, get_day_return
from AIV_step_2_day_expect_return import get_day_expected_return

"""

1.	估计个股的日度残差
"""

def calc_day_residual_return():
    """
    求日预期收益
    :return:
    """
    day_return = get_day_return()
    day_return = day_return[['Stkcd', 'Trddt', 'day_return_rf']].copy()
    day_expected_return = get_day_expected_return()

    day_residual_return = pd.merge(day_return, day_expected_return, on=['Stkcd', 'Trddt'], how='inner')
    day_residual_return['day_residual_return'] = day_residual_return['day_return_rf'] - \
                                                 day_residual_return['day_expected_return']
    day_residual_return = day_residual_return[['Stkcd', 'Trddt', 'day_residual_return']].copy()
    day_residual_return.to_csv(config['day_residual_return'], index=False, header=True)
    return day_residual_return


def get_day_residual_return():
    return pd.read_csv(config['day_residual_return'],parse_dates=['Trddt'],dtype={"Stkcd": str}, sep=',')


if __name__ == "__main__":
    pass
    print(calc_day_residual_return().head(10))
    #print(get_day_residual_return().head())
