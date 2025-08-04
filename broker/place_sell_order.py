from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=1)

# 构建 TQQQ 合约
contract = Stock('TQQQ', 'SMART', 'USD')

# 下单：市价卖出 1 股
order = MarketOrder('SELL', 1)

# 提交订单
trade = ib.placeOrder(contract, order)

# 等待成交
ib.sleep(2)
print("OrderStatus：", trade.orderStatus.status)
print("TradeFills：", trade.fills)

ib.disconnect()
