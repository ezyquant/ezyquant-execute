from threading import Event, Timer
from typing import Callable, Optional

from settrade_v2.realtime import RealtimeDataConnection, Subscriber

from .entity import BidOffer, PriceInfo


class SettradeSubscriber:
    def __init__(self, function: Callable[..., Subscriber], *args, **kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs

        self._data: dict = {}
        self._error: Optional[Exception] = None

        self._event: Event = Event()

        self._subscriber = self.function(
            on_message=self._on_message, *self.args, **self.kwargs
        )
        self._subscriber.start()
        # Stop after 12 hours
        timer = Timer(12 * 60 * 60, self._subscriber.stop)
        timer.daemon = True
        timer.start()

        # wait for first data to be received
        if not self._event.wait(timeout=30):
            raise ConnectionError("No data received yet")

    @property
    def data(self) -> dict:
        if self._error:
            raise self._error
        return self._data

    def _on_message(self, message):
        self._event.set()
        if message["is_success"]:
            self._data = message["data"]
            self._error = None
        else:
            self._error = ConnectionError(message["message"])
            raise self._error


class BidOfferSubscriber(SettradeSubscriber):
    def __init__(self, symbol: str, rt_conn: RealtimeDataConnection):
        super().__init__(rt_conn.subscribe_bid_offer, symbol=symbol)

    @property
    def data(self) -> BidOffer:
        return BidOffer.from_dict(super().data)


class PriceInfoSubscriber(SettradeSubscriber):
    def __init__(self, symbol: str, rt_conn: RealtimeDataConnection):
        super().__init__(rt_conn.subscribe_price_info, symbol=symbol)

    @property
    def data(self) -> PriceInfo:
        return PriceInfo.from_camel_dict(super().data)
