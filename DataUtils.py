# -*- coding: utf-8 -*-
from __future__ import division  ###小数除法

from functools import reduce

from config import config
import datetime

default_encoding = "utf-8"
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)


def getFilePathList(path):
    """
    path 路径下所有文件
    :param path:
    :return:
    """
    file_path_list = []
    for root, dirs, files in os.walk(path):
        for filespath in files:
            file_path_list.append(os.path.join(root, filespath))
    return file_path_list

def calc_part_day_trade_data(path):
    """
    取得部分股票数据
    :param path:
    :return:
    """
    data = pd.read_csv(path, parse_dates=['Trddt'], sep='\t', usecols=['Stkcd', 'Trddt', 'Clsprc', 'Trdsta', 'Dsmvosd'],
                       dtype={'Stkcd': str, 'Trdsta': str})
    data = data.replace("--", np.nan).dropna()  # 剔除na的数据，则包含剔除了停牌的数据
    data = data[(data['Trdsta'] == '1')]
    data = data.sort_values(["Stkcd", "Trddt"], ascending=[1, 1]).reset_index(drop=True)
    data['Clsprc'] = data['Clsprc'].astype(float)  # 收盘价
    data['Trdmn'] = data['Trddt'].apply(lambda x: x.strftime("%Y%m"))
    day_trade_data = data[['Stkcd', 'Trddt', 'Clsprc', 'Dsmvosd', 'Trdmn']].copy()
    return day_trade_data

def calc_day_trade_data():
    """
    计算所有股票的日数据
    包含流通市值数据Dsmvosd
    :return: 汇总所有数据
    """

    save_file_path = config['day_trade_data']
    if os.access(save_file_path, os.F_OK):
        os.remove(save_file_path)  ###若文件存在，先删除
    data = pd.DataFrame(columns=['Stkcd', 'Trddt', 'close_price', 'Dsmvosd', 'Trdmn'], dtype=object)
    data.to_csv(save_file_path, index=False)
    file_paths = getFilePathList(config['day_trade_data_path'])
    for path in file_paths:
        print(path)
        data = calc_part_day_trade_data(path)
        data.to_csv(save_file_path, mode='a', index=False, header=0)  # df.to_csv, 参数mode='a'表示追加

def get_day_trade_data():
    day_trade_data = pd.read_csv(config['day_trade_data'], parse_dates=['Trddt'], low_memory=False,
                                 dtype={'Stkcd': str, 'Trdmn': str})
    day_trade_data = day_trade_data[['Stkcd', 'Trddt', 'close_price', 'Trdmn']].copy()
    day_trade_data = day_trade_data.sort_values(['Stkcd', 'Trddt'], ascending=[1, 1]).reset_index(drop=True)
    return day_trade_data

def get_industry_type():
    """
    金融行业代码是40
    剔除金融行业
    行业年度回归
    :return:
    """
    industry_type = pd.read_excel(config['industry_type'], dtype={'Stkcd': str, 'wind_industry_type': str})
    industry_type = industry_type[industry_type['wind'] != 40]
    industry_type.columns = ['Stkcd', 'wind_industry_name', 'wind_industry_type']
    industry_type['Stkcd'] = industry_type['Stkcd'].apply(lambda x: str(x).split(".")[0])
    industry_type = industry_type.astype({'Stkcd': str, 'wind_industry_type': str})
    return industry_type




def get_STK_MKTLink_StockInfoChg():
    """
    沪港通与深港通标的证券基本信息轨迹表
    Stkcd [证券代码]
    MarketLinkCode [市场通代码]
    Trddt [变动日期]
    ChangeType [变动方向]
    :return:
    """
    STK_MKTLink_StockInfoChg = pd.read_csv(config['STK_MKTLink_StockInfoChg'], encoding='utf-16', sep='\t',
                                           parse_dates=['ChangeDate'], dtype={'Symbol': str})
    STK_MKTLink_StockInfoChg = STK_MKTLink_StockInfoChg.rename(columns={"Symbol": "Stkcd", "ChangeDate": "Trddt"})
    # 筛选ChangeDate为2015之前所有调入的股票
    STK_MKTLink_StockInfoChg = STK_MKTLink_StockInfoChg[
        (STK_MKTLink_StockInfoChg['Trddt'] < '2015-01-01') & (STK_MKTLink_StockInfoChg['ChangeType'] == '调入')]
    STK_MKTLink_StockInfoChg = STK_MKTLink_StockInfoChg.reset_index(drop=True)
    STK_MKTLink_StockInfoChg['hkex'] = 1
    STK_MKTLink_StockInfoChg = STK_MKTLink_StockInfoChg[['Stkcd', 'hkex']].copy()
    return STK_MKTLink_StockInfoChg


def get_IAR_Rept():
    """
    年、中、季报基本情况
    Stkcd [证券代码]
    Annodt [报告公布日期]
    :return:
    """
    IAR_Rept = pd.read_csv(config['IAR_Rept'], encoding='gbk', sep=',', parse_dates=['Annodt'], dtype={'Stkcd': str},
                           usecols=['Stkcd', 'Annodt'])
    IAR_Rept = IAR_Rept.drop_duplicates()  # 公告日期有重复数据

    IAR_Rept = IAR_Rept.reset_index(drop=True)

    return IAR_Rept


def get_day_ff5():
    """
    日5因子
    :return:
    """
    day_ff5 = pd.read_csv(config['day_ff5'], parse_dates=['trddy'], low_memory=False, sep='\t')
    day_ff5 = day_ff5.rename(columns={'trddy': 'Trddt'})
    day_ff5 = day_ff5.sort_values(["Trddt"], ascending=[1]).reset_index(drop=True)
    day_ff5 = day_ff5.dropna()
    return day_ff5

def get_year_return():
    """
    年个股回报率
    Yretwd [考虑现金红利再投资的年个股回报率]
    :return:
    """

    year_return = pd.read_csv(config['year_return'], encoding='utf-16', sep='\t', dtype={'Stkcd': str,'Trdyear':str},
                              usecols=['Stkcd', 'Trdynt', 'Yretwd'])
    year_return = year_return.rename(columns={'Trdynt': 'Trdyear', "Yretwd": "year_return"})
    year_return['Trdyear']=year_return['Trdyear'].astype(str)
    year_return = year_return.sort_values(['Stkcd', 'Trdyear'], ascending=[1, 1]).reset_index(drop=True)
    return year_return


def get_year_FAR_Finidx():
    """
    财务指标文件
    证券代码（Stkcd），
    会计年度（Accper），
    总资产TA（A100000）,
    资产负债率LEV(T30100)，
    经营活动产生的经营现金流量净额CF(D100000)，
    资产收益率（T40402）
    :return:
    """
    year_FAR_Finidx = pd.read_csv(config['year_FAR_Finidx'], encoding='utf-16', sep='\t',
                                  usecols=['Stkcd', 'Accper', 'A100000', 'D100000', 'T30100', 'T40402'],
                                  dtype={'Stkcd': str}, parse_dates=['Accper'])

    year_FAR_Finidx.columns = ['Stkcd', 'Accper', 'ta', 'cf', 'lev', 'roe']
    year_FAR_Finidx['Trdyear'] = year_FAR_Finidx['Accper'].apply(lambda x: datetime.datetime.strftime(x, "%Y"))  # 提取年份

    year_FAR_Finidx['size'] = np.log(year_FAR_Finidx['ta']+1)  # SIZE公司规模（总资产自然对数）= ln（总资产）
    year_FAR_Finidx['cfo'] = year_FAR_Finidx['cf'] / year_FAR_Finidx['ta']  # CFO经营活动现金流=CF（经营活动产生的经营现金流量净额）/TA(总资产)

    year_FAR_Finidx = year_FAR_Finidx.reset_index(drop=True)

    return year_FAR_Finidx


def get_year_inshold():
    """
    机构持股分类表
    机构持股比例

    :return:
    """

    year_INI_HolderSystematics = pd.read_csv(config['year_INI_HolderSystematics'], encoding='utf-16', sep='\t',
                                             dtype={'Symbol': str}, parse_dates=['EndDate'],
                                             usecols=['Symbol', 'EndDate', 'FundHoldProportion', 'QFIIHoldProportion',
                                                      'BrokerHoldProportion', 'InsuranceHoldProportion',
                                                      'SecurityFundHoldProportion', 'EntrustHoldProportion',
                                                      'FinanceHoldProportion', 'BankHoldProportion',
                                                      'NonFinanceHoldProportion'])
    year_INI_HolderSystematics = year_INI_HolderSystematics.fillna(0.0)
    year_INI_HolderSystematics = year_INI_HolderSystematics.rename(columns={"Symbol": "Stkcd"})
    year_INI_HolderSystematics['Trdyear'] = year_INI_HolderSystematics['EndDate'].apply(
        lambda x: datetime.datetime.strftime(x, "%Y"))  # 提取年份
    year_INI_HolderSystematics = year_INI_HolderSystematics.sort_values(['Stkcd', 'EndDate'],
                                                                        ascending=[1, 1]).reset_index(drop=True)
    year_INI_HolderSystematics['inshold'] = year_INI_HolderSystematics['FundHoldProportion'] + \
                                            year_INI_HolderSystematics['QFIIHoldProportion'] + \
                                            year_INI_HolderSystematics['BrokerHoldProportion'] + \
                                            year_INI_HolderSystematics['InsuranceHoldProportion'] + \
                                            year_INI_HolderSystematics['SecurityFundHoldProportion'] + \
                                            year_INI_HolderSystematics['EntrustHoldProportion'] + \
                                            year_INI_HolderSystematics['FinanceHoldProportion'] + \
                                            year_INI_HolderSystematics['BankHoldProportion'] + \
                                            year_INI_HolderSystematics['NonFinanceHoldProportion']
    year_INI_HolderSystematics['inshold'] = year_INI_HolderSystematics['inshold']/100
    year_INI_HolderSystematics = year_INI_HolderSystematics.groupby(['Stkcd', 'Trdyear'])['inshold'].apply(
        lambda x: x.iloc[-1]).reset_index(drop=False)
    year_inshold = year_INI_HolderSystematics[['Stkcd', 'Trdyear', 'inshold']].copy()
    return year_inshold


def get_year_AF_CfeatureProfile():
    """
 	文件“上市公司基本信息特色指标表”,年度数据
 	证券代码（stkcd）
 	会计年度（trdd）
 	被分析师关注度（AnaAttention）
    :return:
    """

    year_AF_CfeatureProfile = pd.read_csv(config['year_AF_CfeatureProfile'], encoding='utf-16', sep='\t',
                                          parse_dates=['Accper'], dtype={'Stkcd': str},
                                          usecols=['Stkcd', 'Accper', 'AnaAttention'])
    year_AF_CfeatureProfile['Trdyear'] = year_AF_CfeatureProfile['Accper'].apply(
        lambda x: datetime.datetime.strftime(x, "%Y"))  # 提取年份

    year_AF_CfeatureProfile = year_AF_CfeatureProfile.sort_values(['Stkcd', 'Trdyear'], ascending=[1, 1]).reset_index(
        drop=True)
    year_AF_CfeatureProfile = year_AF_CfeatureProfile.fillna(0.0)
    return year_AF_CfeatureProfile


def get_year_SRFR_Finidx():
    """
    文件“指标文件”，年度数据，J。证券代码（Stkcd） ，会计年度（Accper），账面市值比BM(Bktomk)
    :return:
    """

    year_SRFR_Finidx = pd.read_csv(config['year_SRFR_Finidx'], encoding='utf-16', sep='\t', dtype={'Stkcd': str},
                                   parse_dates=['Accper'], usecols=['Stkcd', 'Accper', 'Bktomk'])
    year_SRFR_Finidx = year_SRFR_Finidx.rename(columns={"Bktomk": "bm"})
    year_SRFR_Finidx['Trdyear'] = year_SRFR_Finidx['Accper'].apply(
        lambda x: datetime.datetime.strftime(x, "%Y"))  # 提取年份
    year_SRFR_Finidx = year_SRFR_Finidx.sort_values(['Stkcd', 'Trdyear'], ascending=[1, 1]).reset_index(drop=True)
    return year_SRFR_Finidx


def calc_day_return():
    """
    日收益数据
    :return:
    """
    day_trade_data = get_day_trade_data()
    day_ff5 = get_day_ff5()
    day_ff5 = day_ff5[['Trddt', 'rf']].copy()
    day_return = pd.merge(day_trade_data, day_ff5, on=['Trddt'], how='inner')
    day_return = day_return.sort_values(['Stkcd', 'Trddt'], ascending=[1, 1]).reset_index(drop=True)  # 排序
    day_return['close_price_lag1'] = day_return.groupby(['Stkcd'])['close_price'].shift(1).reset_index(drop=True)
    day_return = day_return.dropna().reset_index(drop=True)
    day_return['day_return'] = np.log(day_return['close_price']) - np.log(
        day_return['close_price_lag1'])  # 对数收益
    day_return['day_return_rf'] = day_return['day_return'] - day_return['rf']  # 对数收益-rf
    day_return = day_return[['Stkcd', 'Trddt', 'day_return', 'day_return_rf']].copy()
    day_return.to_csv(config['day_return'], index=False, header=True)
    return day_return


def get_day_return():
    day_return = pd.read_csv(config['day_return'], parse_dates=['Trddt'], dtype={'Stkcd': str})
    return day_return


def get_STK_HKEXtoSSE_Top10():
    #获得十大活跃成交股
    top_ten = pd.read_csv(config['STK_HKEXtoSSE_Top10'], encoding='utf-16', sep='\t',  parse_dates=['TradingDate'],
                          dtype={'Symbol': str}, usecols=['TradingDate', 'Symbol'])
    top_ten = top_ten.rename(columns={'Symbol': 'Stkcd'})
    top_ten['Trddt'] = top_ten['TradingDate'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    #top_ten = top_ten[(top_ten['Trddt'] >= '20141117') & (top_ten['Trddt'] <= '20151231')]
    top_ten = top_ten[(top_ten['Trddt'] >= '20141117')]
    top_ten['top_ten'] = 'high'
    top_ten = top_ten[['Stkcd', 'Trddt', 'top_ten']]
    return top_ten

def get_D_REC():
    """"
    取得应收账款净额'rec'
    """
    FS_Combas = pd.read_csv(config['FS_Combas'], encoding='utf-16', sep='\t',  parse_dates=['Accper'],
                            dtype={'Stkcd': str, 'Typrep': str}, usecols=['Stkcd', 'Accper', 'Typrep', 'A001111000'])
    FS_Combas = FS_Combas.rename(columns={'A001111000': 'rec'})
    FS_Combas['Trdyear'] = FS_Combas['Accper'].apply(lambda x: datetime.datetime.strftime(x, '%Y'))   #  提取年份
    FS_Combas = FS_Combas[FS_Combas['Typrep'] == 'A']
    FS_Combas = FS_Combas.sort_values(['Stkcd', 'Accper'], ascending=[1, 1]).reset_index(drop=True)
    FS_Combas = FS_Combas.groupby(['Stkcd', 'Trdyear'])['rec'].apply(lambda x: x.iloc[-1]).reset_index(drop=False)
    FS_Combas = FS_Combas[['Stkcd', 'Trdyear', 'rec']]
    FS_Combas["rec_lag"] = FS_Combas["rec"].shift(1)
    FS_Combas = FS_Combas.dropna()
    FS_Combas["D_REC"] = FS_Combas["rec"] - FS_Combas["rec_lag"]
    FS_Combas.to_csv(config['d_rec'], index=False, header=True)
    return FS_Combas


def get_depre():
    """
    折旧摊销
    :return:
    """
    depre = pd.read_csv(config['FI_T6'], encoding='utf-16', sep='\t',  parse_dates=['Accper'], dtype={'Stkcd': str, 'Typrep': str},
                         usecols=['Stkcd', 'Accper', 'Typrep', 'F061201B'])
    depre = depre.rename(columns={'F061201B': 'depre'})
    depre = depre[depre['Typrep'] == 'A']
    depre['Trdyear'] = depre['Accper'].apply(lambda x: datetime.datetime.strftime(x, '%Y'))
    depre = depre.sort_values(['Stkcd', 'Trdyear'], ascending=[1, 1]).reset_index(drop=True)
    depre = depre.groupby(['Stkcd', 'Trdyear'])['depre'].apply(lambda x: x.iloc[-1]).reset_index(drop=False)
    return depre

def calc_MNMAPR_Accruals():
    """
    取得计算dacc的数据
    :return:
    """
    MNMAPR_Accruals = pd.read_csv(config['MNMAPR_Accruals'], encoding='utf-16', sep='\t',  parse_dates=['Accper'], dtype={'Stkcd': str},
                                  usecols=['Stkcd', 'Accper', 'A100000', 'A110000', 'A110101', 'A130101', 'A210000', 'A210101', 'B110101', 'B130101', 'Ttlacrul'])
    MNMAPR_Accruals.columns = ['Stkcd', 'Accper', 'asset', 'tla', 'my', 'ppe', 'tll', 'sl', 'rev', 'op', 'ta_m']
    MNMAPR_Accruals['Trdyear'] = MNMAPR_Accruals['Accper'].apply(lambda x: datetime.datetime.strftime(x, '%Y'))
    depre = get_depre()
    depre = depre[['Stkcd', 'Trdyear', 'depre']]
    year_FAR_Finidx = get_year_FAR_Finidx()
    year_FAR_Finidx = year_FAR_Finidx[['Stkcd', 'Trdyear', 'cf', 'roe', 'cfo']]
    D_REC = get_D_REC()
    D_REC = D_REC[['Stkcd', 'Trdyear', "D_REC"]]
    MNMAPR_Accruals = pd.merge(MNMAPR_Accruals, depre, on=['Stkcd', 'Trdyear'], how='inner')
    MNMAPR_Accruals = pd.merge(MNMAPR_Accruals, year_FAR_Finidx, on=['Stkcd', 'Trdyear'], how='inner')
    MNMAPR_Accruals = pd.merge(MNMAPR_Accruals, D_REC, on=['Stkcd', 'Trdyear'], how='inner')
    MNMAPR_Accruals = MNMAPR_Accruals.dropna()
    MNMAPR_Accruals['asset_lag'] = MNMAPR_Accruals['asset'].shift(1)
    MNMAPR_Accruals['tla_lag'] = MNMAPR_Accruals['tla'].shift(1)
    MNMAPR_Accruals['my_lag'] = MNMAPR_Accruals['my'].shift(1)
    MNMAPR_Accruals['tll_lag'] = MNMAPR_Accruals['tll'].shift(1)
    MNMAPR_Accruals['sl_lag'] = MNMAPR_Accruals['sl'].shift(1)
    MNMAPR_Accruals['rev_lag'] = MNMAPR_Accruals['rev'].shift(1)
    MNMAPR_Accruals['d_tla'] = MNMAPR_Accruals['tla'] - MNMAPR_Accruals['tla_lag']
    MNMAPR_Accruals['d_my'] = MNMAPR_Accruals['my'] - MNMAPR_Accruals['my_lag']
    MNMAPR_Accruals['d_tll'] = MNMAPR_Accruals['tll'] - MNMAPR_Accruals['tll_lag']
    MNMAPR_Accruals['d_sl'] = MNMAPR_Accruals['sl'] - MNMAPR_Accruals['sl_lag']
    MNMAPR_Accruals['ta_r'] = (MNMAPR_Accruals['d_tla'] - MNMAPR_Accruals['d_my']) - \
                              (MNMAPR_Accruals['d_tll'] - MNMAPR_Accruals['d_sl']) - MNMAPR_Accruals['depre']
    MNMAPR_Accruals['d_rev'] = MNMAPR_Accruals['rev'] - MNMAPR_Accruals['rev_lag']
    MNMAPR_Accruals['D_REV'] = MNMAPR_Accruals['d_rev'] / MNMAPR_Accruals['asset_lag']
    MNMAPR_Accruals['ACC'] = (MNMAPR_Accruals['op'] - MNMAPR_Accruals['cf']) / MNMAPR_Accruals['asset_lag']
    #MNMAPR_Accruals = MNMAPR_Accruals[['Stkcd', 'Trdyear', 'asset_lag', "D_REC", 'D_REV', 'TA_M', 'TA_R', 'ACC', 'PPE', 'roe']].copy()
    MNMAPR_Accruals['ROE'] = MNMAPR_Accruals['roe']
    MNMAPR_Accruals['TA_M'] = MNMAPR_Accruals['ta_m'] / MNMAPR_Accruals['asset_lag']
    MNMAPR_Accruals['A'] = 1 / MNMAPR_Accruals['asset_lag']
    MNMAPR_Accruals['D_REV_REC'] = (MNMAPR_Accruals['d_rev'] - MNMAPR_Accruals['D_REC']) / MNMAPR_Accruals['asset_lag']
    MNMAPR_Accruals['PPE'] = MNMAPR_Accruals['ppe'] / MNMAPR_Accruals['asset_lag']
    MNMAPR_Accruals['TA_R'] = MNMAPR_Accruals['ta_r'] / MNMAPR_Accruals['asset_lag']
    MNMAPR_Accruals = MNMAPR_Accruals[['Stkcd', 'Trdyear', 'TA_M', 'A', 'D_REV', 'D_REV_REC', 'PPE', 'TA_R', 'ROE', 'ACC']].copy()
    MNMAPR_Accruals.to_csv(config['year_Accruals'], index=False, header=True)
    return MNMAPR_Accruals



def get_MNMAPR_Accruals():
    MNMAPR_Accruals = pd.read_csv(config['year_Accruals'], dtype={'Stkcd': str},  sep=',')
    return MNMAPR_Accruals


def get_STK_MKTLink_StockInfo():
    """
    A+H股是否同时发行
    用来剔除A+H股
    2014117以前
    :return:
    """
    STK_MKTLink_StockInfo = pd.read_csv(config['STK_MKTLink_StockInfo'], encoding='utf-16', sep='\t',  parse_dates=['FirstAbsorbedDate', 'RemovedDate'],
                                        dtype={'Stkcd': str, 'WhetherAandH': str}, usecols=['Symbol', 'WhetherAandH', 'FirstAbsorbedDate', 'RemovedDate'])
    STK_MKTLink_StockInfo = STK_MKTLink_StockInfo.rename(columns={'Symbol': 'Stkcd'})
    STK_MKTLink_StockInfo['FirstAbsorbedDate'] = STK_MKTLink_StockInfo['FirstAbsorbedDate'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    #STK_MKTLink_StockInfo['RemovedDate'] = STK_MKTLink_StockInfo['RemovedDate'].apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d'))
    #STK_MKTLink_StockInfo['RemovedDate'] = STK_MKTLink_StockInfo['RemovedDate'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    STK_MKTLink_StockInfo = STK_MKTLink_StockInfo[(STK_MKTLink_StockInfo['FirstAbsorbedDate'] <= '20151231') & (STK_MKTLink_StockInfo['WhetherAandH'] == 'Y')]
    return STK_MKTLink_StockInfo

def get_year_QFII():
    """
    机构持股分类表
    剔除QFII机构持股比的股票
    :return:
    """

    year_INI_HolderSystematics = pd.read_csv(config['year_INI_HolderSystematics'], encoding='utf-16', sep='\t',
                                             dtype={'Symbol': str}, parse_dates=['EndDate'],
                                             usecols=['Symbol', 'EndDate', 'QFIIHoldProportion'])
    year_INI_HolderSystematics = year_INI_HolderSystematics.fillna(0.0)
    year_INI_HolderSystematics = year_INI_HolderSystematics.rename(columns={"Symbol": "Stkcd"})
    year_INI_HolderSystematics['Trdyear'] = year_INI_HolderSystematics['EndDate'].apply(lambda x: datetime.datetime.strftime(x, "%Y"))  # 提取年份
    year_INI_HolderSystematics = year_INI_HolderSystematics.sort_values(['Stkcd', 'EndDate'],
                                                                        ascending=[1, 1]).reset_index(drop=True)
    year_INI_HolderSystematics = year_INI_HolderSystematics[year_INI_HolderSystematics['QFIIHoldProportion'] == 0.0]
    year_INI_HolderSystematics = year_INI_HolderSystematics[(year_INI_HolderSystematics['Trdyear'] >= '2012') & (year_INI_HolderSystematics['Trdyear'] <= '2015')]
    year_INI_HolderSystematics = year_INI_HolderSystematics.groupby(['Stkcd', 'Trdyear'])['QFIIHoldProportion'].apply(
        lambda x: x.iloc[-1]).reset_index(drop=False)
    year_QFII = year_INI_HolderSystematics[['Stkcd', 'Trdyear', 'QFIIHoldProportion']].copy()
    return year_QFII

def get_Liq_Tover_M():
    """"
    月换手率(ToverOsM-流通股,ToverTlM-总股数)
    计算年换手率
    """
    Liq_Tover_M = pd.read_csv(config['Liq_Tover_M'], encoding='utf-16', sep='\t', dtype={'Symbol': str}, parse_dates=['Trdmnt'],
                              usecols=['Stkcd', 'Trdmnt', 'ToverOsM', 'ToverTlM'])
    Liq_Tover_M['Trdyear'] = Liq_Tover_M['Trdmnt'].apply(lambda x: datetime.datetime.strftime(x, "%Y"))
    Liq_Tover_M['ToverOsM'] = Liq_Tover_M['ToverOsM'] / 100
    # year_AIV = month_aiv.groupby(['Stkcd', 'Trdyear'])['month_aiv_lead4'].apply(np.mean).reset_index(drop=False)
    year_turnover = Liq_Tover_M.groupby(['Stkcd', 'Trdyear'])['ToverOsM'].apply(np.mean).reset_index(drop=False)
    year_turnover.to_csv(config['turnover'], index=False, header=True)
    return year_turnover

def get_EN_EquityNatureAll():
    """
    股权性质（国企与非国企）
    :return:
    """
    EN_EquityNatureAll = pd.read_csv(config['EN_EquityNatureAll'], encoding='utf-16', sep='\t', dtype={'Symbol': str}, parse_dates=['EndDate'],
                                     usecols=['Symbol', 'EndDate', 'EquityNature', 'TopTenHoldersRate', 'EquityNatureID'])
    EN_EquityNatureAll = EN_EquityNatureAll.rename(columns={'Symbol': 'Stkcd'})
    EN_EquityNatureAll['Trdyear'] = EN_EquityNatureAll['EndDate'].apply(lambda x: datetime.datetime.strftime(x, "%Y"))
    EN_EquityNatureAll = EN_EquityNatureAll[EN_EquityNatureAll['Trdyear'] <= '2015']
    return EN_EquityNatureAll

def get_CG_Ybasic():
    """
    文件无法读取
    :return:
    """
    CG_Ybasic = pd.read_table(config['CG_Ybasic'], encoding='utf-16-le', sep='\t')
    # CG_Ybasic['Trdyear'] = CG_Ybasic['Reptdt'].apply(lambda x: datetime.datetime.strftime(x, "%Y"))
    # CG_Ybasic['year_indirector'] = CG_Ybasic['Y1101b'] / CG_Ybasic['Y1101a']
    # CG_Ybasic = CG_Ybasic[['Stkcd', 'Trdyear', 'year_indirector']].copy()
    return CG_Ybasic




if __name__ == "__main__":
    pass
    # print(get_STK_MKTLink_StockInfoChg().shape)
    # print(get_IAR_Rept().head(10))
    # print(get_day_ff5().head(10))
    # calc_day_trade_data()
    # print(get_day_trade_data().head(10))
    # print(get_year_return().head(10))
    # print(get_year_INI_HolderSystematics().head(100))
    # print(get_year_AF_CfeatureProfile().head(100))
    # print(get_year_SRFR_Finidx().head(10))
    # calc_month_composite_data()
    # print(get_month_composite_data().head(10))
    # print(calc_day_return().head(10))
    # print(get_day_return().describe())
    # print(get_day_return().head(10))
    # year_data = get_year_INI_HolderSystematics()
    # print(get_day_return())
    # print(get_year_FAR_Finidx())
    #print(get_STK_HKEXtoSSE_Top10())
    #print(get_D_REC())
    # print(get_depre())
    #print(calc_MNMAPR_Accruals())
    #print(get_MNMAPR_Accruals())
    #print(get_STK_MKTLink_StockInfo())
    #print(get_year_QFII())
    #print(get_Liq_Tover_M())
    #print(get_Tover())
    #print(get_EN_EquityNatureAll())
    #print(get_CG_Ybasic())
    #print(get_industry_type())
    #print(calc_day_trade_data())
    #print(calc_day_return())
    #print(get_day_trade_data())
