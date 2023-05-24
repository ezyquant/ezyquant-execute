import logging
import time as t
from datetime import datetime
from functools import cached_property, lru_cache
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from settrade_v2.context import Context
from settrade_v2.equity import InvestorEquity, MarketRepEquity
from settrade_v2.market import MarketData
from settrade_v2.realtime import RealtimeDataConnection
from settrade_v2.user import Investor, MarketRep, _BaseUser

from . import utils
from .entity import (
    PRICE_TYPE,
    SIDE_BUY,
    SIDE_SELL,
    SIDE_TYPE,
    VALIDITY_TYPE,
    BaseAccountInfo,
    CancelOrder,
    EquityOrder,
    EquityPortfolio,
    EquityTrade,
    PortfolioResponse,
    StockQuoteResponse,
)
from .realtime import BidOfferSubscriber, PriceInfoSubscriber

logger = logging.getLogger(__name__)

# Override _BaseUser.RealtimeDataConnection
# because subscribe will error if init RealtimeDataConnection more than once
# Can remove this line if this issue is fixed
_BaseUser.RealtimeDataConnection = lru_cache(maxsize=1)(
    _BaseUser.RealtimeDataConnection
)

T = TypeVar("T")


def new_refresh(self):
    res = self.request(
        "POST",
        self.refresh_token_path,
        json={"apiKey": self.app_id, "refreshToken": self.refresh_token},
    )
    if not res.ok:
        self.login()  # Added line
        return
    self.token = res.json()["access_token"]
    self.refresh_token = res.json()["refresh_token"]
    self.expired_at = int(t.time()) + res.json()["expires_in"]


# Override refresh method
Context.refresh = new_refresh


class ExecuteContext:
    def __init__(
        self,
        settrade_user: Union[Investor, MarketRep],
        account_no: str,
        pin: Optional[str] = None,
    ):
        """Execute context.

        Parameters
        ----------
        settrade_user : Union[Investor, MarketRep]
            Settrade user
        account_no : str
            Account number
        pin : Optional[str], optional
            PIN. Only for investor.
        """
        self.settrade_user = settrade_user
        self.account_no = account_no
        self.pin = pin

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def ts(self) -> datetime:
        """Current timestamp."""
        return datetime.now()

    """
    Account functions
    """

    @property
    def line_available(self) -> float:
        """Line Available."""
        return self.get_account_info().line_available

    @property
    def cash_balance(self) -> float:
        """Cash Balance."""
        return self.get_account_info().cash_balance

    @property
    def total_cost_value(self) -> float:
        """Sum of all stock market value in portfolio."""
        return self.get_portfolios().total_portfolio.amount

    @property
    def total_market_value(self) -> float:
        """Sum of all stock cost value in portfolio."""
        return self.get_portfolios().total_portfolio.market_value

    @property
    def port_value(self) -> float:
        """Total portfolio value."""
        return self.cash_balance + self.total_market_value

    @property
    def cash(self) -> float:
        """Cash Balance."""
        return self.cash_balance

    """
    Cancel order functions
    """

    def cancel_orders(
        self, condition: Callable[[EquityOrder], bool] = lambda _: True
    ) -> List[CancelOrder]:
        """Cancel orders.

        Parameters
        ----------
        condition: Callable[[dict], bool]
            condition function

        Returns
        -------
        dict
            cancel order result
        """
        orders = self.get_orders(lambda x: x.can_cancel and condition(x))
        order_no_list = [i.order_no for i in orders]
        return self._cancel_orders(order_no_list)

    def cancel_buy_orders(self) -> List[CancelOrder]:
        """Cancel all buy orders."""
        return self.cancel_orders(lambda x: x.side.capitalize() == SIDE_BUY)

    def cancel_sell_orders(self) -> List[CancelOrder]:
        """Cancel all sell orders."""
        return self.cancel_orders(lambda x: x.side.capitalize() == SIDE_SELL)

    def cancel_price_orders(self, price: float) -> List[CancelOrder]:
        """Cancel all orders with price."""
        return self.cancel_orders(lambda x: x.price == price)

    def _cancel_orders(self, order_no_list: List[str]) -> List[CancelOrder]:
        if not order_no_list:
            return []

        res = self._settrade_equity.cancel_orders(
            order_no_list=order_no_list, **self._pin_acc_no_kw
        )
        out = [CancelOrder.from_camel_dict(i) for i in res["results"]]

        for i in out:
            if i.error_response is not None:
                logger.warn(
                    f"Cancel order {i.order_no} failed: {i.error_response['message']}"
                )

        return out

    """
    Settrade SDK functions
    """

    @property
    def _acc_no_kw(self) -> dict:
        return (
            {"account_no": self.account_no}
            if isinstance(self.settrade_user, MarketRep)
            else {}
        )

    @property
    def _pin_acc_no_kw(self) -> dict:
        return (
            {"account_no": self.account_no}
            if isinstance(self.settrade_user, MarketRep)
            else {"pin": self.pin}
        )

    @property
    def _settrade_equity(self) -> Union[InvestorEquity, MarketRepEquity]:
        kw = (
            {"account_no": self.account_no}
            if isinstance(self.settrade_user, Investor)
            else {}
        )
        return self.settrade_user.Equity(**kw)

    @property
    def _settrade_market_data(self) -> MarketData:
        return self.settrade_user.MarketData()

    @property
    def _settrade_realtime_data_connection(self) -> RealtimeDataConnection:
        return self.settrade_user.RealtimeDataConnection()

    def get_account_info(self) -> BaseAccountInfo:
        """Get account info."""
        res = self._settrade_equity.get_account_info(**self._acc_no_kw)
        return BaseAccountInfo.from_camel_dict(res)

    def get_portfolios(self) -> PortfolioResponse:
        """Get portfolios."""
        res: Dict[str, Any] = self._settrade_equity.get_portfolios(**self._acc_no_kw)  # type: ignore
        return PortfolioResponse.from_camel_dict(res)

    def get_orders(self, condition: Callable = lambda _: True) -> List[EquityOrder]:
        """Get orders."""
        if isinstance(self._settrade_equity, InvestorEquity):
            res = self._settrade_equity.get_orders()
        else:
            res = self._settrade_equity.get_orders_by_account_no(
                account_no=self.account_no
            )
        out = [EquityOrder.from_camel_dict(i) for i in res]
        out = self._filter_list(out, condition)
        return out

    def get_trades(self, condition: Callable = lambda _: True) -> List[EquityTrade]:
        """Get trades."""
        res = self._settrade_equity.get_trades(**self._acc_no_kw)
        out = [EquityTrade.from_camel_dict(i) for i in res]
        out = self._filter_list(out, condition)
        return out

    """
    Override functions
    """

    def get_portfolio(self, symbol: str) -> Optional[EquityPortfolio]:
        """Get portfolio of the symbol."""
        res = self.get_portfolios()
        for i in res.portfolio_list:
            if i.symbol == symbol:
                return i
        return None

    def place_order(
        self,
        symbol: str,
        side: SIDE_TYPE,
        volume: float,
        price: float,
        qty_open: int = 0,
        trustee_id_type: str = "Local",
        price_type: PRICE_TYPE = "Limit",
        validity_type: VALIDITY_TYPE = "Day",
        bypass_warning: Optional[bool] = True,
        valid_till_date: Optional[str] = None,
    ) -> Optional[EquityOrder]:
        """Place order.

        Round volume to 100. If volume is 0, return None.
        """
        volume = utils.round_100(volume)
        if volume == 0:
            return

        res = self._settrade_equity.place_order(
            symbol=symbol,
            side=side,
            volume=volume,
            price=price,
            qty_open=qty_open,
            trustee_id_type=trustee_id_type,
            price_type=price_type,
            validity_type=validity_type,
            bypass_warning=bypass_warning,
            valid_till_date=valid_till_date,
            **self._pin_acc_no_kw,
        )
        return EquityOrder.from_camel_dict(res)

    def get_quote_symbol(self, symbol: str) -> StockQuoteResponse:
        """Get quote symbol."""
        res = self._settrade_market_data.get_quote_symbol(symbol=symbol)
        return StockQuoteResponse.from_camel_dict(res)

    def _filter_list(self, l: List[T], condition: Callable = lambda _: True) -> List[T]:
        """Filter list by symbol and condition."""
        return [i for i in l if condition(i)]


class ExecuteContextSymbol(ExecuteContext):
    def __init__(
        self,
        settrade_user: Union[Investor, MarketRep],
        account_no: str,
        symbol: str,
        pin: Optional[str] = None,
        signal: Any = None,
    ):
        """Execute context.

        Parameters
        ----------
        settrade_user : Union[Investor, MarketRep]
            Settrade user
        account_no : str
            Account number
        symbol : str
            Selected symbol
        pin : Optional[str], optional
            PIN. Only for investor.
        signal : Any, optional
            Signal, by default None
        """
        super().__init__(settrade_user=settrade_user, account_no=account_no, pin=pin)
        self.symbol = symbol
        self.signal = signal

    """
    Price functions
    """

    @property
    def market_price(self) -> Optional[float]:
        """Market price.

        Return 0 at pre-open session.
        """
        return self._po_sub.data.last

    @property
    def best_bid_price(self) -> float:
        """Best bid price."""
        return self._bo_sub.data.best_bid_price

    @property
    def best_ask_price(self) -> float:
        """Best ask price."""
        return self._bo_sub.data.best_ask_price

    """
    Position functions
    """

    @property
    def volume(self) -> float:
        """Actual volume."""
        ps = self.get_portfolio()
        return ps.actual_volume if ps else 0

    @property
    def cost_price(self) -> float:
        """Cost price.

        return 0.0 if no position.
        """
        ps = self.get_portfolio()
        return ps.average_price if ps else 0.0

    @property
    def cost_value(self) -> float:
        """Cost value."""
        ps = self.get_portfolio()
        return ps.amount if ps else 0.0

    @property
    def market_value(self) -> float:
        """Market value of symbol in portfolio."""
        ps = self.get_portfolio()
        return ps.market_value if ps else 0.0

    """
    Place order functions
    """

    def buy(self, volume: float, price: float) -> Optional[EquityOrder]:
        """Place buy order."""
        return self.place_order(side=SIDE_BUY, volume=volume, price=price)

    def sell(self, volume: float, price: float) -> Optional[EquityOrder]:
        """Place sell order."""
        return self.place_order(side=SIDE_SELL, volume=volume, price=price)

    def buy_pct_port(self, pct_port: float) -> Optional[EquityOrder]:
        """Buy from the percentage of the portfolio. calculate the buy volume by pct_port * port_value / best ask price.

        Parameters
        ----------
        pct_port: float
            percentage of the portfolio
        """
        return self.buy_value(self.port_value * pct_port)

    def buy_value(self, value: float) -> Optional[EquityOrder]:
        """Buy from the given value. calculate the buy volume by value / best
        ask price.

        Parameters
        ----------
        value: float
            value
        """
        price = self.best_ask_price
        volume = value / price
        return self.buy(volume=volume, price=price)

    def sell_pct_port(self, pct_port: float) -> Optional[EquityOrder]:
        """Sell from the percentage of the portfolio. calculate the sell volume by pct_port * port_value / best ask price.
        Parameters
        ----------
        pct_port: float
            percentage of the portfolio
        """
        return self.sell_value(self.port_value * pct_port)

    def sell_value(self, value: float) -> Optional[EquityOrder]:
        """Sell from the given value. calculate the sell volume by value / best
        bid price.

        Parameters
        ----------
        value: float
            value
        """
        price = self.best_bid_price
        volume = value / price
        return self.sell(volume=volume, price=price)

    def target_pct_port(self, pct_port: float) -> Optional[EquityOrder]:
        """Buy/Sell to make the current position reach the target percentage of
        the portfolio. Calculate the buy/sell volume by compare between the
        best bid/ask price.

        Parameters
        ----------
        pct_port: float
            percentage of the portfolio
        """
        return self.target_value(self.port_value * pct_port)

    def target_value(self, value: float) -> Optional[EquityOrder]:
        """Buy/Sell to make the current position reach the target value.
        Calculate the buy/sell volume by compare between the best bid/ask
        price.

        Parameters
        ----------
        value: float
            value
        """
        value -= self.market_value

        if value > 0:
            return self.buy_value(value)
        else:
            return self.sell_value(-value)

    """
    Validate order functions
    """

    def is_buy_sufficient(
        self, volume: float, price: float, pct_commission: float = 0.0
    ) -> bool:
        """Check if the line available is sufficient for buy order.

        Parameters
        ----------
        volume: float
            volume
        price: float
            price
        pct_commission: float
            percentage of commission example 0.01 for 1%
        """
        return self.line_available >= volume * price * (1 + pct_commission)

    def is_sell_sufficient(self, volume: float) -> bool:
        """Check if the volume is sufficient for sell order.

        Parameters
        ----------
        volume: float
            volume
        """
        return self.volume >= volume

    """
    Settrade SDK functions
    """

    @cached_property
    def _bo_sub(self) -> BidOfferSubscriber:
        return BidOfferSubscriber(
            symbol=self.symbol, rt_conn=self._settrade_realtime_data_connection
        )

    @cached_property
    def _po_sub(self) -> PriceInfoSubscriber:
        return PriceInfoSubscriber(
            symbol=self.symbol, rt_conn=self._settrade_realtime_data_connection
        )

    """
    Override functions
    """

    def get_portfolio(self) -> Optional[EquityPortfolio]:
        """Get portfolio of the symbol."""
        return super().get_portfolio(self.symbol)

    def place_order(
        self,
        side: SIDE_TYPE,
        volume: float,
        price: float,
        qty_open: int = 0,
        trustee_id_type: str = "Local",
        price_type: PRICE_TYPE = "Limit",
        validity_type: VALIDITY_TYPE = "Day",
        bypass_warning: Optional[bool] = True,
        valid_till_date: Optional[str] = None,
    ) -> Optional[EquityOrder]:
        """Place order.

        Round volume to 100. If volume is 0, return None.
        """
        return super().place_order(
            symbol=self.symbol,
            side=side,
            volume=volume,
            price=price,
            qty_open=qty_open,
            trustee_id_type=trustee_id_type,
            price_type=price_type,
            validity_type=validity_type,
            bypass_warning=bypass_warning,
            valid_till_date=valid_till_date,
        )

    def get_quote_symbol(self) -> StockQuoteResponse:
        """Get quote symbol."""
        return super().get_quote_symbol(self.symbol)

    def _filter_list(self, l: List[T], condition: Callable = lambda _: True) -> List[T]:
        """Filter list by symbol and condition."""
        return super()._filter_list(
            l, lambda x: x.symbol == self.symbol and condition(x)
        )
