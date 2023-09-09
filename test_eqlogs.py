import pytest
from eqlogs import Money
from unittest.mock import patch
import unittest

class TestMoney:
    def test_init(self):
        nothing="0 platinum, 0 gold, 0 silver and 0 copper"
        much="2 platinum, 6 gold, 4 silver and 9 copper"
        zeroint=Money(0)
        zerostr=Money(nothing)
        some_money=Money(much)

        print(f"debug: {str(zeroint)},{str(some_money)}")
        assert str(zeroint) == str(zerostr)
        assert str(zeroint) == nothing 
        assert str(some_money) == much
        assert int(zerostr) == 0
        assert int(some_money) == 2649
