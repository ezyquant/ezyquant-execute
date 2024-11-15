import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ezyquant_execution')))

import pytest
from typing import  Optional
from settrade_v2.user import Investor
from ezyquant_execution.order_management import OrderManagement

def test_order_management(settrade_user, account_no: str, pin: Optional[str] = None):
    """
    Test all order cancellation functions
    """
    # Initialize order manager
    order_manager = OrderManagement(settrade_user=settrade_user, account_no=account_no, pin=pin)
       
    # Test cancel bid orders
    cancelled_bids = order_manager.cancel_bid_orders()
    print(f"Cancelled bid orders: {cancelled_bids}")
    
    # Test cancel ask orders
    cancelled_asks = order_manager.cancel_ask_orders()
    print(f"Cancelled ask orders: {cancelled_asks}")
    
    # Test cancel orders below price
    test_price_below = 50.0
    cancelled_below = order_manager.cancel_orders_below_price(test_price_below)
    print(f"Cancelled orders below {test_price_below}: {cancelled_below}")
    
    # Test cancel orders above price
    test_price_above = 100.0
    cancelled_above = order_manager.cancel_orders_above_price(test_price_above)
    print(f"Cancelled orders above {test_price_above}: {cancelled_above}")

if __name__ == "__main__":
    settrade_user = Investor(
        app_id="HlRY0wfHtC3pDhf8",
        app_secret="AJvakgiUdfV92WVmFKS/NoqdD7cEWOrGQ9QHr8pdY1F5",
        broker_id="SANDBOX",
        app_code="SANDBOX",
        is_auto_queue=False
    )
    
    account_no = "ezyquant-E"
    pin = "000000"

    test_order_management(settrade_user, account_no, pin)
    print("All tests passed!")