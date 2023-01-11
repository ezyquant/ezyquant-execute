from settrade_v2.realtime import RealtimeDataConnection

from ezyquant_execution.realtime import BidOfferSubscriber


def test_bid_offer_subscriber(stt_rt: RealtimeDataConnection):
    sub = BidOfferSubscriber(symbol="AOT", rt_conn=stt_rt)

    result = sub.bid_offer

    print(result)
