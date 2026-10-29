import os
import sys
from pathlib import Path
import pytest

# Ensure the module directory is in sys.path regardless of execution working directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from laundry_service import extra_weight_charge, order_acceptable, dropoff_status


# Starter example test cases:
def test_within_included_weight():
    assert extra_weight_charge("regular", 4, "standard", False) == 0


def test_order_acceptable():
    assert order_acceptable(10, 20, False) is True


# =======================================================================
# Additional test cases to achieve 90-100% line and branch coverage
# =======================================================================

def test_extra_weight_charge_invalid_garment():
    with pytest.raises(ValueError, match="unknown garment type"):
        extra_weight_charge("silk", 10, "standard", False)


def test_extra_weight_charge_negative_weight():
    with pytest.raises(ValueError, match="invalid weight"):
        extra_weight_charge("regular", -1, "standard", False)


def test_extra_weight_charge_member_bonus():
    # regular: 5 + 2 = 7kg included. weight 6kg -> extra = -1 <= 0 -> 0
    assert extra_weight_charge("regular", 6, "standard", True) == 0
    # delicate: 3 + 2 = 5kg included. weight 7kg -> extra = 2 -> 2 * 30 = 60
    assert extra_weight_charge("delicate", 7, "standard", True) == 60


def test_extra_weight_charge_member_bedding_no_bonus():
    # bedding gets no membership bonus: included stays 8kg. weight 10kg -> extra = 2 -> 60
    assert extra_weight_charge("bedding", 10, "standard", True) == 60


def test_extra_weight_charge_rates_and_tiers():
    # standard speed under 10kg extra: rate = 30
    assert extra_weight_charge("regular", 8, "standard", False) == 90
    # non-standard speed (express) under 10kg extra: rate = 50
    assert extra_weight_charge("regular", 8, "express", False) == 150
    # standard speed over 10kg extra: rate = 30 + 15 = 45 -> 13 * 45 = 585
    assert extra_weight_charge("regular", 18, "standard", False) == 585
    # express speed over 10kg extra: rate = 50 + 15 + 10 = 75 -> 13 * 75 = 975
    assert extra_weight_charge("regular", 18, "express", False) == 975
    # non-standard, non-express over 10kg extra: rate = 50 + 15 = 65 -> 13 * 65 = 845
    assert extra_weight_charge("regular", 18, "economy", False) == 845


def test_order_acceptable_delicate():
    # delicate order item limit is 5
    assert order_acceptable(10, 5, True) is True
    assert order_acceptable(10, 6, True) is False


def test_order_acceptable_non_delicate():
    # weight limit is 25kg
    assert order_acceptable(26, 10, False) is False
    # items limit is 40
    assert order_acceptable(25, 40, False) is True
    assert order_acceptable(25, 41, False) is False


def test_dropoff_status_all_scenarios():
    # No bedding, standard: cutoff 60, late window [40, 60)
    assert dropoff_status(60, False, False) == "accepted"
    assert dropoff_status(50, False, False) == "late"
    assert dropoff_status(39, False, False) == "rejected"

    # Bedding, standard: cutoff 90, late window [70, 90)
    assert dropoff_status(90, True, False) == "accepted"
    assert dropoff_status(75, True, False) == "late"
    assert dropoff_status(60, True, False) == "rejected"

    # No bedding, express: cutoff 90, late window [70, 90)
    assert dropoff_status(90, False, True) == "accepted"
    assert dropoff_status(70, False, True) == "late"
    assert dropoff_status(69, False, True) == "rejected"

    # Bedding, express: cutoff 120, late window [100, 120)
    assert dropoff_status(120, True, True) == "accepted"
    assert dropoff_status(100, True, True) == "late"
    assert dropoff_status(99, True, True) == "rejected"
