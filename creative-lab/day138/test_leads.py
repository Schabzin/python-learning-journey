from leads import tally


def test_counts_by_code():
    leads = [
        {"name": "A", "code": "WEB7"},
        {"name": "B", "code": " web7 "},
        {"name": "C", "code": "LB2"},
    ]
    counts, unknown = tally(leads)
    assert counts["WEB7"] == 2
    assert counts["LB2"] == 1
    assert unknown == []


def test_ads_with_no_leads_still_show_zero():
    counts, _ = tally([])
    assert counts == {"WEB7": 0, "REC1": 0, "LB1": 0, "LB2": 0,
                      "GBP1": 0, "FB1": 0, "FB2": 0, "FB3": 0, "FB4": 0}


def test_typo_code_goes_to_unknown():
    counts, unknown = tally([{"name": "Typo", "code": "WEB 7"}])
    assert unknown == ["Typo"]
    assert sum(counts.values()) == 0