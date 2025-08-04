from ib_insync import *

# 启动 IB 接口
ib = IB()
ib.connect('127.0.0.1', 4002, clientId=1)  # 4001 是 paper account 默认端口

# 定义合约（TQQQ）
contract = Stock('TQQQ', 'SMART', 'USD')
ib.qualifyContracts(contract)

# 创建订单（买入 1 股）
order = MarketOrder('BUY', 1)

# 下单
trade = ib.placeOrder(contract, order)

# 等待订单被确认或成交
ib.sleep(3)

print(f"OrderStatus：{trade.orderStatus.status}")
print(f"TradeFills：{trade.fills}")

# 断开连接
ib.disconnect()
