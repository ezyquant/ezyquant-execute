from dataclasses import dataclass
from threading import Event
from typing import Any

import pandas as pd
from settrade_v2.market import MarketData
from settrade_v2.user import Investor


@dataclass
class ExecuteContext:
    symbol: str
    """Selected symbol."""
    signal: Any
    """Signal."""
    settrade_user: Investor
    """Settrade user."""
    event: Event
    """Event object to stop on timer."""

    @property
    def ts(self) -> pd.Timestamp:
        """Current timestamp."""
        return pd.Timestamp.now()

    @property
    def market_price(self) -> float:
        """Market price from settrade open api."""
        return self.get_quote_symbol()["last"]

    @property
    def best_bid_price(self) -> float:
        """Best bid price from settrade open api."""

    @property
    def best_ask_price(self) -> float:
        """Best ask price from settrade open api."""

    @property
    def cost_price(self) -> float:
        """Cost price.

        return 0.0 if no position.
        """

    @property
    def volume(self) -> float:
        """Current volume."""

    @property
    def cash(self) -> float:
        """Available cash."""

    @property
    def total_cost_value(self) -> float:
        """Sum of all stock market value in portfolio."""

    @property
    def total_market_value(self) -> float:
        """Sum of all stock cost value in portfolio."""

    @property
    def port_value(self) -> float:
        """Total portfolio value."""

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

    """
    Backtesting Context
    """

    def buy_pct_port(self, pct_port: float) -> dict:
        """Buy from the percentage of the portfolio. calculate the buy volume by pct_port * port_value / best ask price.

        Parameters
        ----------
        pct_port: float
            percentage of the portfolio

        Returns
        -------
        float
            buy volume, always positive, not round 100
        """
        return self.buy_value(self.port_value * pct_port)

    def buy_value(self, value: float) -> dict:
        """Buy from the given value. calculate the buy volume by value / best ask price.

        Parameters
        ----------
        value: float
            value

        Returns
        -------
        float
            buy volume, always positive, not round 100
        """

    def sell_pct_port(self, pct_port: float) -> dict:
        """Sell from the percentage of the portfolio. calculate the sell volume by pct_port * port_value / best ask price.
        Parameters
        ----------
        pct_port: float
            percentage of the portfolio

        Returns
        -------
        float
            sell volume, always negative, not round 100
        """
        return self.sell_value(self.port_value * pct_port)

    def sell_value(self, value: float) -> dict:
        """Sell from the given value. calculate the sell volume by value / best bid price.

        Parameters
        ----------
        value: float
            value

        Returns
        -------
        float
            sell volume, always negative, not round 100
        """

    def target_pct_port(self, pct_port: float) -> dict:
        """Buy/Sell to make the current position reach the target percentage of
        the portfolio. Calculate the buy/sell volume by compare between the
        best bid/ask price.

        Parameters
        ----------
        pct_port: float
            percentage of the portfolio

        Returns
        -------
        float
            buy/sell volume, not round 100
        """
        return self.target_value(self.port_value * pct_port)

    def target_value(self, value: float) -> dict:
        """Buy/Sell to make the current position reach the target value.
        Calculate the buy/sell volume by compare between the best bid/ask
        price.

        Parameters
        ----------
        value: float
            value

        Returns
        -------
        float
            buy/sell volume, not round 100
        """

    """
    Settrade Open API functions
    """

    @property
    def _settrade_market_data(self) -> MarketData:
        return self.settrade_user.MarketData()

    def get_candlestick_df(self, limit: int = 5) -> pd.DataFrame:
        """Get candlestick data from settrade open api.

        Columns: ["lastSequence", "time", "open", "high", "low", "close", "volume", "value"]
        """
        df = pd.DataFrame(
            self._settrade_market_data.get_candlestick(
                symbol=self.symbol, interval="1d", limit=limit
            )
        )
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert(
            "Asia/Bangkok"
        )
        return df

    def get_quote_symbol(self) -> dict:
        """Get quote symbol from settrade open api."""
        return self._settrade_market_data.get_quote_symbol(symbol=self.symbol)
