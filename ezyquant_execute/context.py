from ezyquant.backtesting import Context
from settrade_v2.user import Investor


class ExecuteContext(Context):
    settrade_user: Investor

    @property
    def market_price(self):
        """Market price from settrade open api."""

    @property
    def best_bid_price(self):
        """Best bid price from settrade open api."""

    @property
    def best_ask_price(self):
        """Best ask price from settrade open api."""

    def buy(self):
        pass

    def sell(self):
        pass

    def cancel_all_orders(self):
        pass

    def cancel_all_buy_orders(self):
        pass

    def cancel_all_sell_orders(self):
        pass

    def cancel_orders_by_price(self, price: float):
        pass
