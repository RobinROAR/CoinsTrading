#!/usr/bin/env python3
# -*- coding:utf-8 -*-

###############################################################################
# Class market aims to find proper trade pairs

# Author : Robin   <zrb915@live.com> CHINA.
###############################################################################
# changes @ 20180501


#引入包
from bitshares import BitShares
from pprint import pprint

from bitshares.market import Market



from io import BytesIO
import pycurl

class Market(object):
    def __init__(self,url = 'https://api.crypto-bridge.org/api/v1/ticker'):
        self.url=url
    def get_ticker(self):
        '''
        根据url返回market list
        :return:
        '''
        #PycURL没有对网络的响应提供存贮机制。因此，我们必须提供一个缓存（以StringIO的形式）并且让PycURL将内容写入这个缓存。
        buffer = BytesIO()
        #创建一个pucurl.Curl的实例
        c = pycurl.Curl()
        #使用  setopt  来设置请求选项
        c.setopt(pycurl.WRITEDATA, buffer)
        c.setopt(pycurl.URL, 'https://api.crypto-bridge.org/api/v1/ticker')
        #执行请求
        c.perform()
        c.close()
        body = buffer.getvalue()
        return body.decode('utf-8')


    def write2file(self,content):
        with open('tickers', 'w') as f:
            f.write(content)



###########################################################################################################################################################
import json
import pickle

# #使用json解析ticker
# with open('./tickers','r') as f:
#     tmp = f.readline(
rbz = Market()
tmp = rbz.get_ticker()


#begin
markets = json.loads(tmp)
mlist = []
for _ in markets:
    market = (_['id'])

    #区分 quote 和 base
    quote,base = market.split('_')[0],market.split('_')[1]
    mlist.append([quote,base])
#print(mlist)


def get_pairs(sons):
    pairs = []
    for i in range(len(sons)):
        for j in range(i+1,len(sons)):
            if [sons[i],sons[j]] in mlist:
                pairs.append([sons[i],sons[j]])
            elif [sons[j],sons[i]] in mlist:
                pairs.append([sons[j],sons[i]])
            else:
                continue
    return pairs


def get_sons(start):
    sons = []
    for _ in mlist:
        if _[1] == start:
            sons.append(_[0])
    return sons


#第一循环
#找到都能根starter交易的交易对
p1 = get_pairs(get_sons('BTC'))
#去掉btc后的list
p1list = []
for i in mlist:
    if 'BTC' in i:
        continue
    else:
        p1list.append(i)
#第二循环
p2 = []
for i in p1:
    for j in p1list:
        #找到两个货币之间的bridge
        if i[0] in j:
            if i[0] == j[0]:
                temp = j[1]
            else:
                temp = j[0]
            if ([temp,i[1]] in p1list):
                p2.append([i[0],temp,i[1]])

            elif [i[1],temp] in p1list:
                p2.append([i[0],temp,i[1]])
            else:
                continue
#第三循环
p3 = []
#i代表外层[a,b]: btc-a   b-btc
for i in p1:
    #j连接a[a.b]的交易对: 把p1中每一个都放进来，a-j[0]  j[1]-b 分别在p1list中即可。t同时，j[0],j[1]在表里
    for j in p1list:
        if ([i[0],j[0]] in p1list) and ( [j[1],i[1]] in p1list ):
            p3.append([i[0],j[0],j[1],i[1]])
        #elif ([i[0],j[1]] in p1list) and ( [j[0],i[1]] in p1list ):
         #   p3.append([i[0], j[0], j[1], i[1]])
        else:
            continue


def cal_price(num, coin1, coin2, d=0.002):
    '''
    根据汇率计算货币.计算两个价格 【最近成交价，最快成交价】
    :param num:  输入[1,1]
    :param coin1:
    :param coin2:
    :return:  【price1,price2】
    '''
    result = [-1, -1]
    if coin1 == coin2:
        result = [1, 1]
    else:

        for _ in markets:
            e = 0.00000000000001
            m = (_['id'])
            base, quote = m.split('_')[1], m.split('_')[0]
            # print(base,quote)
            ratio_last = float(_['last'])
            ratio_bid = float(_['bid'])
            ratio_ask = float(_['ask'])

            if ratio_bid < e or ratio_ask < e:
                # 处理00值
                continue
            # 当coin2为quote，需要买，对应lowask
            elif (coin1 == base) and (coin2 == quote):
                result[0] = num[0] * ratio_last * (1 - d)
                result[1] = num[1] * ratio_ask * (1 - d)
            # 当coin1为quote，需要卖，对应highbid
            elif (coin2 == base) and (coin1 == quote):
                result[0] = num[0] / ratio_last * (1 - d)
                result[1] = num[1] / ratio_bid * (1 - d)
            else:
                continue
    if result[0] == -1:
        print('no match')
        return ([0, 0, 0])
    else:
        return result
#p1寻找最优派对
p1_price = []
for i in p1:
    coin1 = 'BTC'
    coin2 = i[0]
    coin3 = i[1]

    t0 = cal_price([1,1],coin1,coin2)
    t1 = cal_price(t0,coin2,coin3)
    t2 = cal_price(t1,coin3,coin1)
    tep = {'bridge':[coin2,coin3],'price':[t2[0],t2[1]]}
    p1_price.append(tep)
    tep = None


def test_single_pairs():
    coin1 = 'BTC'
    coin2 = 'RVN'
    coin3 = 'LTC'

    t0 = cal_price([1,1],coin1,coin2)
    t1 = cal_price(t0,coin2,coin3)
    t2 = cal_price(t1,coin3,coin1)

    t00 = cal_price([1,1],coin1,coin3)
    t11 = cal_price(t00,coin3,coin2)
    t22 = cal_price(t11,coin2,coin1)

    print({'bridge':[coin2,coin3],'price':[t2[0],t2[1]]})
    print({'bridge':[coin3,coin2],'price':[t22[0],t22[1]]})





# for i in p2:
#     coin1 = 'BTC'
#     coin2 = i[0]
#     coin3 = i[1]
#     coin4 = i[2]
#
#     t0 = cal_price(1,coin1,coin2)
#     t1 = cal_price(t0,coin2,coin3)
#     t2 = cal_price(t1,coin3,coin4)
#     t3 = cal_price(t1, coin4, coin1)
#     print(1,coin1,coin2,coin3,coin4,coin1,t3)

def return_volume_list(markets,basecoin):
    #根据交易量排序，指针对给定basecoin
    temp = []
    for _ in markets:
        m = (_['id'])
        base, quote = m.split('_')[1], m.split('_')[0]
        if base == basecoin:
            temp.append(_)
        else:
            continue
    tep = sorted(temp, key = lambda d:float(d['volume']),reverse=True)
    result = []
    for _ in tep:
        m = _['id']
        base, quote = m.split('_')[1], m.split('_')[0]
        #print(quote,base)
        result.append(quote)

    return result

#print(return_volume_list(markets,'BTC'))

def sort_result(l,low,volume):
    '''
    对输出的结果列表进行排序
    :param l: l:[ {bridge:[BCO,Smart],price:[t1,t2,t3]},   ]
    :param profit: float: the low bound of profit
    :param volume: a volume list [RVN, PGN, ...]
    :return:
    '''
    tmp = []
    for _ in l:
        if _['price'][0]>low and _['price'][1]>low:
            tmp.append(_)
        else:
            continue
    v = list(reversed(volume))
    for _ in tmp:
        index = [v.index(_['bridge'][0]),v.index(_['bridge'][1])]
        _['index'] = index
    tmp = sorted(tmp,key = lambda d:(d['index'][0],d['index'][1]),reverse = True)
    return tmp

print(sort_result(p1_price,1,return_volume_list(markets,'BTC')))



def list_num(mlist):
    base_list = [i[1] for i in mlist ]

    result = {}
    bset = set(base_list)
    for item in bset:
        result[item] = base_list.count(item)
    print(result)



