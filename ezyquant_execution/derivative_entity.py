import inspect
from dataclasses import dataclass
from typing import List, Literal

from . import utils

SIDE_TYPE = Literal["Long", "Short"]
OPEN_CLOSE_TYPE = Literal["AUTO", "OPEN", "CLOSE"]
STATUS_TYPE = Literal["UNREGISTRATION", "ACTIVE", "RECTIFIED"]
TRADE_TYPE = Literal["NEW", "REVERSING", "OVERTAKING"]
CURRENCY_TYPE = Literal["THB", "USD"]


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
