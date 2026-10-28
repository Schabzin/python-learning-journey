import pytest
from card import draw_card, WHITE
from qr import read_qr
from vcard import make_vcard


def test_qr_still_reads_inside_the_card(tmp_path):
    vcard = make_vcard("Sechaba Mofokeng", "+27732239762")
    path = tmp_path / "card.png"
    draw_card(vcard, [("Sechaba Mofokeng", 72, WHITE)], path)
    assert read_qr(path) == vcard


def test_text_too_wide_is_refused(tmp_path):
    vcard = make_vcard("Sechaba Mofokeng", "+27732239762")
    too_long = [("Sechaba Mofokeng" * 5, 72, WHITE)]
    with pytest.raises(ValueError):
        draw_card(vcard, too_long, tmp_path / "card.png")