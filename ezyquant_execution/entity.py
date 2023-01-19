from dataclasses import dataclass
from typing import List

import pandas as pd

from . import utils

SIDE_BUY = "Buy"
SIDE_SELL = "Sell"

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


class SettradeStruct:
    @classmethod
    def from_camel_dict(cls, dct: dict):
        return cls(**{utils.camel_to_snake(k): v for k, v in dct.items()})


@dataclass
class EquityPortfolio(SettradeStruct):
    symbol: str
    flag: str
    nvdr_flag: str
    market_price: float
    amount: float
    marketdescription: float
    market_value: float
    profit: float
    percent_profit: float
    realize_profit: float
    start_volume: float
    current_volume: float
    actual_volume: float
    start_price: float
    average_price: float
    show_na: bool
    port_flag: str
    margin_rate: float
    liabilities: float
    commission_rate: float
    vat_rate: float


@dataclass
class EquityOrder(SettradeStruct):
    enter_id: str
    account_no: str
    order_no: str
    set_order_no: str
    symbol: str
    trade_date: str
    trade_time: str
    entry_time: str
    side: str
    price_type: str
    price: float
    vol: int
    iceberg_vol: int
    validity: str
    order_type: str
    matched: int
    balance: int
    cancelled: int
    status: str
    show_order_status: str
    show_order_status_meaning: str
    reject_code: int
    reject_reason: str
    cancel_id: str
    cancel_time: str
    version: int
    nvdr_flag: str
    can_change_account: bool
    can_change_trustee_id: bool
    can_change_price_vol: bool
    can_cancel: bool
    counter_party_member: str
    trade_report_type: str
    trade_report: bool
    terminal_type: str
    valid_till_date: str


@dataclass
class EquityTrade(SettradeStruct):
    account_no: str
    broker_id: str
    brokerage_fee: float
    clearing_fee: float
    deal_no: str
    entry_id: str
    order_no: str
    px: float
    qty: int
    side: str
    symbol: str
    trade_date: str
    trade_no: str
    trade_time: str
    trading_fee: float
    trustee_id: str
