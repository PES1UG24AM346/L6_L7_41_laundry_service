import os
import sys
from pathlib import Path
import pytest

# Ensure the module directory is in sys.path regardless of execution working directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from laundry_service import (
    INCLUDED_KG,
    extra_weight_charge,
    order_acceptable,
    dropoff_status,
)


# =======================================================================
# Branch Coverage Tests: extra_weight_charge
# =======================================================================

class TestExtraWeightChargeBranches:
    """Exercises all decision branches and boolean sub-expressions in extra_weight_charge."""

    def test_branch_garment_type_not_in_included_kg_true(self):
        """Branch: garment_type not in INCLUDED_KG -> True (raises ValueError)."""
        with pytest.raises(ValueError, match="unknown garment type"):
            extra_weight_charge("silk", 5, "standard", False)

    def test_branch_garment_type_not_in_included_kg_false(self):
        """Branch: garment_type not in INCLUDED_KG -> False (valid types)."""
        # Valid garment types without extra weight return 0
        assert extra_weight_charge("regular", 5, "standard", False) == 0
        assert extra_weight_charge("delicate", 3, "standard", False) == 0
        assert extra_weight_charge("bedding", 8, "standard", False) == 0

    def test_branch_weight_kg_negative_true(self):
        """Branch: weight_kg < 0 -> True (raises ValueError)."""
        with pytest.raises(ValueError, match="invalid weight"):
            extra_weight_charge("regular", -0.5, "standard", False)

    def test_branch_weight_kg_negative_false_zero_weight(self):
        """Branch: weight_kg < 0 -> False with boundary weight 0 (returns 0)."""
        assert extra_weight_charge("regular", 0, "standard", False) == 0

    def test_branch_membership_regular_true_true(self):
        """
        Decision: is_member and garment_type != 'bedding' -> True.
        Garment: regular (5kg) -> member gets 5 + 2 = 7kg included.
        """
        # At exactly 7kg: extra = 0 -> 0 charge
        assert extra_weight_charge("regular", 7, "standard", True) == 0
        # At 9kg: extra = 2 -> 2 * 30 = 60 charge
        assert extra_weight_charge("regular", 9, "standard", True) == 60

    def test_branch_membership_delicate_true_true(self):
        """
        Decision: is_member and garment_type != 'bedding' -> True.
        Garment: delicate (3kg) -> member gets 3 + 2 = 5kg included.
        """
        # At 7kg: extra = 2 -> 2 * 30 = 60 charge
        assert extra_weight_charge("delicate", 7, "standard", True) == 60

    def test_branch_membership_bedding_true_false(self):
        """
        Decision: is_member and garment_type != 'bedding' -> False (second condition False).
        Garment: bedding (8kg) -> member receives NO bonus (included remains 8kg).
        """
        # At 8kg: extra = 0 -> 0 charge
        assert extra_weight_charge("bedding", 8, "standard", True) == 0
        # At 10kg: extra = 2 -> 2 * 30 = 60 charge
        assert extra_weight_charge("bedding", 10, "standard", True) == 60

    def test_branch_membership_non_member_false(self):
        """
        Decision: is_member and garment_type != 'bedding' -> False (first condition False).
        Non-member regular: included remains 5kg.
        """
        # At 5kg: extra = 0 -> 0 charge
        assert extra_weight_charge("regular", 5, "standard", False) == 0
        # At 7kg: extra = 2 -> 2 * 30 = 60 charge
        assert extra_weight_charge("regular", 7, "standard", False) == 60

    def test_branch_extra_weight_lte_zero_true(self):
        """
        Branch: extra <= 0 -> True.
        Evaluates both extra < 0 and extra == 0.
        """
        # extra < 0: weight 3kg for regular (included 5) -> extra = -2 -> returns 0
        assert extra_weight_charge("regular", 3, "standard", False) == 0
        # extra == 0: weight 5kg for regular (included 5) -> extra = 0 -> returns 0
        assert extra_weight_charge("regular", 5, "standard", False) == 0

    def test_branch_extra_weight_lte_zero_false(self):
        """Branch: extra <= 0 -> False (extra > 0 proceeds to rate calculation)."""
        # weight 6kg for regular (included 5) -> extra = 1 -> charge = 1 * 30 = 30
        assert extra_weight_charge("regular", 6, "standard", False) == 30

    def test_branch_speed_standard_true(self):
        """Branch: speed == 'standard' -> True (rate = 30)."""
        # extra = 2, extra <= 10 -> rate = 30 -> charge = 60
        assert extra_weight_charge("regular", 7, "standard", False) == 60

    def test_branch_speed_standard_false(self):
        """Branch: speed == 'standard' -> False (rate = 50)."""
        # extra = 2, extra <= 10, speed = 'express' -> rate = 50 -> charge = 100
        assert extra_weight_charge("regular", 7, "express", False) == 100
        # extra = 2, extra <= 10, speed = 'overnight' -> rate = 50 -> charge = 100
        assert extra_weight_charge("regular", 7, "overnight", False) == 100

    def test_branch_extra_gt_10_false_at_boundary(self):
        """
        Branch: extra > 10 -> False.
        Boundary testing: extra == 10 (no +15 surcharge applied).
        """
        # extra = 10 (weight 15 - 5), standard speed -> rate = 30 -> charge = 300
        assert extra_weight_charge("regular", 15, "standard", False) == 300
        # extra = 10 (weight 15 - 5), express speed -> rate = 50 -> charge = 500
        assert extra_weight_charge("regular", 15, "express", False) == 500

    def test_branch_extra_gt_10_true_speed_express_true(self):
        """
        Branch: extra > 10 -> True AND speed == 'express' -> True.
        rate = 50 + 15 + 10 = 75.
        """
        # extra = 11 (weight 16 - 5), express speed -> rate = 75 -> charge = 11 * 75 = 825
        assert extra_weight_charge("regular", 16, "express", False) == 825

    def test_branch_extra_gt_10_true_speed_express_false_standard(self):
        """
        Branch: extra > 10 -> True AND speed == 'express' -> False (speed is 'standard').
        rate = 30 + 15 = 45 (express surcharge +10 skipped).
        """
        # extra = 11 (weight 16 - 5), standard speed -> rate = 45 -> charge = 11 * 45 = 495
        assert extra_weight_charge("regular", 16, "standard", False) == 495

    def test_branch_extra_gt_10_true_speed_express_false_other_speed(self):
        """
        Branch: extra > 10 -> True AND speed == 'express' -> False (speed is non-standard other).
        rate = 50 + 15 = 65 (express surcharge +10 skipped).
        """
        # extra = 11 (weight 16 - 5), overnight speed -> rate = 65 -> charge = 11 * 65 = 715
        assert extra_weight_charge("regular", 16, "overnight", False) == 715


# =======================================================================
# Branch Coverage Tests: order_acceptable
# =======================================================================

class TestOrderAcceptableBranches:
    """Exercises all decision branches and boundary conditions in order_acceptable."""

    def test_branch_is_delicate_true_items_lte_5(self):
        """
        Branch: is_delicate -> True AND items <= 5 -> True.
        Accepts delicate orders with up to 5 items, regardless of weight.
        """
        # Boundary: items == 5
        assert order_acceptable(10, 5, True) is True
        # Below boundary: items == 1, heavy weight (bypasses weight check)
        assert order_acceptable(50, 1, True) is True

    def test_branch_is_delicate_true_items_gt_5(self):
        """
        Branch: is_delicate -> True AND items <= 5 -> False.
        Rejects delicate orders with more than 5 items.
        """
        # Boundary: items == 6
        assert order_acceptable(5, 6, True) is False

    def test_branch_is_delicate_false_weight_gt_25_true(self):
        """
        Branch: is_delicate -> False AND weight_kg > 25 -> True.
        Rejects non-delicate orders exceeding 25 kg.
        """
        # Boundary: weight_kg == 25.1
        assert order_acceptable(25.1, 10, False) is False
        assert order_acceptable(30, 5, False) is False

    def test_branch_is_delicate_false_weight_lte_25_items_lte_40(self):
        """
        Branch: is_delicate -> False, weight_kg > 25 -> False, items <= 40 -> True.
        Accepts non-delicate orders with weight <= 25 kg and items <= 40.
        """
        # Boundary: weight_kg == 25, items == 40
        assert order_acceptable(25, 40, False) is True
        # Within limits
        assert order_acceptable(15, 20, False) is True

    def test_branch_is_delicate_false_weight_lte_25_items_gt_40(self):
        """
        Branch: is_delicate -> False, weight_kg > 25 -> False, items <= 40 -> False.
        Rejects non-delicate orders with items > 40 even if weight <= 25 kg.
        """
        # Boundary: weight_kg == 25, items == 41
        assert order_acceptable(25, 41, False) is False
        assert order_acceptable(10, 50, False) is False


# =======================================================================
# Branch Coverage Tests: dropoff_status
# =======================================================================

class TestDropoffStatusBranches:
    """Exercises all decision branches, cutoff combinations, and status outcomes in dropoff_status."""

    def test_combination_no_bedding_standard(self):
        """
        Combination: has_bedding=False, is_express=False -> cutoff = 60.
        Late threshold: 60 - 20 = 40.
        """
        # minutes >= 60 -> accepted (boundary 60, and above 75)
        assert dropoff_status(60, False, False) == "accepted"
        assert dropoff_status(75, False, False) == "accepted"
        # 40 <= minutes < 60 -> late (boundary 59, and lower boundary 40)
        assert dropoff_status(59, False, False) == "late"
        assert dropoff_status(40, False, False) == "late"
        # minutes < 40 -> rejected (boundary 39, and 0)
        assert dropoff_status(39, False, False) == "rejected"
        assert dropoff_status(0, False, False) == "rejected"

    def test_combination_has_bedding_standard(self):
        """
        Combination: has_bedding=True, is_express=False -> cutoff = 90.
        Late threshold: 90 - 20 = 70.
        """
        # minutes >= 90 -> accepted
        assert dropoff_status(90, True, False) == "accepted"
        # 70 <= minutes < 90 -> late
        assert dropoff_status(89, True, False) == "late"
        assert dropoff_status(70, True, False) == "late"
        # minutes < 70 -> rejected
        assert dropoff_status(69, True, False) == "rejected"

    def test_combination_no_bedding_express(self):
        """
        Combination: has_bedding=False, is_express=True -> cutoff = 60 + 30 = 90.
        Late threshold: 90 - 20 = 70.
        """
        # minutes >= 90 -> accepted
        assert dropoff_status(90, False, True) == "accepted"
        # 70 <= minutes < 90 -> late
        assert dropoff_status(70, False, True) == "late"
        # minutes < 70 -> rejected
        assert dropoff_status(69, False, True) == "rejected"

    def test_combination_has_bedding_express(self):
        """
        Combination: has_bedding=True, is_express=True -> cutoff = 90 + 30 = 120.
        Late threshold: 120 - 20 = 100.
        """
        # minutes >= 120 -> accepted
        assert dropoff_status(120, True, True) == "accepted"
        assert dropoff_status(150, True, True) == "accepted"
        # 100 <= minutes < 120 -> late
        assert dropoff_status(119, True, True) == "late"
        assert dropoff_status(100, True, True) == "late"
        # minutes < 100 -> rejected
        assert dropoff_status(99, True, True) == "rejected"
        assert dropoff_status(30, True, True) == "rejected"
