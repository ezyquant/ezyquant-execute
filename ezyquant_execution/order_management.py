import pandas as pd
import logging
import time as t
from functools import cached_property, lru_cache
from typing import Any, Callable, Dict, List, Literal, Optional, TypeVar, Union

from settrade_v2.context import Context
from settrade_v2.user import Investor, MarketRep, _BaseUser
from ezyquant import EzyQuant 

logger = logging.getLogger(__name__)

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

class OrderManagement:
    def __init__(
        self,
        account_no: str,
        pin: Optional[str] = None,
    ):
        """Execute context.

        Parameters
        ----------
            Settrade user
        account_no : str
            Account number
        pin : Optional[str], optional
            PIN. Only for investor.
        """
        self.settrade_user = self
        self.account_no = account_no
        self.pin = pin
        self.ezyquant = EzyQuant(api_key="your_api_key")  # Initialize EzyQuant

    def get_active_orders(self) -> pd.DataFrame:
        """
        Get all active orders
        
        Returns:
            pd.DataFrame: DataFrame containing active orders
        """
        try:
            orders = self.ezyquant.get_orders(status='ACTIVE')  # Use EzyQuant
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
                result = self.ezyquant.cancel_order(order['order_id'])  # Use EzyQuant
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
                result = self.ezyquant.cancel_order(order['order_id'])  # Use EzyQuant
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
                result = self.ezyquant.cancel_order(order['order_id'])  # Use EzyQuant
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
                result = self.ezyquant.cancel_order(order['order_id'])  # Use EzyQuant
                if result.get('status') == 'SUCCESS':
                    cancelled_orders.append(order['order_id'])
                    
            return cancelled_orders
        except Exception as e:
            print(f"Error cancelling orders above price: {str(e)}")
            return cancelled_orders
