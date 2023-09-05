import logging
import time as t
from datetime import datetime
from functools import cached_property, lru_cache
from typing import Any, Callable, Dict, List, Literal, Optional, TypeVar, Union

from settrade_v2.context import Context
from settrade_v2.derivatives import InvestorDerivatives, MarketRepDerivatives
from settrade_v2.market import MarketData
from settrade_v2.realtime import RealtimeDataConnection
from settrade_v2.user import Investor, MarketRep, _BaseUser

from ezyquant_execution.realtime import BidOfferSubscriber, PriceInfoSubscriber

from .derivative_entity import (
    CLOSE_POSITION,
    OPEN_POSITION,
    POSITION,
    PRICE_TYPE,
    SIDE_LONG,
    SIDE_SHORT,
    SIDE_TYPE,
    TRIGGER_CONDITION,
    TRIGGER_SESSION,
    VALIDITY_TYPE,
    BaseAccountDerivativeInfo,
    CancelOrder,
    DerivativeOrder,
    DerivativePortfolio,
    DerivativePortfolioResponse,
    DerivativeTrade,
    StockQuoteResponse,
)

logger = logging.getLogger(__name__)

_BaseUser.RealtimeDataConnection = lru_cache(maxsize=1)(
    _BaseUser.RealtimeDataConnection
)

T = TypeVar("T")

PLACE_ORDER_MODE_TYPE = Literal["none", "skip", "raise", "available"]


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


class ExecuteDerivativeContext:
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

    def __hash__(self):
        return id(self)

    @lru_cache
    def Symbol(self, symbol: str) -> "ExecuteDerivativeContextSymbol":
        return ExecuteDerivativeContextSymbol(
            settrade_user=self.settrade_user,
            symbol=symbol,
            account_no=self.account_no,
            pin=self.pin,
        )

    @property
    def ts(self) -> datetime:
        """Current timestamp."""
        return datetime.now()

    """
    Account functions
    """

    @property
    def excess_equity(self) -> float:
        """Excess Equity.

        The remaining funds after deducting the insurance premium from opening the contract
        can be either added to the existing account or withdrawn.
        """
        return self.get_account_info().excess_equity

    @property
    def cash_balance(self) -> float:
        """Cash Balance.

        When place order cash balance will **not** be decrease by order
        value.
        """
        return self.get_account_info().cash_balance

    @property
    def total_cost_value(self) -> float:
        """Sum of all stock cost value in portfolio.

        Include order that pending.
        """
        return self.get_portfolios().total_portfolio.amount

    @property
    def total_market_value(self) -> float:
        """Sum of all stock market value in portfolio.

        Include order that pending.
        """
        return self.get_portfolios().total_portfolio.market_value

    # @property
    # def pending_order_value(self) -> float:
    #     """Sum of all pending order value.

    #     Not include commission.
    #     """
    #     return sum(i.price * i.vol for i in self.get_orders(_is_pending_order))

    @property
    def port_value(self) -> float:
        """Total portfolio value."""
        return self.get_account_info().equity

    @property
    def cash(self) -> float:
        """Cash Balance."""
        return self.cash_balance

    """
    Cancel order functions
    """

    def cancel_orders(
        self, condition: Callable[[DerivativeOrder], bool] = lambda _: True
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

    def cancel_long_orders(self) -> List[CancelOrder]:
        """Cancel all buy orders."""
        return self.cancel_orders(lambda x: x.side.capitalize() == SIDE_LONG)

    def cancel_short_orders(self) -> List[CancelOrder]:
        """Cancel all sell orders."""
        return self.cancel_orders(lambda x: x.side.capitalize() == SIDE_SHORT)

    def cancel_price_orders(self, price: float) -> List[CancelOrder]:
        """Cancel all orders with price."""
        return self.cancel_orders(lambda x: x.price == price)

    def _cancel_orders(
        self, order_no_list: List[int]
    ) -> List[CancelOrder]:  # List[str] -> List[int]
        if not order_no_list:
            return []

        res = self._settrade_derivative.cancel_orders(
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
    def _settrade_derivative(self) -> Union[InvestorDerivatives, MarketRepDerivatives]:
        kw = (
            {"account_no": self.account_no}
            if isinstance(self.settrade_user, Investor)
            else {}
        )
        return self.settrade_user.Derivatives(**kw)

    @property
    def _settrade_market_data(self) -> MarketData:
        return self.settrade_user.MarketData()

    @property
    def _settrade_realtime_data_connection(self) -> RealtimeDataConnection:
        return self.settrade_user.RealtimeDataConnection()

    def get_account_info(self) -> BaseAccountDerivativeInfo:
        """Get derivative account info."""
        res = self._settrade_derivative.get_account_info(**self._acc_no_kw)
        return BaseAccountDerivativeInfo.from_camel_dict(res)

    def get_portfolios(self) -> DerivativePortfolioResponse:
        """Get portfolios."""
        res: Dict[str, Any] = self._settrade_derivative.get_portfolios(**self._acc_no_kw)  # type: ignore
        return DerivativePortfolioResponse.from_camel_dict(res)

    def get_orders(self, condition: Callable = lambda _: True) -> List[DerivativeOrder]:
        """Get orders."""
        if isinstance(self._settrade_derivative, InvestorDerivatives):
            res = self._settrade_derivative.get_orders()
        else:
            res = self._settrade_derivative.get_orders_by_account_no(
                account_no=self.account_no
            )
        out = [DerivativeOrder.from_camel_dict(i) for i in res]
        out = self._filter_list(out, condition)
        return out

    def get_trades(self, condition: Callable = lambda _: True) -> List[DerivativeTrade]:
        """Get trades."""
        res = self._settrade_derivative.get_trades(**self._acc_no_kw)
        out = [DerivativeTrade.from_camel_dict(i) for i in res]
        out = self._filter_list(out, condition)
        return out

    """
    Override functions
    """

    def get_portfolio(self, symbol: str) -> Optional[DerivativePortfolio]:
        """Get portfolio of the symbol."""
        res = self.get_portfolios()
        for i in res.portfolio_list:
            if i.symbol == symbol:
                return i
        return None

    def place_order(
        self,
        symbol: str,
        side: SIDE_TYPE = "Long",
        position: POSITION = "Open",
        price_type: PRICE_TYPE = "Limit",
        price: float = 0,
        volume: int = 1,
        iceberg_vol: int = 0,
        validity_type: VALIDITY_TYPE = "Day",
        validity_date_condition: Optional[str] = None,
        stop_condition: Optional[TRIGGER_CONDITION] = None,
        stop_symbol: Optional[str] = None,
        stop_price: Optional[int] = None,
        trigger_session: Optional[TRIGGER_SESSION] = None,
        bypass_warning: Optional[bool] = True,
    ) -> Optional[DerivativeOrder]:

        logger.info(f"Place order: {side} {symbol} {volume} {price}")

        res = self._settrade_derivative.place_order(
            symbol=symbol,
            side=side,
            position=position,
            price_type=price_type,
            price=price,
            volume=volume,
            iceberg_vol=iceberg_vol,
            validity_type=validity_type,
            validity_date_condition=validity_date_condition,
            stop_condition=stop_condition,
            stop_symbol=stop_symbol,
            stop_price=stop_price,
            trigger_session=trigger_session,
            bypass_warning=bypass_warning,
            **self._pin_acc_no_kw,
        )
        return DerivativeOrder.from_camel_dict(res)

    def get_quote_symbol(self, symbol: str) -> StockQuoteResponse:
        """Get quote symbol."""
        res = self._settrade_market_data.get_quote_symbol(symbol=symbol)
        return StockQuoteResponse.from_camel_dict(res)

    def _filter_list(self, l: List[T], condition: Callable = lambda _: True) -> List[T]:
        """Filter list by symbol and condition."""
        return [i for i in l if condition(i)]


class ExecuteDerivativeContextSymbol(ExecuteDerivativeContext):
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

    # @property
    # def volume(self) -> float:
    #     """Actual volume."""
    #     return self.actual_volume

    # @property
    # def actual_volume(self) -> float:
    #     """Actual volume. return 0.0 if no position.

    #     Actual volume will **not** reduce when order is placed.
    #     """
    #     ps = self.get_portfolio()
    #     return ps.actual_volume if ps else 0

    # @property
    # def current_volume(self) -> float:
    #     """Current volume. return 0.0 if no position.

    #     Current volume will reduce when order is placed.
    #     """
    #     ps = self.get_portfolio()
    #     return ps.current_volume if ps else 0

    # @property
    # def cost_price(self) -> float:
    #     """Cost price.

    #     return 0.0 if no position.
    #     """
    #     ps = self.get_portfolio()
    #     return ps.average_price if ps else 0.0

    # @property
    # def cost_value(self) -> float:
    #     """Cost value.

    #     return 0.0 if no position.
    #     """
    #     ps = self.get_portfolio()
    #     return ps.amount if ps else 0.0

    # @property
    # def market_value(self) -> float:
    #     """Market value of symbol in portfolio.

    #     return 0.0 if no position.
    #     """
    #     ps = self.get_portfolio()
    #     return ps.market_value if ps else 0.0

    # @property
    # def profit(self) -> float:
    #     """Unrealized Profit (THB).

    #     return 0.0 if no position.
    #     """
    #     ps = self.get_portfolio()
    #     return ps.profit if ps else 0.0

    # def percent_profit(self) -> float:
    #     """Unrealized Percent profit. return 0.0 if no position.

    #     Example 1.0 = 1% profit.
    #     """
    #     ps = self.get_portfolio()
    #     return ps.percent_profit if ps else 0.0

    """
    Place order functions
    """

    def buy(
        self, side: SIDE_TYPE, volume: int, price: float = 0, **kwargs
    ) -> Optional[DerivativeOrder]:
        """Place Buy Order in Long or Short Side."""
        return self.place_order(
            side=side, position=OPEN_POSITION, volume=volume, price=price, **kwargs
        )

    def sell(
        self, side: SIDE_TYPE, volume: int, price: float = 0, **kwargs
    ) -> Optional[DerivativeOrder]:
        """Place Sell Order in Long or Short Side."""
        return self.place_order(
            side=side, position=CLOSE_POSITION, volume=volume, price=price, **kwargs
        )

    # def buy_pct_port(self, pct_port: float, **kwargs) -> Optional[DerivativeOrder]:
    #     """Buy from the percentage of the portfolio. calculate the buy volume
    #     by pct_port * port_value / best ask price.

    #     Parameters
    #     ----------
    #     pct_port: float
    #         percentage of the portfolio
    #     """
    #     return self.buy_value(self.port_value * pct_port, **kwargs)

    # def buy_value(self, value: int, **kwargs) -> Optional[DerivativeOrder]:
    #     """Buy from the given value. calculate the buy volume by value / best
    #     ask price.

    #     Parameters
    #     ----------
    #     value: float
    #         value
    #     """
    #     price = self.best_ask_price
    #     volume = value / price
    #     return self.buy(volume=volume, price=price, **kwargs)

    # def sell_pct_port(self, pct_port: float, **kwargs) -> Optional[DerivativeOrder]:
    #     """Sell from the percentage of the portfolio. calculate the sell volume
    #     by pct_port * port_value / best ask price.

    #     Parameters
    #     ----------
    #     pct_port: float
    #         percentage of the portfolio
    #     """
    #     return self.sell_value(self.port_value * pct_port, **kwargs)

    # def sell_value(self, value: float, **kwargs) -> Optional[DerivativeOrder]:
    #     """Sell from the given value. calculate the sell volume by value / best
    #     bid price.

    #     Parameters
    #     ----------
    #     value: float
    #         value
    #     """
    #     price = self.best_bid_price
    #     volume = value / price
    #     return self.sell(volume=volume, price=price, **kwargs)

    # def target_pct_port(self, pct_port: float, **kwargs) -> Optional[DerivativeOrder]:
    #     """Buy/Sell to make the current position reach the target percentage of
    #     the portfolio. Calculate the buy/sell volume by compare between the
    #     best bid/ask price.

    #     Parameters
    #     ----------
    #     pct_port: float
    #         percentage of the portfolio
    #     """
    #     return self.target_value(self.port_value * pct_port, **kwargs)

    # def target_value(self, value: float, **kwargs) -> Optional[DerivativeOrder]:
    #     """Buy/Sell to make the current position reach the target value.
    #     Calculate the buy/sell volume by compare between the best bid/ask
    #     price.

    #     Parameters
    #     ----------
    #     value: float
    #         value
    #     """
    #     value -= self.market_value

    #     if value > 0:
    #         return self.buy_value(value, **kwargs)
    #     else:
    #         return self.sell_value(-value, **kwargs)

    # """
    # Validate order functions
    # """

    # def is_buy_sufficient(self, volume: float, price: float = 0.0) -> bool:
    #     """Check if the line available is sufficient for buy order.

    #     Parameters
    #     ----------
    #     volume: float
    #         volume
    #     price: float
    #         price
    #     pct_commission: float
    #         percentage of commission example 0.01 for 1%
    #     """
    #     return self.max_buy_volume(price) >= volume

    # def is_sell_sufficient(self, volume: float) -> bool:
    #     """Check if the volume is sufficient for sell order.

    #     Parameters
    #     ----------
    #     volume: float
    #         volume
    #     """
    #     return self.max_sell_volume() >= volume

    # def max_buy_volume(self, price: float = 0.0) -> float:
    #     """Get maximum buy volume.

    #     Parameters
    #     ----------
    #     price: float
    #         price
    #     """
    #     # If price_type is not limit, price is not required.
    #     if not price:
    #         price = self.best_ask_price
    #     return self. / price / (1 + cfg.SETTRADE_COMMISSIION)

    # def max_sell_volume(self) -> float:
    #     """Get maximum sell volume."""
    #     return self.current_volume

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

    def get_portfolio(self) -> Optional[DerivativePortfolio]:
        """Get portfolio of the symbol."""
        return super().get_portfolio(self.symbol)

    def place_order(
        self,
        side: SIDE_TYPE = "Long",
        position: POSITION = "Open",
        price_type: PRICE_TYPE = "Limit",
        price: float = 0,
        volume: int = 1,
        iceberg_vol: int = 0,
        validity_type: VALIDITY_TYPE = "Day",
        validity_date_condition: Optional[str] = None,
        stop_condition: Optional[TRIGGER_CONDITION] = None,
        stop_symbol: Optional[str] = None,
        stop_price: Optional[int] = None,
        trigger_session: Optional[TRIGGER_SESSION] = None,
        bypass_warning: Optional[bool] = True,
    ) -> Optional[DerivativeOrder]:
        """
        Place a derivative order.

        Parameters
        ----------
        side : SIDE_TYPE, optional
            The side of the order, either "Long" or "Short". Defaults to "Long".
        position : POSITION, optional
            The position type, "Auto", "Open", or "Close". Defaults to "Open".
        price_type : PRICE_TYPE, optional
            The price type, 'Limit', 'ATO', 'MP-MKT', or 'MP-MTL'. Defaults to "Limit".
        price : float, optional
            The price at which to execute the order. Defaults to 0.
        volume : int, optional
            The volume of the order. Defaults to 1.
        iceberg_vol : int, optional
            The iceberg volume, i.e., the visible part of the order. Defaults to 0.
        validity_type : VALIDITY_TYPE, optional
            The validity type, 'Day', 'FOK' (Fill or Kill), 'IOC' (Immediate or Cancel), 'Date', 'Cancel'. Defaults to "Day".
        validity_date_condition : Optional[str], optional
            The validity date condition for the order. Defaults to None.
        stop_condition : Optional[TRIGGER_CONDITION], optional
            The stop condition for the order. Defaults to None.
        stop_symbol : Optional[str], optional
            The symbol for the stop condition. Defaults to None.
        stop_price : Optional[int], optional
            The stop price for the order. Defaults to None.
        trigger_session : Optional[TRIGGER_SESSION], optional
            The trigger session for the order. Options are 'Pre-Open1', 'Open1', 'Day', 'Pre-Open2', 'Open2', 'Pre-Open0', 'Open0'. Defaults to None.
        bypass_warning : Optional[bool], optional
            Whether to bypass any warning messages. Defaults to True.

        Returns
        -------
        Optional[DerivativeOrder]
            Returns the derivative order placed.

        """
        return super().place_order(
            symbol=self.symbol,
            side=side,
            position=position,
            price_type=price_type,
            price=price,
            volume=volume,
            iceberg_vol=iceberg_vol,
            validity_type=validity_type,
            validity_date_condition=validity_date_condition,
            stop_condition=stop_condition,
            stop_symbol=stop_symbol,
            stop_price=stop_price,
            trigger_session=trigger_session,
            bypass_warning=bypass_warning,
        )

    def get_quote_symbol(self) -> StockQuoteResponse:
        """Get quote symbol."""
        return super().get_quote_symbol(self.symbol)

    def _filter_list(self, l: List[T], condition: Callable = lambda _: True) -> List[T]:
        """Filter list by symbol and condition."""
        return super()._filter_list(
            l, lambda x: x.symbol == self.symbol and condition(x)
        )


def _is_pending_order(order: DerivativeOrder) -> bool:
    return order.balance_qty > 0 and "Expired" not in order.show_status
    # return order.can_cancel # This not work because GTC order can't cancel after market close
    # return order.balance > 0 # This not work because Expired order still have balance > 0
