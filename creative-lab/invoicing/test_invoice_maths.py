"""Known answers for the money rules. Run: python -m pytest test_invoice_maths.py -v"""
import pytest
from invoice_maths import rand, split_deposit, invoice_total, invoice_number


def test_rand_formats_like_a_south_african_invoice():
    assert rand(175000) == "R1,750.00"
    assert rand(5) == "R0.05"
    assert rand(100000000) == "R1,000,000.00"


def test_itumeleng_deposit_is_half_of_3500():
    assert split_deposit(350000) == (175000, 175000)


def test_odd_cent_goes_to_the_balance():
    assert split_deposit(333301) == (166650, 166651)


def test_deposit_and_balance_always_add_up():
    for total in range(0, 100001, 7):
        deposit, balance = split_deposit(total)
        assert deposit + balance == total


def test_invoice_total_adds_quantity_times_price():
    items = [("Starter website", 1, 500000), ("Founding client discount", 1, 0)]
    assert invoice_total(items) == 500000


def test_invoice_number_have_four_digits():
    assert invoice_number(1) == "SEP-INV-0001"
    assert invoice_number(5, prefix="SEP-Q") == "SEP-Q-0005"


@pytest.mark.parametrize("bad", [3500.0, "3500", -1, True])
def test_bad_amount_are_refused(bad):
    with pytest.raises(ValueError):
        rand(bad)