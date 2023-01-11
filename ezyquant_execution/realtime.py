from functools import lru_cache
from threading import Event
from typing import Optional

from settrade_v2.realtime import RealtimeDataConnection

from .entity import BidOffer


class BidOfferSubscriber:
    def __init__(self, symbol: str, rt_conn: RealtimeDataConnection):
        self.symbol = symbol
        self.rt_conn = rt_conn

        self._bid_offer: Optional[BidOffer] = None
        self._event: Event = Event()

    @property
    def bid_offer(self) -> BidOffer:
        self._subscribe()  # subscribe if not subscribed yet (lru_cache)
        self._event.wait()  # wait for first update
        assert self._bid_offer is not None
        return self._bid_offer

    @property
    def best_bid_price(self) -> float:
        return self.bid_offer.best_bid_price

    @property
    def best_bid_volume(self) -> int:
        return self.bid_offer.best_bid_volume

    @property
    def best_ask_price(self) -> float:
        return self.bid_offer.best_ask_price

    @property
    def best_ask_volume(self) -> int:
        return self.bid_offer.best_ask_volume

    @lru_cache(maxsize=1)
    def _subscribe(self):
        self.rt_conn.subscribe_bid_offer(
            symbol=self.symbol, on_message=self._on_bid_offer_update
        ).start()

    def _on_bid_offer_update(self, message):
        if message["is_success"]:
            self._bid_offer = BidOffer.from_dict(message["data"])
            self._event.set()
        else:
            raise ConnectionError(message["message"])
