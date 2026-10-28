from PIL import Image
from qr import make_qr, read_qr
from vcard import make_vcard


def test_round_trip(tmp_path):
    card = make_vcard("Sechaba Mofokeng", "+27732239762", company="Separaka Holdings")
    path = tmp_path / "card.png"
    make_qr(card, path)
    assert read_qr(path) == card


def test_more_text_needs_bigger_qr(tmp_path):
    small = make_qr("hi", tmp_path / "small.png")
    big = make_qr("x" * 300, tmp_path / "big.png")
    assert big > small


def test_blank_image_reads_nothing(tmp_path):
    path = tmp_path / "blank.png"
    Image.new("RGB", (300, 300), "white").save(path)
    assert read_qr(path) == ""