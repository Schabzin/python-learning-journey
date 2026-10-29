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