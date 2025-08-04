# broker/ibkr_trading.py

from ib_insync import *

class IBKRTrader:
    def __init__(self, host='127.0.0.1', port=7497, client_id=1):
        self.ib = IB()
        self.ib.connect(host, port, clientId=client_id)
        print("✅ Connected to IBKR")

    def get_price(self, symbol='TQQQ'):
        contract = Stock(symbol, 'SMART', 'USD')
        self.ib.qualifyContracts(contract)
        ticker = self.ib.reqMktData(contract)
        self.ib.sleep(2)
        self.ib.cancelMktData(contract)
        return ticker.last

    def place_order(self, symbol='TQQQ', quantity=10, action='BUY'):
        contract = Stock(symbol, 'SMART', 'USD')
        order = MarketOrder(action, quantity)
        trade = self.ib.placeOrder(contract, order)
        print(f"📤 Order Submitted: {action} {quantity} shares of {symbol}")
        self.ib.sleep(1)
        return trade

    def account_info(self):
        account = self.ib.accountSummary()
        for item in account:
            print(f"{item.tag}: {item.value} {item.currency}")

    def close(self):
        self.ib.disconnect()
        print("❎ Disconnected from IBKR")
