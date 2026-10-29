import pytest
from vcard import make_vcard


def test_card_always_ends():
    card = make_vcard("Sechaba Mofokeng", "+27732239762", company="Separaka Holdings")
    assert card.endswith("END:VCARD\r\n")
    assert card.count("\r\n") == 7


def test_one_word_name():
    card = make_vcard("Percy", "+27821234567")
    assert "N:;Percy;;;" in card
    assert "FN:Percy" in card


def test_comma_is_escaped():
    card = make_vcard("Lindi Mokeona", "+27791259610", company="Hair, Nails & Beauty")
    assert "ORG:Hair\\, Nails & Beauty" in card


def test_empty_name_refused():
    with pytest.raises(ValueError):
        make_vcard("   ", "+27732239762")


def test_email_is_filed_as_work():
    card = make_vcard("Sechaba Mofokeng", "+27732239762", email="info@separaka.co.za")
    assert "EMAIL;TYPE=WORK:info@separaka.co.za\r\n" in card