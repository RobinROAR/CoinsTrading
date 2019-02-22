#!/usr/bin/env python3
# -*- coding:utf-8 -*-

###############################################################################
# 主函数

# Author : Robin   <zrb915@live.com> CHINA.
###############################################################################
# changes @ 201801001


#引入包
import json
from bitshares import BitShares
from bitshares.market import Market
import pprint as pp

##通用变量
bitBeijing = BitShares(node="wss://api.bts.ai")


def buy_Coin1_from_NCoin2(coin1,coin2,amount,n, lim=10 ):

    #例子：USD:BTS， 将100 BTS 转换成 XX USD, 根据最靠前的limit个offer计算xx的区间。
    #find the specific market
    mk = Market("{}:{}".format(coin1,coin2), bitshares_instance=bitBeijing)
    #get the order book
    od= mk.orderbook(limit=lim)
    asks = od['asks']
    #返回每个卖单的具体信息， list[ [base_amount, price],]
    def get_details(od_list):
        details = []
        for _ in od_list['asks']:
            #print(_)
            base = _['base'].amount
            price = _['price']
            details.append([base, price])
        return details
    dt = get_details(od)

    if len(dt) == 0:
        print("no orderbook")
        return 0,0
    else:
        #计算卖出ncoin2得到的价格
        best = 0.0
        worst = 0.0
        cur = 0
        sum = dt[cur][0]

        if amount*n <= sum:
            #当前order的price
            if cur < len(dt) - 1:
                best = dt[cur][1]
                worst = dt[cur + 1][1]
            else:
                best = dt[cur][1]
                worst = dt[cur][1]
        #若是订单满足不了需求
        else:
            while amount*n > sum and cur<len(dt)-1:
                cur+=1
                sum += dt[cur][0]
            if cur<len(dt)-1:
                best = dt[cur][1]
                worst = dt[cur+1][1]
            else:
                best = dt[cur][1]
                worst = dt[cur][1]

        return amount/best, amount/worst


######################################################################
def cal_bridge(base, bridge,amount, n, limit):
    '''

    :param base: 'BTS'
    :param b:  ['CNY','USD']
    :return:  result, rresult
    '''
    def cal(b):
        t = 0
        w = 0
        for i in range(0,len(b)):
            if i ==0:
                t,w = buy_Coin1_from_NCoin2(b[i],base,amount, n, limit)
            else :
                t,w_n = buy_Coin1_from_NCoin2(b[i],b[i-1],t, n, limit)
                t_n, w = buy_Coin1_from_NCoin2(b[i],b[i-1],w, n, limit)
        t, w_n = buy_Coin1_from_NCoin2(base, b[i],t, n, limit)
        t_n, w = buy_Coin1_from_NCoin2(base, b[i], w, n, limit)

        res = [t,w]
        return res

    res1 = cal(bridge)
    bridge.reverse()
    res2 = cal(bridge)

    return bridge,res1, res2



# assets = ['OPEN.BTC','OPEN.ETH','USD','CNY','EUR','BRIDGE.BTC','GDEX.BTC','GDEX.ETH']
#
# for i in range(len(assets)):
#     for j in range(i+1,len(assets)):
#         b = [assets[i],assets[j]]
#         print(cal_bridge('BTS', b))


print(cal_bridge('BTS', ['USD','EUR','CNY'],100, 2, 10))


# bitBeijing = BitShares(node="wss://api.bts.ai")
# market = Market("USD:BTS",bitshares_instance=bitBeijing)
#
# pp.pprint(market.ticker())
#
# pp.pprint(market.orderbook(limit=5))
