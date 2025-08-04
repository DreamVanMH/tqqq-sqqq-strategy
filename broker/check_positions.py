from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=1)

# 查询当前所有持仓
positions = ib.positions()
for p in positions:
    print(f"Symbol：{p.contract.symbol}, Position：{p.position}, AvgCost：{p.avgCost}")

ib.disconnect()
