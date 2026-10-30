import pytest
from leave_behind import chat_link, make_sheet


def test_chat_link_carries_the_code():
    assert chat_link("LB1").endswith("%28LB1%29.")


def test_sheet_is_a_real_pdf(tmp_path):
    path = tmp_path / "sheet.pdf"
    make_sheet("LB1", str(path))
    assert path.read_bytes().startswith(b"%PDF")


def test_unknown_sheet_code_refused(tmp_path):
    with pytest.raises(KeyError):
        make_sheet("NOPE", str(tmp_path / "x.pdf"))


def test_every_sheet_builds(tmp_path):
    from sheets import SHEETS
    for code in SHEETS:
        path = tmp_path / f"{code}.pdf"
        make_sheet(code, str(path))
        assert path.exists()


def test_qr_is_tappable_in_the_pdf(tmp_path):
    from pypdf import PdfReader
    path = tmp_path / "sheet.pdf"
    make_sheet("LB2", str(path))
    page = PdfReader(str(path)).pages[0]
    links = [a.get_object()["/A"]["/URI"] for a in page.get("/Annots", [])]
    assert links == [chat_link("LB2")]