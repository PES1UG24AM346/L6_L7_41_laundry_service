import pytest
from laundry_service import extra_weight_charge, order_acceptable, dropoff_status

# Example test cases:
def test_within_included_weight():
    assert extra_weight_charge("regular", 4, "standard", False) == 0

def test_order_acceptable():
    assert order_acceptable(10, 20, False) is True

# Write the rest of the test cases so that the code is 90-100% covered.
