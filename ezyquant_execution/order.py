import pandas as pd
import logging
import time as t
from datetime import datetime
from functools import cached_property, lru_cache
from typing import Any, Callable, Dict, List, Literal, Optional, TypeVar, Union

from settrade_v2.context import Context
# from settrade_v2.equity import InvestorEquity, MarketRepEquity
# from settrade_v2.market import MarketData
# from settrade_v2.realtime import RealtimeDataConnection
from settrade_v2.user import Investor, MarketRep, _BaseUser

logger = logging.getLogger(__name__)

# Override _BaseUser.RealtimeDataConnection
# because subscribe will error if init RealtimeDataConnection more than once
# Can remove this line if this issue is fixed
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

class Order:
    # def __init__(self, settrade_api_key: str):
    #     """
    #     Initialize OrderCancellation with Settrade API credentials
        
    #     Args:
    #         settrade_api_key (str): Your Settrade API key
    #     """
    #     self.api = SettradePythonAPI(api_key=settrade_api_key)

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

    def get_active_orders(self) -> pd.DataFrame:
        """
        Get all active orders
        
        Returns:
            pd.DataFrame: DataFrame containing active orders
        """
        try:
            orders = self.api.get_orders(status='ACTIVE')
            return pd.DataFrame(orders)
        except Exception as e:
            print(f"Error getting active orders: {str(e)}")
            return pd.DataFrame()

    def cancel_bid_orders(self) -> List[str]:
        """
        Cancel all bid (buy) orders
        
        Returns:
            List[str]: List of cancelled order IDs
        """
        cancelled_orders = []
        try:
            active_orders = self.get_active_orders()
            bid_orders = active_orders[active_orders['side'] == 'BUY']
            
            for _, order in bid_orders.iterrows():
                result = self.api.cancel_order(order['order_id'])
                if result.get('status') == 'SUCCESS':
                    cancelled_orders.append(order['order_id'])
                    
            return cancelled_orders
        except Exception as e:
            print(f"Error cancelling bid orders: {str(e)}")
            return cancelled_orders

    def cancel_ask_orders(self) -> List[str]:
        """
        Cancel all ask (sell) orders
        
        Returns:
            List[str]: List of cancelled order IDs
        """
        cancelled_orders = []
        try:
            active_orders = self.get_active_orders()
            ask_orders = active_orders[active_orders['side'] == 'SELL']
            
            for _, order in ask_orders.iterrows():
                result = self.api.cancel_order(order['order_id'])
                if result.get('status') == 'SUCCESS':
                    cancelled_orders.append(order['order_id'])
                    
            return cancelled_orders
        except Exception as e:
            print(f"Error cancelling ask orders: {str(e)}")
            return cancelled_orders

    def cancel_orders_below_price(self, price: float) -> List[str]:
        """
        Cancel all orders below specified price
        
        Args:
            price (float): Price threshold
            
        Returns:
            List[str]: List of cancelled order IDs
        """
        cancelled_orders = []
        try:
            active_orders = self.get_active_orders()
            below_price_orders = active_orders[active_orders['price'] < price]
            
            for _, order in below_price_orders.iterrows():
                result = self.api.cancel_order(order['order_id'])
                if result.get('status') == 'SUCCESS':
                    cancelled_orders.append(order['order_id'])
                    
            return cancelled_orders
        except Exception as e:
            print(f"Error cancelling orders below price: {str(e)}")
            return cancelled_orders

    def cancel_orders_above_price(self, price: float) -> List[str]:
        """
        Cancel all orders above specified price
        
        Args:
            price (float): Price threshold
            
        Returns:
            List[str]: List of cancelled order IDs
        """
        cancelled_orders = []
        try:
            active_orders = self.get_active_orders()
            above_price_orders = active_orders[active_orders['price'] > price]
            
            for _, order in above_price_orders.iterrows():
                result = self.api.cancel_order(order['order_id'])
                if result.get('status') == 'SUCCESS':
                    cancelled_orders.append(order['order_id'])
                    
            return cancelled_orders
        except Exception as e:
            print(f"Error cancelling orders above price: {str(e)}")
            return cancelled_orders

# Test functions
def test_order_cancellation():
    """
    Test all order cancellation functions
    """
    # Initialize with your API key
    # api_key = "thoZEaWEdA1zACUC"
    order_manager = Order()
    
    # Test cancel bid orders
    print("\nTesting cancel bid orders...")
    cancelled_bids = order_manager.cancel_bid_orders()
    print(f"Cancelled bid orders: {cancelled_bids}")
    
    # Test cancel ask orders
    print("\nTesting cancel ask orders...")
    cancelled_asks = order_manager.cancel_ask_orders()
    print(f"Cancelled ask orders: {cancelled_asks}")
    
    # Test cancel orders below price
    print("\nTesting cancel orders below price...")
    test_price_below = 50.0
    cancelled_below = order_manager.cancel_orders_below_price(test_price_below)
    print(f"Cancelled orders below {test_price_below}: {cancelled_below}")
    
    # Test cancel orders above price
    print("\nTesting cancel orders above price...")
    test_price_above = 100.0
    cancelled_above = order_manager.cancel_orders_above_price(test_price_above)
    print(f"Cancelled orders above {test_price_above}: {cancelled_above}")

if __name__ == "__main__":
    test_order_cancellation()

  