from settrade_v2.realtime import RealtimeDataConnection

from ezyquant_execution.realtime import BidOfferSubscriber, PriceInfoSubscriber


def test_bid_offer_subscriber(stt_rt: RealtimeDataConnection):
    sub = BidOfferSubscriber(symbol="AOT", rt_conn=stt_rt)

    result = sub.data

    print(result)


def test_price_info_subscriber(stt_rt: RealtimeDataConnection):
    sub = PriceInfoSubscriber(symbol="AOT", rt_conn=stt_rt)

    result = sub.data

    print(result)
