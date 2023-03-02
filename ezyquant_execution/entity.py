import inspect
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional

import pandas as pd

from . import utils

SIDE_BUY = "Buy"
SIDE_SELL = "Sell"
SIDE_TYPE = Literal["Buy", "Sell"]


PRICE_TYPE_LIMIT = "Limit"
PRICE_TYPE_ATO = "ATO"
PRICE_TYPE_ATC = "ATC"
PRICE_TYPE_MP_MKT = "MP-MKT"
PRICE_TYPE_MP_MTL = "MP-MTL"
PRICE_TYPE = Literal["Limit", "ATO", "ATC", "MP-MKT", "MP-MTL"]


VALIDITY_TYPE_DAY = "Day"
VALIDITY_TYPE_FOK = "FOK"
VALIDITY_TYPE_IOC = "IOC"
VALIDITY_TYPE_DATE = "Date"
VALIDITY_TYPE_CANCEL = "Cancel"
VALIDITY_TYPE = Literal["Day", "FOK", "IOC", "Date", "Cancel"]


class SettradeStruct:
    @classmethod
    def from_camel_dict(cls, dct: dict):
        snake_dct = {utils.camel_to_snake(k): v for k, v in dct.items()}
        return cls(
            **{
                k: v
                for k, v in snake_dct.items()
                if k in inspect.signature(cls).parameters
            }
        )


@dataclass
class StockQuoteResponse(SettradeStruct):
    instrument_type: str
    symbol: str
    high: float
    low: float
    last: float
    average: float
    change: float
    percent_change: float
    total_volume: int
    security_type: str
    eps: float
    pe: float
    pbv: float
    percent_yield: float
    maturity_date: str
    exercise_price: float
    underlying: str
    underlying_price: float
    intrinsic_value: float
    theoretical: float
    moneyness: str
    last_trading_date: str
    to_last_trade: int
    exercise_ratio: float
    implied_volatility: float
    exchange: str
    aum_size: float
    inav: float


# Market Section
@dataclass
class BidOfferItem:
    price: float
    volume: int


@dataclass
class BidOffer:
    symbol: str
    bids: List[BidOfferItem]
    asks: List[BidOfferItem]

    @property
    def best_bid_price(self):
        return self.bids[0].price

    @property
    def best_bid_volume(self):
        return self.bids[0].volume

    @property
    def best_ask_price(self):
        return self.asks[0].price

    @property
    def best_ask_volume(self):
        return self.asks[0].volume

    @property
    def dataframe(self):
        data = {
            "bid_volume": [i.volume for i in self.bids],
            "bid_price": [i.price for i in self.bids],
            "ask_price": [i.price for i in self.asks],
            "ask_volume": [i.volume for i in self.asks],
        }
        return pd.DataFrame(data)

    def __str__(self):
        return self.dataframe.to_string()

    @classmethod
    def from_dict(cls, data: dict):
        bids = [
            BidOfferItem(price=data[f"bid_price{i}"], volume=data[f"bid_volume{i}"])
            for i in range(1, 11)
        ]
        asks = [
            BidOfferItem(price=data[f"ask_price{i}"], volume=data[f"ask_volume{i}"])
            for i in range(1, 11)
        ]
        return cls(data["symbol"], bids, asks)


@dataclass
class PriceInfo(SettradeStruct):
    symbol: str
    projected_open_price: Optional[float]
    high: Optional[float]
    low: Optional[float]
    last: Optional[float]
    change: float
    total_volume: float
    total_value: float
    market_status: str

    def __post_init__(self):
        for i in ["projected_open_price", "high", "low", "last"]:
            if not getattr(self, i):
                setattr(self, i, None)


@dataclass
class BaseAccountInfo(SettradeStruct):
    line_available: float
    """Line available"""
    credit_limit: float
    """Credit limit"""
    cash_balance: float
    """Cash balance"""
    account_type: str
    """Account Type"""
    client_type: str
    """Client Type"""
    customer_type: str
    """Customer Type"""
    can_buy: bool
    """Flag indicates that the account has a permission to buy stock"""
    can_sell: bool
    """Flag indicates that the account has a permission to sell stock"""
    crossing_key: str
    """Crossing Key"""
    credit_balance: float
    """Credit Balance"""


@dataclass
class PortfolioResponse:
    portfolio_list: List["EquityPortfolio"]
    total_portfolio: "EquityPortfolio"

    @classmethod
    def from_camel_dict(cls, dct: dict):
        return cls(
            portfolio_list=[
                EquityPortfolio.from_camel_dict(i) for i in dct["portfolioList"]
            ],
            total_portfolio=EquityPortfolio.from_camel_dict(dct["totalPortfolio"]),
        )


@dataclass
class EquityPortfolio(SettradeStruct):
    symbol: str
    """Symbol"""
    flag: str
    """Flag indicates stock's condition (if any). Return description will be display description, for example (P) for margin pledge symbol"""
    nvdr_flag: str
    """Flag indicates trustee type"""
    market_price: float
    """Current market price"""
    amount: float
    """Amount"""
    marketdescription: float
    """Market description"""
    market_value: float
    """Market value"""
    profit: float
    """Profit/Loss"""
    percent_profit: float
    """Percentage of profit"""
    realize_profit: float
    """Realized profit/loss"""
    start_volume: float
    """Initial volume"""
    current_volume: float
    """Current volume"""
    actual_volume: float
    """Actual volume"""
    start_price: float
    """Initial price"""
    average_price: float
    """Average price"""
    show_na: bool
    """Flag indicates symbol non-existence. Return true if the stock isn't existed."""
    port_flag: str
    """Portfolio flag"""
    margin_rate: float
    """Margin rate"""
    liabilities: float
    """Liabilities"""
    commission_rate: float
    """Commission rate"""
    vat_rate: float
    """Vat rate"""


@dataclass
class EquityOrder(SettradeStruct):
    enter_id: str
    """Enter Id"""
    account_no: str
    """Account number"""
    order_no: str
    """Settrade Order number"""
    set_order_no: str
    """SET order number"""
    symbol: str
    """Symbol"""
    trade_date: str
    """Trade date (yyyy-MM-dd)"""
    trade_time: str
    """Trade time (yyyy-MM-dd'T'HH:mm:ss)"""
    entry_time: str
    """Entry time (yyyy-MM-dd'T'HH:mm:ss)"""
    side: SIDE_TYPE
    """Order side"""
    price_type: PRICE_TYPE
    """Account number"""
    price: float
    """Price"""
    vol: int
    """Volume"""
    iceberg_vol: int
    """Iceberg volume"""
    validity: VALIDITY_TYPE
    """Order validity"""
    order_type: str
    """Order type"""
    matched: int
    """Matched volume"""
    balance: int
    """Balance volume"""
    cancelled: int
    """Cancelled volume"""
    status: str
    """Order status"""
    show_order_status: str
    """Order status (display)"""
    show_order_status_meaning: str
    """Order status meaning"""
    reject_code: int
    """Reject code"""
    reject_reason: str
    """Reject reason"""
    cancel_id: str
    """Cancel Id"""
    cancel_time: str
    """Cancel time(yyyy-MM-dd'T'HH:mm:ss)"""
    version: int
    """Version of the order"""
    nvdr_flag: str
    """Flag indicates trustee type"""
    can_change_account: bool
    """Flag indicates that the order is allowed to change its account"""
    can_change_trustee_id: bool
    """Flag indicates that the order is allowed to change its trustee Id"""
    can_change_price_vol: bool
    """Flag indicates that the order is allowed to change its price or volume"""
    can_cancel: bool
    """Flag indicates that the order is allowed to be cancelled"""
    counter_party_member: str
    """Counter party member Id"""
    trade_report_type: str
    """Trade report type"""
    trade_report: bool
    """Flag indicates that the order is trade report"""
    terminal_type: str
    """Terminal Type"""
    valid_till_date: str
    """Valid Till Date (yyyy-MM-dd)"""


@dataclass
class EquityTrade(SettradeStruct):
    broker_id: str
    """Broker Id"""
    order_no: str
    """Order number"""
    entry_id: str
    """Entry Id (If the order placed by marketing representative)"""
    account_no: str
    """Account number"""
    trade_no: str
    """Trade number"""
    deal_no: str
    """Deal number"""
    trade_date: str
    """Trade date (yyyy-MM-dd)"""
    trade_time: str
    """Trade time (yyyy-MM-dd'T'HH:mm:ss)"""
    symbol: str
    """Symbol"""
    side: SIDE_TYPE
    """Order side"""
    qty: int
    """Volume"""
    px: float
    """Price"""
    trustee_id: str
    """Trustee type"""
    brokerage_fee: float
    """Brokerage fee"""
    trading_fee: float
    """Trading Fee"""
    clearing_fee: float
    """Clearing Fee"""


@dataclass
class CancelOrder(SettradeStruct):
    order_no: str
    """Order number"""
    error_response: Dict[str, Any]
    http_status: str
    """HTTP status"""
    http_status_code: int
    """HTTP status code"""
