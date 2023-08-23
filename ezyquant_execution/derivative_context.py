from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from settrade_v2.derivatives import InvestorDerivatives, MarketRepDerivatives
from settrade_v2.user import Investor, MarketRep

from .derivative_entity import (
    BaseAccountDerivativeInfo,
    DerivativePortfolioResponse,
    DerivativeTrade,
)

T = TypeVar("T")


class ExecuteDerivativeContext:
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

    """
    Settrade SDK functions
    """

    @property
    def _acc_no_kw(self) -> dict:
        return (
            {"account_no": self.account_no}
            if isinstance(self.settrade_user, MarketRep)
            else {}
        )

    @property
    def _settrade_derivative(self) -> Union[InvestorDerivatives, MarketRepDerivatives]:
        kw = (
            {"account_no": self.account_no}
            if isinstance(self.settrade_user, Investor)
            else {}
        )
        return self.settrade_user.Derivatives(**kw)

    def get_account_info(self) -> BaseAccountDerivativeInfo:
        """Get derivative account info."""
        res = self._settrade_derivative.get_account_info(**self._acc_no_kw)
        return BaseAccountDerivativeInfo.from_camel_dict(res)

    def get_portfolios(self) -> DerivativePortfolioResponse:
        """Get portfolios."""
        res: Dict[str, Any] = self._settrade_derivative.get_portfolios(**self._acc_no_kw)  # type: ignore
        return DerivativePortfolioResponse.from_camel_dict(res)

    def get_trades(self, condition: Callable = lambda _: True) -> List[DerivativeTrade]:
        """Get trades."""
        res = self._settrade_derivative.get_trades(**self._acc_no_kw)
        out = [DerivativeTrade.from_camel_dict(i) for i in res]
        out = self._filter_list(out, condition)
        return out

    """
    Override functions
    """

    def _filter_list(self, l: List[T], condition: Callable = lambda _: True) -> List[T]:
        """Filter list by symbol and condition."""
        return [i for i in l if condition(i)]
