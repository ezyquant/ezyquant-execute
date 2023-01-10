from dataclasses import dataclass
from threading import Event
from typing import Any

import pandas as pd
from settrade_v2.user import Investor


# TODO: inherit from ezyquant.backtesting import Context
@dataclass
class ExecuteContext:
    settrade_user: Investor
    """Settrade user."""
    event: Event
    """Event object to stop execute algorithm."""
    symbol: str
    """Selected symbol."""
    signal: Any
    """Signal."""

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
