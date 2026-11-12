from hypothesis import given, strategies as st
from laundry_service import parse_order, weight_average, payable_charge


@given(st.text() | st.none())
def test_parse_order_no_crash(s):
    try:
        parse_order(s)
    except Exception as e:
        assert False, f"parse_order crashed with: {e}"


@given(st.text() | st.none())
def test_weight_average_no_crash(s):
    try:
        weight_average(s)
    except Exception as e:
        assert False, f"weight_average crashed with: {e}"


@given(st.text() | st.none())
def test_payable_charge_no_crash(s):
    try:
        payable_charge(s)
    except Exception as e:
        assert False, f"payable_charge crashed with: {e}"
