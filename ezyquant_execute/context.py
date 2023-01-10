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
    """Event object to stop execute algorithm."""

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

    @property
    def close_price(self) -> float:
        """Close price from settrade open api."""
        return self.market_price

    def buy_pct_port(self, pct_port: float) -> float:
        """Calculate buy volume from the percentage of the portfolio.

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

    def buy_value(self, value: float) -> float:
        """Calculate buy volume from the given value.

        Parameters
        ----------
        value: float
            value

        Returns
        -------
        float
            buy volume, always positive, not round 100
        """
        return value / self.close_price

    def buy_pct_position(self, pct_position: float) -> float:
        """Calculate buy volume from the percentage of the current position.

        Parameters
        ----------
        pct_position: float
            percentage of position

        Returns
        -------
        float
            buy volume, always positive, not round 100
        """
        return pct_position * self.volume

    def sell_pct_port(self, pct_port: float) -> float:
        """Calculate sell volume from the percentage of the portfolio.
        Parameters
        ----------
        pct_port: float
            percentage of the portfolio

        Returns
        -------
        float
            sell volume, always negative, not round 100
        """
        return self.buy_pct_port(-pct_port)

    def sell_value(self, value: float) -> float:
        """Calculate sell volume from the given value.

        Parameters
        ----------
        value: float
            value

        Returns
        -------
        float
            sell volume, always negative, not round 100
        """
        return self.buy_value(-value)

    def sell_pct_position(self, pct_position: float) -> float:
        """Calculate sell volume from the percentage of the current position.

        Parameters
        ----------
        pct_position: float
            percentage of position

        Returns
        -------
        float
            sell volume, always negative, not round 100
        """
        return self.buy_pct_position(-pct_position)

    def target_pct_port(self, pct_port: float) -> float:
        """Calculate buy/sell volume to make the current position reach the
        target percentage of the portfolio.

        Parameters
        ----------
        pct_port: float
            percentage of the portfolio

        Returns
        -------
        float
            buy/sell volume, not round 100
        """
        return self.buy_pct_port(pct_port) - self.volume

    def target_value(self, value: float) -> float:
        """Calculate buy/sell volume to make the current position reach the
        target value.

        Parameters
        ----------
        value: float
            value

        Returns
        -------
        float
            buy/sell volume, not round 100
        """
        return self.buy_value(value) - self.volume

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
