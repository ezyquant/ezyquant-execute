from dataclasses import dataclass
from typing import Optional

import pandas as pd
from ezyquant.backtesting import Context
from settrade_v2.user import Investor


@dataclass
class ExecuteContext(Context):
    settrade_user: Optional[Investor] = None  # TODO: remove optional

    @property
    def ts(self) -> pd.Timestamp:
        """Current timestamp."""
        return pd.Timestamp.now()

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
