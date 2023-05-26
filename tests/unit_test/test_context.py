from dataclasses import dataclass
from typing import Callable
from unittest.mock import ANY

import pytest

from ezyquant_execution.context import ExecuteContext, ExecuteContextSymbol

SYMBOL = "AOT"


@pytest.fixture
def ctx():
    return ExecuteContextSymbol(
        settrade_user=ANY,
        account_no=ANY,
        symbol=SYMBOL,
    )


@dataclass
class TestStruct:
    id: int
    symbol: str


@pytest.mark.parametrize(
    ("l", "condition", "expected"),
    [
        # Test empty list
        ([], lambda x: True, []),
        ([], lambda x: False, []),
        # Test list with one element
        (
            [TestStruct(id=1, symbol=SYMBOL)],
            lambda x: True,
            [TestStruct(id=1, symbol=SYMBOL)],
        ),
        ([TestStruct(id=1, symbol="BBL")], lambda x: True, []),
        # Test condition
        (
            [TestStruct(id=1, symbol=SYMBOL)],
            lambda x: x.id == 1,
            [TestStruct(id=1, symbol=SYMBOL)],
        ),
        ([TestStruct(id=1, symbol="BBL")], lambda x: x.id == 1, []),
    ],
)
def test_filter_list(ctx: ExecuteContext, l: list, condition: Callable, expected: list):
    result = ctx._filter_list(l, condition=condition)
    assert result == expected
