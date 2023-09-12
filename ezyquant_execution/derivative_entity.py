import inspect
from dataclasses import dataclass
from typing import Any, Dict, List, Literal

import pandas as pd

from . import utils

# ORDER AND TRADE
SIDE_LONG = "Long"
SIDE_SHORT = "Short"
SIDE_TYPE = Literal["Long", "Short"]

# TRADE
OPEN_CLOSE_TYPE = Literal["AUTO", "OPEN", "CLOSE"]
STATUS_TYPE = Literal["UNREGISTRATION", "ACTIVE", "RECTIFIED"]
TRADE_TYPE = Literal["NEW", "REVERSING", "OVERTAKING"]
CURRENCY_TYPE = Literal["THB", "USD"]

# ORDER REQUEST
OPEN_POSITION = "Open"
CLOSE_POSITION = "Close"
POSITION = Literal["Auto", "Open", "Close"]
PRICE_TYPE = Literal["Limit", "ATO", "MP-MKT", "MP-MTL"]
VALIDITY_TYPE = Literal["Day", "FOK", "IOC", "Date", "Cancel"]
TRIGGER_CONDITION = Literal[
    "ASK_OR_HIGHER",
    "ASK_OR_LOWER",
    "BID_OR_HIGHER",
    "BID_OR_LOWER",
    "LAST_PAID_OR_HIGHER",
    "LAST_PAID_OR_LOWER",
    "SESSION",
]
TRIGGER_SESSION = Literal[
    "Pre-Open1", "Open1", "Day", "Pre-Open2", "Open2", "Pre-Open0", "Open0"
]

# QUOTE SYMBOL
MARKET_STATUS_DISPLAY_TYPE = Literal[
    "Close",
    "Pre-Open1",
    "Pre-Open",
    "Freeze1",
    "Open1",
    "Open",
    "Intermission1",
    "Pre-Open2",
    "Freeze2",
    "Open2",
    "Pre-Close",
    "Freeze3",
    "OffHour",
    "Circuit Breaker",
    "Full Halt",
]


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
    instrumentType: str
    symbol: str
    high: float
    low: float
    last: float
    average: float
    change: float
    percentChange: float
    totalVolume: int
    marketName: str
    marketStatus: MARKET_STATUS_DISPLAY_TYPE
    underlying: str
    underlyingPrice: float
    multiplier: int
    expDate: str
    lastTradingDate: str
    spread: float
    settlement: float
    previousSettle: float
    openInterest: int
    theoretical: float
    basis: float


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
class BaseAccountDerivativeInfo(SettradeStruct):
    credit_line: float
    """Line Available"""
    excess_equity: float
    """Excess Equity"""
    cash_balance: float
    """Cash Balance"""
    equity: float
    """Equity Balance"""
    total_mr: float
    """Total Margin Required"""
    total_mm: float
    """Total Maintenance Margin"""
    total_fm: float
    """Call Force Margin Value"""
    call_force_flag: str
    """Call Force Flag: `No` - None, `C` - Call margin, `F` - Force close margin"""
    call_force_margin: float
    """Call Force Margin Value"""
    liquidation_value: float
    """Liquidation Value"""
    deposit_withdrawal: float
    """Deposit Withdrawal"""
    call_force_margin_mm: float
    """Call Force Margin MM"""
    initial_margin: float
    """Initial Margin"""
    closing_method: str
    """Closing Method"""


@dataclass
class DerivativePortfolioResponse:
    portfolio_list: List["DerivativePortfolio"]
    total_portfolio: "DerivativeTotalPortfolio"

    @classmethod
    def from_camel_dict(cls, dct: dict):
        return cls(
            portfolio_list=[
                DerivativePortfolio.from_camel_dict(i) for i in dct["portfolioList"]
            ],
            total_portfolio=DerivativeTotalPortfolio.from_camel_dict(
                dct["totalPortfolio"]
            ),
        )


@dataclass
class DerivativePortfolio(SettradeStruct):
    broker_id: str
    """Broker Id"""
    account_no: str
    """Account number"""
    symbol: str
    """Symbol"""
    underlying: str
    """Underlying symbol"""
    security_type: str
    """Security type
    * `FUTURES` - Futures
    * `OPTIONS` - Options
    * `FUTURES (Futures),OPTIONS (Options)`"""
    last_trading_date: str
    """Last trading date of the symbol (yyyy-MM-dd)"""
    multiplier: float
    """Multiplier"""
    currency: str
    """Currency
    * `THB` - Thai Baht
    * `USD` - US Dollar
    * `THB (Thai Baht),USD (US Dollar)`"""
    current_xrt: float
    """Current currency exchange rate (as Thai Baht)"""
    as_of_date_xrt: str
    """Current currency exchange rate as of date (yyyy-MM-dd'T'HH:mm:ss)"""
    has_long_position: bool
    """Flag indicates order position (true if the order is a long position)"""
    start_long_position: int
    """Initial volume of long position order"""
    actual_long_position: int
    """Actual volume of long position order"""
    available_long_position: int
    """Available volume of long position order"""
    start_long_price: float
    """Initial price of long position order"""
    start_long_cost: float
    """Initial cost of long position order"""
    long_avg_price: float
    """Average price of long position order"""
    long_avg_cost: float
    """Average cost of long position order"""
    short_avg_cost_thb: float
    """Average cost of short position order in THB"""
    long_avg_cost_thb: float
    """Average cost of long position order in THB"""
    open_long_position: int
    """Volume of open long position order"""
    close_long_position: int
    """Volume of close long position order"""
    start_xrt_long: float
    """Initial currency exchange rate of long position order"""
    start_xrt_long_cost: float
    """Initial currency exchange rate (cost) of long position order"""
    avg_xrt_long: float
    """Average currency exchange rate of long position order"""
    avg_xrt_long_cost: float
    """Average currency exchange rate (cost) of long position order"""
    has_short_position: bool
    """Flag indicates order position (true if the order is a short position)"""
    start_short_position: int
    """Initial volume of short position order"""
    actual_short_position: int
    """Actual volume of short position order"""
    available_short_position: int
    """Available volume of short position order"""
    start_short_price: float
    """Initial price of short position order"""
    start_short_cost: float
    """Initial cost of short position order"""
    short_avg_price: float
    """Average price of short position order"""
    short_avg_cost: float
    """Average cost of short position order"""
    open_short_position: int
    """Volume of open short position order"""
    close_short_position: int
    """Volume of close short position order"""
    start_xrt_short: float
    """Initial currency exchange rate of short position order"""
    start_xrt_short_cost: float
    """Initial currency exchange rate (cost) of short position order"""
    avg_xrt_short: float
    """Average currency exchange rate of short position order"""
    avg_xrt_short_cost: float
    """Average currency exchange rate (cost) of short position order"""
    market_price: float
    """Current market price"""
    realized_pl: float
    """Realized profit/loss"""
    realized_pl_by_cost: float
    """Realized profit/loss by cost"""
    realized_pl_currency: float
    """Realized profit/loss (as Thai Baht)"""
    realized_pl_by_cost_currency: float
    """Realized profit/loss by cost (as Thai Baht)"""
    short_amount: float
    """Amount of short position order"""
    long_amount: float
    """Amount of long position order"""
    short_amount_by_cost: float
    """Amount by cost of short position order"""
    long_amount_by_cost: float
    """Amount by cost of long position order"""
    price_digit: int
    """Decimal point of Price value"""
    settle_digit: int
    """Decimal point of Settle value"""
    long_unrealize_pl: float
    """Unrealized profit/loss of long position order"""
    long_unrealize_pl_by_cost: float
    """Unrealized profit/loss of long position order by Cost"""
    long_percent_unrealize_pl: float
    """Unrealized profit/loss of long position order by Cost"""
    long_percent_unrealize_pl_by_cost: float
    """Unrealized profit/loss of long position in percent by Cost"""
    long_options_value: float
    """Long Options Value"""
    long_market_value: float
    """Long Market Value"""
    short_unrealize_pl: float
    """Unrealized profit/loss of short position order"""
    short_percent_unrealize_pl: float
    """Unrealized profit/loss of short position in percent"""
    short_unrealize_pl_by_cost: float
    """Unrealized profit/loss of short position order by Cost"""
    short_percent_unrealize_pl_by_cost: float
    """Unrealized profit/loss of short position in percent by Cost"""
    short_options_value: float
    """Short Options Value"""
    short_market_value: float
    """Short Market Value"""
    long_avg_price_thb: float
    """Long Average Price in THB"""
    short_avg_price_thb: float
    """Short Average Price in THB"""
    short_amount_currency: float
    long_amount_currency: float
    long_market_value_currency: float
    short_market_value_currency: float
    long_unrealize_pl_currency: float
    short_unrealize_pl_currency: float
    long_unrealized_pl_by_cost_currency: float
    short_unrealized_pl_by_cost_currency: float
    long_amount_by_cost_currency: float
    short_amount_by_cost_currency: float


@dataclass
class DerivativeTotalPortfolio(SettradeStruct):
    amount: float
    """Amount of short position order"""
    market_value: float
    """Market value of short position order"""
    amount_by_cost: float
    """Amount of short position order by cost"""
    unrealize_pl: float
    """Unrealized profit/loss (as Thai Baht)"""
    unrealize_pl_by_cost: float
    """Unrealized profit/loss by cost (as Thai Baht)"""
    realize_pl: float
    """Realized profit/loss (as Thai Baht)"""
    realize_pl_by_cost: float
    """Realized profit/loss by cost (as Thai Baht)"""
    percent_unrealize_pl: float
    """Percent unrealized profit/loss (as Thai Baht)"""
    percent_unrealize_pl_by_cost: float
    """Percent unrealized profit/loss by cost (as Thai Baht)"""
    options_value: float
    """Options Value"""


@dataclass
class DerivativeOrder(SettradeStruct):
    order_no: int
    """Order number"""
    tfx_order_no: str
    """TFEX order number (Pattern: orderbook-side-orderid)"""
    account_no: str
    """Account number"""
    entry_id: str
    """Entry Id (If the order placed by marketing representative)"""
    entry_time: str
    """Time of transaction sent to Settrade (yyyy-MM-dd'T'HH:mm:ss)"""
    trade_date: str
    """Trade date (formatted as yyyy-MM-dd)"""
    transaction_time: str
    """Time of transaction sent to TFEX (yyyy-MM-dd'T'HH:mm:ss)"""
    cancel_id: str  # Nullable field
    """Cancel Id (If the order canceled by marketing representative)"""
    cancel_time: str  # Nullable field
    """Cancel time (yyyy-MM-dd'T'HH:mm:ss)"""
    symbol: str
    """Symbol"""
    side: SIDE_TYPE
    """Order side:
    * `Long` - Buy
    * `Short` - Sell"""
    position: POSITION
    """Order position:
    * `Open` - Open Position
    * `Close` - Close Position
    * `Auto` - Auto Position (extra permission required)"""
    price_type: PRICE_TYPE
    """Price type:
    * `Limit` - Limit Order
    * `ATO` - At The Open (field price must be 0)
    * `MP-MTL` - Market To Limit Order (field price must be 0)
    * `MP-MKT` - Market Order (field price must be 0)"""
    price: float
    """Price"""
    qty: int
    """Volume (Balance volume + Matched volume + Cancelled volume)"""
    iceberg_vol: int
    """Iceberg Volume"""
    balance_qty: int
    """Balance volume"""
    match_qty: int
    """Matched volume"""
    cancel_qty: int
    """Cancelled volume"""
    validity: VALIDITY_TYPE
    """Order validity:
    * `Day` - Order will be available only on the order entry date
    * `FOK` - Fill or Kill
    * `IOC` - Immediate or Cancel
    * `Date` - GTD order will be available to a specific date
    * `Cancel` - GTC order will be available for a maximum of 254 days after the business date"""
    valid_to_date: str  # Nullable field
    """Valid to date (Format: yyyy-MM-dd) for validity type Date or Cancel (after TFEX accepts the order)"""
    is_stop_order_not_activate: str
    """Flag indicating if the stop order is waiting for activation"""
    trigger_condition: TRIGGER_CONDITION  # Nullable field
    """Trigger condition for stop order:
    * `ASK_OR_HIGHER` - Stop price >= Ask price (Condition type: Price Movement)
    * `ASK_OR_LOWER` - Stop price <= Ask price (Condition type: Price Movement)
    * `BID_OR_HIGHER` - Stop price >= Bid price (Condition type: Price Movement)
    * `BID_OR_LOWER` - Stop price <= Bid price (Condition type: Price Movement)
    * `LAST_PAID_OR_HIGHER` - Stop price >= Last price (Condition type: Price Movement)
    * `LAST_PAID_OR_LOWER` - Stop price <= Last price (Condition type: Price Movement)
    * `SESSION` - Stop order will trigger when the trading session changes"""
    trigger_symbol: str  # Nullable field
    """Trigger symbol for stop order"""
    trigger_price: float
    """Trigger price for stop order"""
    trigger_session: TRIGGER_SESSION  # Nullable field
    """Trigger session (required if triggerCondition = SESSION): 
    * 'Pre-Open1' - Pre Open before Morning Session and Day Session
    * 'Open1' - Morning Session
    * 'Day' - Day Session (for non-intermission product e.g. RSS, RSS3D)
    * 'Pre-Open2' - Pre Open before Afternoon Session
    * 'Open2' - Afternoon Session
    * 'Pre-Open0' - Pre Open before Night Session (for night session product e.g. GOLD, CURRENCY)
    * 'Open0' - Night Session (for night session product e.g. GOLD, CURRENCY)"""
    status: str
    """Order status (Abbreviation)"""
    show_status: str
    """Order status (For display)"""
    status_meaning: str
    """Order status meaning"""
    reject_code: int
    """Reject code"""
    reject_reason: str  # Nullable field
    """Description of rejectCode"""
    cpm: str  # Nullable field
    """Counter party member"""
    tr_type: str  # Nullable field
    """Trade report type"""
    terminal_type: str  # Nullable field
    """Terminal type"""
    version: int
    """Version of order status"""
    can_cancel: bool
    """Flag indicating whether the order is allowed to be cancelled"""
    can_change: bool
    """Flag indicating whether the order is allowed to be changed"""
    price_digit: int
    """Decimal point of Price value"""


@dataclass
class DerivativeTrade(SettradeStruct):
    broker_id: str
    """Broker Id"""
    order_no: int
    """Order number"""
    trade_date: str
    """Trade date (yyyy-MM-dd)"""
    entry_id: str
    """Entry Id (If the order placed by marketing representative)"""
    account_no: str
    """Account number"""
    trade_no: str
    """Trade number(Pattern : side-matchid)"""
    trade_id: int
    """Trade Id"""
    trade_time: str
    """Trade time (yyyy-MM-dd'T'HH:mm:ss)"""
    symbol: str
    """Symbol"""
    side: SIDE_TYPE
    """Order side:
    * `Long` - Buy
    * `Short` - Sell"""
    qty: int
    """Volume"""
    px: float
    """Price"""
    open_close: OPEN_CLOSE_TYPE
    """Order position:
    * `Open` - Open Position
    * `Close` - Close Position
    * `Auto` - Auto Position (extra permission required)"""
    status: STATUS_TYPE
    """Trade status:
    * `UNREGISTRATION` - Received trade from matching engine waiting confirmation from clearing system
    * `ACTIVE` - Received trade from matching engine and clearing system, can perform trade amendment
    * `RECTIFIED` - Rectified"""
    trade_type: TRADE_TYPE
    """Trade update type:
    * `NEW` - New
    * `REVERSING` - Reversing
    * `OVERTAKING` - Overtaking"""
    rectified_qty: int
    """Rectified volume"""
    multiplier: float
    """Multiplier"""
    currency: CURRENCY_TYPE
    """Currency:
    * `THB` - Thai Baht
    * `USD` - US Dollar"""
    ledger_date: str
    """Ledger date (yyyy-MM-dd)"""
    ledger_seq: int
    """Ledger sequence"""
    ledger_time: str
    """Ledger time (yyyy-MM-dd'T'HH:mm:ss)"""
    ref_ledger_date: str
    """Reference ledger date (yyyy-MM-dd)"""
    ref_ledger_seq: int
    """Reference ledger sequence"""
    reject_code: str
    """Reject code"""
    reject_reason: str
    """Reject reason"""


@dataclass
class CancelOrder(SettradeStruct):
    order_no: str
    """Order number"""
    error_response: Dict[str, Any]
    http_status: str
    """HTTP status"""
    http_status_code: int
    """HTTP status code"""
