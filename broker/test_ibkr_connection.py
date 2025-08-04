from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 4001, clientId=1)

contract = Stock('TQQQ', 'SMART', 'USD')
ib.qualifyContracts(contract)

ticker = ib.reqMktData(contract, snapshot=True, regulatorySnapshot=False)
ib.sleep(2)

print("✅ Connected to IBKR")
print("🔍 marketPrice:", ticker.marketPrice())
print("📉 close price:", ticker.close)

ib.disconnect()
