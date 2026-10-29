import os
import sys
from pathlib import Path
import pytest

# Ensure the module directory is in sys.path regardless of execution working directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from laundry_service import extra_weight_charge, order_acceptable, dropoff_status


# =======================================================================
# Line Coverage Tests: extra_weight_charge
# =======================================================================

def test_extra_weight_charge_invalid_garment_type():
    """Covers line raising ValueError for unknown garment type."""
    with pytest.raises(ValueError, match="unknown garment type"):
        extra_weight_charge("leather", 10, "standard", False)


def test_extra_weight_charge_negative_weight():
    """Covers line raising ValueError for negative weight."""
    with pytest.raises(ValueError, match="invalid weight"):
        extra_weight_charge("regular", -1, "standard", False)


def test_extra_weight_charge_member_within_included_weight():
    """
    Covers lines:
    - included += 2 (member bonus)
    - return 0 (when extra <= 0)
    """
    # Member with regular garment: included = 5 + 2 = 7; weight = 6 -> extra = -1 <= 0
    assert extra_weight_charge("regular", 6, "standard", True) == 0


def test_extra_weight_charge_standard_rate():
    """
    Covers lines:
    - speed == 'standard' -> rate = 30
    - return extra * rate
    """
    # Non-member regular garment: included = 5; weight = 8 -> extra = 3 <= 10
    # speed is standard -> rate = 30 -> charge = 3 * 30 = 90
    assert extra_weight_charge("regular", 8, "standard", False) == 90


def test_extra_weight_charge_express_over_10kg_extra():
    """
    Covers lines:
    - non-standard speed -> rate = 50
    - extra > 10 -> rate = rate + 15
    - speed == 'express' -> rate += 10
    """
    # Non-member regular: included = 5; weight = 18 -> extra = 13 (> 10)
    # speed is express -> rate = 50 + 15 + 10 = 75 -> charge = 13 * 75 = 975
    assert extra_weight_charge("regular", 18, "express", False) == 975


# =======================================================================
# Line Coverage Tests: order_acceptable
# =======================================================================

def test_order_acceptable_delicate_order():
    """Covers line: return items <= 5 when is_delicate is True."""
    assert order_acceptable(10, 4, True) is True


def test_order_acceptable_overweight_order():
    """Covers line: return False when weight_kg > 25."""
    assert order_acceptable(30, 10, False) is False


def test_order_acceptable_regular_order():
    """Covers line: return items <= 40 when not delicate and weight_kg <= 25."""
    assert order_acceptable(20, 25, False) is True


# =======================================================================
# Line Coverage Tests: dropoff_status
# =======================================================================

def test_dropoff_status_accepted_bedding_express():
    """
    Covers lines:
    - has_bedding -> cutoff = 90
    - is_express -> cutoff += 30 (cutoff becomes 120)
    - minutes_before_closing >= cutoff -> return 'accepted'
    """
    assert dropoff_status(130, True, True) == "accepted"


def test_dropoff_status_late_no_bedding_standard():
    """
    Covers lines:
    - else (no bedding) -> cutoff = 60
    - elif minutes_before_closing >= cutoff - 20 -> return 'late'
    """
    # cutoff = 60, cutoff - 20 = 40; 50 is in [40, 60)
    assert dropoff_status(50, False, False) == "late"


def test_dropoff_status_rejected():
    """Covers line: return 'rejected' when minutes < cutoff - 20."""
    # cutoff = 60, cutoff - 20 = 40; 20 is < 40
    assert dropoff_status(20, False, False) == "rejected"
