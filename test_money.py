from money import fmt_rand

def test_thousands_and_cents():
    assert fmt_rand(6420.0) == "R6,420.00"
    assert fmt_rand(201020.5) == "R201,020.50"

def test_small_and_zero():
    assert fmt_rand(950) == "R950.00"
    assert fmt_rand(0) == "R0.00"

def test_no_deposit_shows_zero():
    assert fmt_rand(None) == "R0.00"

def test_cents_carry_into_rands():
    assert fmt_rand(19.999) == "R20.00"

def test_negative_sign_goes_before_R():
    assert fmt_rand(-1500) == "-R1,500.00"