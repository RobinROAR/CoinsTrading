#!/usr/bin/env python3
# -*- coding:utf-8 -*-

###############################################################################
# 主函数

# Author : Robin   <zrb915@live.com> CHINA.
###############################################################################
# changes @ 20180501


#引入包
from bitshares import BitShares
from pprint import pprint
from bitshares.market import Market


# market = Market('BRIDGE.BTC:BRIDGE.RVN')
# print(market.ticker())
from bitshares import BitShares
from bitshares.account import Account
from bitshares.market import Market
bitshares = BitShares(node="wss://bitshares.dacplay.org:8089/ws")
import time



class MyAccount(object):
    def __init__(self,name = "owari21st"):
        self.name = name
        self.account = Account("owari21st")
    @property
    def pdetails(self):
        print('Account ID:{}'.format(self.account))
        print('Current Balances:')
        print(self.account.balances)
        print('Open orders:')
        print(self.account.openorders)
    @property
    def phistroy(self):
        for h in self.account.history():
            print(h)


def cancell_openorder(market, ac,we,orderid):
    for i in range(5):
        sig = list(ac.account.history())[0]['result'][0]
        if sig == 0:
            break
        else:
            #time.sleep(1)
            print('Still waiting deal...')
            lowask, highbid =  float(market.ticker()['lowestAsk']), float(market.ticker()['highestBid'])
            print('current price:', [lowask, highbid],we)
            #通过关键字，查询order情况
            #status,order_id = list(ac.account.history())[0]['result'][0],list(ac.account.history())[0]['result'][1]
            #print(status,order_id)
            continue
    if list(ac.account.history())[0]['result'][0] == 0:
        print('$$ Order filled.')
        return 0
    else:
        print(list(ac.account.history())[0]['result'][0])
        # 将历史记录转换为list，并从最近一条,定位出order id
        #order_id = list(ac.account.history())[0]['result'][1]
        market.cancel(orderid, account='owari21st')
        print('$$ Order cancelled:',orderid)
        return 1


ac = MyAccount()
ac.pdetails







def trade(bos,q,b,num,e=0.000):
    market = Market("BRIDGE.{0}:BRIDGE.{1}".format(q,b))
    latest, lowask, highbid = float(market.ticker()['latest']), float(market.ticker()['lowestAsk']), float(
        market.ticker()['highestBid'])
    # 此处需要从账户中解锁钱包，与文档事例不符。
    ac.account.bitshares.wallet.unlock("a******6")
    if bos == 'b':
        print('***********')
        er=e
        we_use = lowask*(1+er)
        print(we_use)
        print('$$ Order submited:')
        tx = market.buy(we_use,num,account='owari21st',returnOrderId=1)# sell 100 USD for 300 BTS/USD expiration='20'
        orderid = tx["orderid"]
        print('***********')
        c = cancell_openorder(market,ac,we_use,orderid)
        return c
    elif bos == 's':
        print('***********')
        er = e
        we_use = highbid * (1 - er)
        print('$$ Order submited:')
        tx = market.sell(we_use, num, account='owari21st',returnOrderId=1)
        orderid = tx["orderid"]
        print('***********')
        c = cancell_openorder(market, ac,we_use,orderid)
        return c
    else:
        print('buy or sell? ')
        return -1


def bridge(coin1,coin2,btc = 0.0001):
    #第一步：卖固定金额BTC，求最快成交时，地影多少coin1
    ticker = Market("BRIDGE.{0}:BRIDGE.BTC".format(coin1)).ticker()
    lowask =  float(ticker['lowestAsk'])

    init  = btc/lowask
    #print(init)

    s1 = trade('b', coin1,'BTC', init)
    if s1== 0:
        print('1 win')
        #第二步，把所有coin1都卖掉换成coin2
        while float(ac.account.balance('BRIDGE.{}'.format(coin1))) != float(0.0):
            s2 = trade('s', coin1, coin2, float(ac.account.balance('BRIDGE.{}'.format(coin1))))
        if  s2==0:
            print('2 win')
            #第三部，把所用coin2都卖掉，换成btc
            while float(ac.account.balance('BRIDGE.{}'.format(coin2))) != float(0.0):
                s3 = trade('s', coin2, 'BTC', float(ac.account.balance('BRIDGE.{}'.format(coin2))))
            if s3==0:
                 print('3 win')
            else:
                 print('3 fail')
        else:
            print('2 fail')
    else:
        print('1 fail')


#bridge('RVN', 'LTC')

trade('s', 'LTC','BTC', float(ac.account.balance('BRIDGE.{}'.format('LTC'))))
#trade('b','LTC','BTC',0.0001,e=0.000)
#s2 = trade('s', 'LTC', 'MONA', ac.account.balance('BRIDGE.{}'.format('LTC')))

#s3 = trade('s', 'MONA', 'BTC', ac.account.balance('BRIDGE.{}'.format('MONA')) )

#将历史记录转换为list，并从最近一条,定位出order id
# order_id = list(ac.account.history())[0]['result'][1]
# market.cancel(order_id,account='owari21st')

# while(len(ac.account.openorders)!=0):
#     ac.pdetails

#ac.phistroy









