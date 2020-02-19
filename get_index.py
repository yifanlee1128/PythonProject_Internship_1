# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals, division
import numpy as np
import pandas as pd
from gm.api import *
import datetime
# 需要先set_token
"""
该函数用于获取各种商品期货的指数数据，使用前须set_token，函数的四个参数均为可选字段，key_word空缺时默认获取所有商品
的期货指数，其列表见下方，freq空缺时默认获取的是日频数据，支持的数据频度见下方，begin_time空缺时默认的起始时间点为
对应商品可获得的最早期货品种的上市日期，end_time空缺时默认的截止时间点为使用当天的一天前
"""

"""支持的键入参数类型"""
"""
key_word:可以为一个字符串，也可以为元素为字符串的一个列表，其字符串可以是商品关键字、商品英文标识或
带有交易所简称的英文标识：如：铜、CU或SHFE.CU（不区分大小写），列表元素同理
begin_time/end_time:同history函数，支持字符串及datetime.datetime类型的时间格式
"""

"""函数一些自带的处理方式"""
"""
关于关键词：关键词仅限下面列表内所含的品种类别，输入对应相同商品的关键词时，函数会自动去重
关于时间：终止时间超出当前时间点,或距离当前时间点过近的情形下，终止时间将自动调为前一天的当前时刻
"""

"""支持的商品品种"""
"""
玉米, 玉米淀粉, 白糖, 鸡蛋, 动力煤, 沥青, 热轧卷板, 豆一, 棉一, 线型, 聚氯乙烯, 铜, 铝, 锌, 铅, 镍, 螺纹钢,
玻璃, 橡胶, PTA, 甲醇, 聚丙烯, 焦煤, 焦炭, 铁矿石, 豆粕, 菜粕, 豆油, 棕榈油, 菜籽油, 硅铁, 锰硅, 黄金, 白银
"""

"""支持的数据频度"""
"""
1d, 3600s, 1800s, 900s, 300s, 60s
"""
"""其他提示"""
"""
由于玉米关键词会调出玉米与玉米期货的数据，所以处理方法为：只要出现两者其一相关的关键词，统一处理为'玉米'，
即先将两者的指数全部计算出，再在最后根据输入的内容将不需要的指数剔除，剔除由函数内的指示变量logic与logic2实现

若出现data['sec_abbr']有关的错误，有可能是从服务器获取数据时出现问题，可尝试重新操作
"""


def get_index_data(key_word=None, freq=None, begin_time=None, end_time=None):
    index_total = pd.DataFrame()
    use_begin_time = ''
    use_end_time = ''

    """处理频度参数"""
    freq_list = ['1d', '3600s', '1800s', '900s', '300s', '60s']
    if freq is None:
        freq = '1d'
    elif freq not in freq_list:
        raise TypeError('You input an invalid frequency!')
    else:
        pass

    """处理时间格式"""
    if begin_time is None:
        pass
    else:
        dt_begin_time = ''
        if isinstance(begin_time, str):
            try:
                if ":" in begin_time:
                    dt_begin_time = datetime.datetime.strptime(begin_time, "%Y-%m-%d %H:%M:%S")
                else:
                    dt_begin_time = datetime.datetime.strptime(begin_time, "%Y-%m-%d")
            except:
                TypeError("the time format of begin_time is invalid!")
        elif isinstance(begin_time, datetime.datetime):
            dt_begin_time = begin_time
        use_begin_time = datetime.datetime.strftime(dt_begin_time, "%Y-%m-%d %H:%M:%S")  # 最终统一为str格式
    if end_time is None:
        pass
    else:
        dt_end_time = ''
        if isinstance(end_time, str):
            try:
                if ":" in end_time:
                    dt_end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                else:
                    dt_end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d")
            except:
                raise TypeError("the time format of end_time is invalid!")
        elif isinstance(end_time, datetime.datetime):
            dt_end_time = end_time
        """处理截止时间超出当前时间点,或距离当前时间点过近的情形"""
        if ((datetime.datetime.now()-dt_end_time).seconds < 1800) and dt_end_time <= datetime.datetime.now(): ###
            dt_end_time = dt_end_time - datetime.timedelta(minutes=30)
            print("Considering the precision of the index ,the end time has been adjusted to ",
                  dt_end_time, '\n')
        if dt_end_time > datetime.datetime.now():
            dt_end_time = datetime.datetime.now()-datetime.timedelta(minutes=30)
            print('The end time you input is a future time ,it has been adjusted to', dt_end_time)
        use_end_time = datetime.datetime.strftime(dt_end_time, "%Y-%m-%d %H:%M:%S")

    """处理关键词格式"""
    name_list1 = ['玉米', '白糖', '鸡蛋', '动力煤', '沥青', '热轧卷板', '豆一', '棉一', '线型', '聚氯乙烯', '铜', '铝',
                  '锌', '铅', '镍', '螺纹钢', '玻璃', '橡胶', 'PTA', '甲醇', '聚丙烯', '焦煤', '焦炭', '铁矿石', '豆粕',
                  '菜粕', '豆油', '棕榈油', '菜籽油', '硅铁', '锰硅', '黄金', '白银']
    name_list2 = ['C', 'SR', 'JD', 'TC', 'BU', 'HC', 'A', 'CF', 'L', 'V', 'CU', 'AL',
                  'ZN', 'PB', 'NI', 'RB', 'FG', 'RU', 'TA', 'MA', 'PP', 'JM', 'J', 'I', 'M',
                  'RM', 'Y', 'P', 'OI', 'SF', 'SM', 'AU', 'AG']
    name_list3 = ['DCE.C', 'CZCE.SR', 'DCE.JD', 'CZCE.TC', 'SHFE.BU', 'SHFE.HC', 'DCE.A', 'CZCE.CF',
                  'DCE.L', 'DCE.V', 'SHFE.CU', 'SHFE.AL', 'SHFE.ZN', 'SHFE.PB', 'SHFE.NI', 'SHFE.RB', 'CZCE.FG',
                  'SHFE.RU', 'CZCE.TA', 'CZCE.MA', 'DCE.PP', 'DCE.JM', 'DCE.J', 'DCE.I', 'DCE.M', 'CZCE.RM',
                  'DCE.Y', 'DCE.P', 'CZCE.OI', 'CZCE.SF', 'CZCE.SM', 'SHFE.AU', 'SHFE.AG']
    name_list = []               # 用于获取数据的关键词列表
    logic = 0                    # 关于玉米与玉米淀粉指数的指示变量，用途见函数主体前的其他提示
    if key_word is None:
        name_list = name_list1
    elif isinstance(key_word, str):
        if key_word.upper() in name_list1+name_list2+name_list3:
            if key_word.upper() in name_list1:
                name_list = [key_word]
            elif key_word.upper() in name_list2:
                adr = name_list2.index(key_word.upper())
                name_list = [name_list1[adr]]               # 统一转换为中文关键词
            elif key_word.upper() in name_list3:
                adr = name_list3.index(key_word.upper())
                name_list = [name_list1[adr]]               # 统一转换为中文关键词
        elif key_word.upper() in ['玉米淀粉', '淀粉', 'CS', 'DCE.CS']:
            name_list = ['玉米']
        else:
            raise TypeError("You input an invalid key_word!")
    elif isinstance(key_word, list):
        for key_word1 in key_word:
            if isinstance(key_word1, str):
                if key_word1.upper() in name_list1+name_list2+name_list3:
                    if key_word1.upper() in name_list1:
                        name_list.insert(len(name_list), key_word1)
                    elif key_word1.upper() in name_list2:
                        adr = name_list2.index(key_word1.upper())
                        name_list.insert(len(name_list), name_list1[adr])
                    elif key_word1.upper() in name_list3:
                        adr = name_list3.index(key_word1.upper())
                        name_list.insert(len(name_list), name_list1[adr])
                elif key_word1.upper() in ['玉米淀粉', '淀粉', 'CS', 'DCE.CS']:
                    name_list.insert(len(name_list), '玉米')
                    logic = 1
                else:
                    raise TypeError("You input a list including an invalid key_word!")
            else:
                raise TypeError("You input a list including an invalid key_word!")
        name_list = list(set(name_list))
    else:
        raise TypeError("You input an invalid key_word!")

    """数据获取及指数计算"""
    for name in name_list:
        data = get_instruments(names=name, sec_types=[4], df=True)
        temp_list = np.unique(data['sec_abbr'])
        for temp_name in temp_list:
            data1 = data[data['sec_abbr'] == temp_name]
            id_for_concat = data1['sec_id'].values[0]
            if id_for_concat[1] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                key = id_for_concat[0].upper()
            else:
                key = id_for_concat[0:2].upper()
            if name == name_list[0] and temp_name == temp_list[0]:
                name_for_concat = []
            name_for_concat.insert(len(name_for_concat), key)
            print('Status:', name_for_concat)
            id_list = data1['symbol'].values

            """获取仅包含仓位和每日收盘价的原始表"""
            raw = pd.DataFrame(columns=['eob'])
            for name_id in id_list:
                """时间段分割"""
                temp_data = data[data['symbol'] == name_id]
                if begin_time is None:
                    dt_begin_time = temp_data['listed_date'].values
                    dt_begin_time = dt_begin_time.tolist()[0]
                    use_begin_time = datetime.datetime.strftime(dt_begin_time, '%Y-%m-%d')
                if end_time is None:
                    dt_end_time = temp_data['delisted_date'].values
                    dt_end_time = dt_end_time.tolist()[0]
                    use_end_time = datetime.datetime.strftime(dt_end_time, '%Y-%m-%d')
                time_array = pd.date_range(start=use_begin_time, end=use_end_time, freq='60D', closed=None)
                time_array = [datetime.datetime.strftime(x, '%Y-%m-%d') for x in list(time_array)]
                time_array = [' '.join([x, '05:00:00']) for x in list(time_array)]
                if len(time_array)>0:
                    del time_array[0]
                time_array.insert(0, use_begin_time)
                time_array.insert(len(time_array), use_end_time)
                """对不同时间段的数据进行拼接"""
                data3 = pd.DataFrame(columns=['eob'])
                for k in range(0, len(time_array) - 1):
                    data2 = history(symbol=name_id, frequency=freq, start_time=time_array[k],
                                    end_time=time_array[k + 1],
                                    fields='close,position,eob', fill_missing='NaN', df=True)
                    if data2.empty:
                        continue
                    else:
                        if freq not in ['1d', '60s']:
                            data2.drop(["symbol", "bob", "frequency"], axis=1, inplace=True)
                        elif freq in ['1d', '60s']:
                            data2.drop(["symbol"], axis=1, inplace=True)
                        data2 = pd.DataFrame(data2)
                        if data2.shape[1] == 3:
                            data3 = pd.concat([data3, data2], axis=0, join='outer')
                        else:
                            continue
                if data3.empty:
                    continue
                else:
                    data3 = pd.DataFrame(data3)
                    if data3.shape[1] == 3:
                        raw = pd.merge(raw, data3, how='outer', on='eob', sort=True, suffixes=('_x', '_y'))
                    else:
                        continue
            if "position" in raw.columns:
                raw.dropna(axis=0, how='all', subset=['position_x', 'position_y', 'position'], inplace=True)
            else:
                raw.dropna(axis=0, how='all', subset=['position_x', 'position_y'], inplace=True)

            """计算每日内,各品种的相对持仓量（百分比）"""
            if "position" in raw.columns:
                position = pd.concat([raw["position_x"], raw["position_y"], raw["position"]], axis=1)
            else:
                position = pd.concat([raw["position_x"], raw["position_y"]], axis=1)
            position = np.float32(position)
            t_position = np.nansum(position, axis=1)
            for p in range(0, position.shape[1]):
                position[:, p] = position[:, p] / t_position
            del t_position
            r_position = pd.DataFrame(position)

            """计算指数"""
            if "close" in raw.columns:
                close = pd.concat([raw["close_x"], raw["close_y"], raw["close"]], axis=1)
            else:
                close = pd.concat([raw["close_x"], raw["close_y"]], axis=1)
            temp = np.zeros(close.shape)
            close = np.float32(close)
            r_position = np.float32(r_position)
            for p in range(0, close.shape[1]):
                temp[:, p] = (np.multiply(close[:, p], r_position[:, p]))
            temp = np.nansum(temp, axis=1)
            index = pd.DataFrame(np.array(temp))

            """拼接时间"""
            del temp
            time = pd.DataFrame(raw["eob"].values)
            index = pd.concat([time, index], axis=1)
            index.columns = ['time', key]
            index = index.set_index('time')

            """将数据拼接到总表"""
            del raw
            if name == name_list[0] and temp_name == temp_list[0]:
                index_total = index
            else:
                index_total = pd.concat([index_total, index], axis=1, join='outer', keys='time', ignore_index=True)

    index_total.columns = name_for_concat

    # 通过指示变量剔除玉米相关指数中所不需要的指数
    if isinstance(key_word, str):
        if key_word in ['玉米淀粉', '淀粉', 'CS', 'DCE.CS']:
            del index_total["C"]
        elif key_word in ['玉米', 'C', 'DCE.C']:
            del index_total["CS"]
    elif isinstance(key_word, list):
        logic2 = 0
        for temp_key in key_word:
            if temp_key in ['玉米', 'C', 'DCE.C']:
                logic2 = 1
                break
        if logic == 1 and logic2 == 1:
            pass
        elif logic == 1 and logic2 == 0:
            del index_total["C"]
        elif logic == 0 and logic2 == 1:
            del index_total["CS"]
    index_total = index_total.sort_index(axis=1)
    index_total = pd.DataFrame(index_total)
    index_total = index_total.fillna(method='ffill')
    index_total = index_total.round(2)
    print(index_total)

    """若结果存在1小时内的数据，为保证数据准确性，将该部分剔除"""
    for k in range(len(index_total) - 1, -1, -1):
        print(index_total.index[k] <= (datetime.datetime.now()-datetime.timedelta(minutes=30)))
        if index_total.index[k] <= (datetime.datetime.now()-datetime.timedelta(minutes=30)):
            index_total = index_total[0:k+1]
            break
    return index_total
