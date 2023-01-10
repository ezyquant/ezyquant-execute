from dataclasses import dataclass
from threading import Event
from typing import Any, Optional

import pandas as pd
from settrade_v2.equity import InvestorEquity
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
    account_no: str
    """Account number."""
    pin: str
    """PIN."""
    event: Event
    """Event object to stop on timer."""

    @property
    def ts(self) -> pd.Timestamp:
        """Current timestamp."""
        return pd.Timestamp.now()

    """
    Price functions
    """

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

    """
    Position functions
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

    """
    Place order functions
    """

    def buy(
        self,
        volume: int,
        price: float,
        qty_open: int = 0,
        trustee_id_type: str = "Local",
        price_type: str = "Limit",
        validity_type: str = "Day",
        bypass_warning: Optional[bool] = None,
        valid_till_date: Optional[str] = None,
    ) -> dict:
        """Place buy order."""
        return self._settrade_equity.place_order(
            pin=self.pin,
            side="buy",
            symbol=self.symbol,
            volume=volume,
            price=price,
            qty_open=qty_open,
            trustee_id_type=trustee_id_type,
            price_type=price_type,
            validity_type=validity_type,
            bypass_warning=bypass_warning,
            valid_till_date=valid_till_date,
        )

    def sell(
        self,
        volume: int,
        price: float,
        qty_open: int = 0,
        trustee_id_type: str = "Local",
        price_type: str = "Limit",
        validity_type: str = "Day",
        bypass_warning: Optional[bool] = None,
        valid_till_date: Optional[str] = None,
    ) -> dict:
        """Place sell order."""
        return self._settrade_equity.place_order(
            pin=self.pin,
            side="sell",
            symbol=self.symbol,
            volume=volume,
            price=price,
            qty_open=qty_open,
            trustee_id_type=trustee_id_type,
            price_type=price_type,
            validity_type=validity_type,
            bypass_warning=bypass_warning,
            valid_till_date=valid_till_date,
        )

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
        """Buy from the given value. calculate the buy volume by value / best
        ask price.

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
        """Sell from the given value. calculate the sell volume by value / best
        bid price.

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
    Cancel order functions
    """

    def cancel_all_orders(self) -> dict:
        """Cancel all orders with the same symbol."""
        orders = self._settrade_equity.get_orders()
        order_no_list = [order["order_id"] for order in orders]
        return self._settrade_equity.cancel_orders(
            order_no_list=order_no_list, pin=self.pin
        )

    def cancel_all_buy_orders(self):
        """Cancel all buy orders with the same symbol."""

    def cancel_all_sell_orders(self):
        """Cancel all sell orders with the same symbol."""

    def cancel_orders_by_price(self, price: float):
        """Cancel all orders with the same symbol and price."""

    """
    Settrade Open API functions
    """

    @property
    def _settrade_market_data(self) -> MarketData:
        return self.settrade_user.MarketData()

    @property
    def _settrade_equity(self) -> InvestorEquity:
        return self.settrade_user.Equity(account_no=self.account_no)

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
