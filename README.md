## ABSTRACT
- 设计并实现了一个在Bitshares内场交易cryptocurrencies的策略
- 通过便利所有循环的交易对，发现特殊的可盈利交易对进行套利。



## DETAILS
### order histroy 分析
- 每发起一笔交易，histroy order会新增一个dict，随着交易状态改变，该dict内容也会改变。
- 状态体现在result中
```
正在进行中
{'block_num': 26793221, 'trx_in_block': 10, 'op': [1, {'fee': {'asset_id': '1.3.0', 'amount': 578}, 'expiration': '2018-05-08T08:01:46', 'fill_or_kill': False, 'min_to_receive': {'asset_id': '1.3.3422', 'amount': 147969}, 'seller': '1.2.797044', 'extensions': [], 'amount_to_sell': {'asset_id': '1.3.3751', 'amount': 2000000}}], 'op_in_trx': 0, 'virtual_op': 11277, 'id': '1.11.189254669', 'result': [1, '1.7.70188996']}
取消后
{'trx_in_block': 16, 'id': '1.11.189254800', 'block_num': 26793227, 'virtual_op': 11553, 'op': [2, {'extensions': [], 'order': '1.7.70188996', 'fee': {'amount': 57, 'asset_id': '1.3.0'}, 'fee_paying_account': '1.2.797044'}], 'op_in_trx': 1, 'result': [2, {'amount': 2000000, 'asset_id': '1.3.3751'}]}
成交后
{'op_in_trx': 0, 'trx_in_block': 4, 'id': '1.11.189258394', 'op': [4, {'account_id': '1.2.797044', 'receives': {'amount': 73799, 'asset_id': '1.3.3422'}, 'fee': {'amount': 147, 'asset_id': '1.3.3422'}, 'fill_price': {'base': {'amount': 23671941, 'asset_id': '1.3.3422'}, 'quote': {'amount': 641516038, 'asset_id': '1.3.3751'}}, 'is_maker': False, 'order_id': '1.7.70190390', 'pays': {'amount': 2000000, 'asset_id': '1.3.3751'}}], 'virtual_op': 19146, 'result': [0, {}], 'block_num': 26793335}
```
### 每个交易对的 ticker() 分析
- 对于一个market[rvn,btc],rvn是quote，btc是base
- 假设返回0.00053, 返回的单位是 1 q = b， 即 1 rvn = 0.00053 btc
- lowask 卖rvn的人最低要求 > high bid 买rvn的人最高出价

### 分析一个具体ticker以及orderbook： BTS：USD
```
{'baseSettlement_price': 0.040853382 USD/BTS,
 'baseVolume': 4,533.7492 USD,
 'core_exchange_rate': 0.051137922 USD/BTS,
 'highestBid': 0.050410509 USD/BTS,
 'latest': 0.050410509 USD/BTS,
 'lowestAsk': 0.050999201 USD/BTS,
 'percentChange': -0.76,
 'quoteVolume': 89,680.95165 BTS}
```
 
- 对于一个market[USD, BTS],BTS是BASE，USD是QUOTE
- lowask > highbid ; 卖方>买方
- 如果我们买USD，应该看lowask， 用USD买BTS， 看highbid 
 
```
{'asks': [880.00000 BTS for 44.8793 USD @ 0.050999205 USD/BTS,
          13,254.92554 BTS for 676.0012 USD @ 0.051000000 USD/BTS,
          199.00486 BTS for 10.1867 USD @ 0.051188197 USD/BTS,
          3,048.83398 BTS for 156.0660 USD @ 0.051188750 USD/BTS,
          10,000.00000 BTS for 511.9971 USD @ 0.051199710 USD/BTS],
 'bids': [295.06938 BTS for 14.8746 USD @ 0.050410517 USD/BTS,
          584.92966 BTS for 29.4866 USD @ 0.050410506 USD/BTS,
          405.74086 BTS for 20.4536 USD @ 0.050410501 USD/BTS,
          36,623.59250 BTS for 1,846.0122 USD @ 0.050405001 USD/BTS,
          107,906.66882 BTS for 5,439.0357 USD @ 0.050405001 USD/BTS]}
```

### 确保交易完成的策略
- 交易数额：
    - 需求为实际交易值的n倍
    - 如果<挂单数额，按当前价格挂单，直接挂单
    - 如果>挂单数额，按最差的挂单
    
### 交易条件： 监控市场活跃性
- basevolume
- 24 change percentage