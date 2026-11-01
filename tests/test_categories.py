import pandas as pd
import pytest

from retail.categories import OTHER, categorize, classify, labels, load_rules

CFG = {
    "rules": [
        {"name": "christmas", "label": "Christmas", "any": ["CHRISTMAS", "BAUBLE"]},
        {"name": "jewellery", "any": ["RING", "NECKLACE"], "none": ["NAPKIN RING"]},
        {"name": "candles", "any": ["T-LIGHT", "CANDLE"]},
        {"name": "kitchen", "any": ["NAPKIN RING", "CAKE STAND"]},
    ],
    "overrides": {"85123A": "kitchen"},
}


def test_first_match_wins_whole_words_and_vetoes():
    rules, _ = load_rules(CFG)
    assert classify("christmas t-light holder", rules) == "christmas"  # order, upper case
    assert classify("WHITE HANGING HEART T-LIGHT HOLDER", rules) == "candles"
    assert classify("SILVER NAPKIN  RING SET", rules) == "kitchen"  # veto, runs of spaces
    assert classify("PINK ENAMEL RING", rules) == "jewellery"
    assert classify("EARRINGS", rules) == OTHER and classify("CANDLESTICK", rules) == OTHER
    assert classify("KEYRING", rules) == OTHER  # no match inside a word
    assert classify(None, rules) == OTHER


def test_categorize_with_overrides_and_labels():
    desc = pd.Series({"85123A": "WHITE HEART T-LIGHT", "22423": "REGENCY CAKE STAND", "X": "?"})
    out = categorize(desc, CFG)
    assert out.to_dict() == {"85123A": "kitchen", "22423": "kitchen", "X": OTHER}
    assert out.name == "category"
    assert labels(CFG) == {"christmas": "Christmas", "jewellery": "jewellery",
                           "candles": "candles", "kitchen": "kitchen", OTHER: "Other"}  # fmt: skip


def test_bad_configs():
    with pytest.raises(ValueError):
        load_rules({"rules": [{"name": "a", "any": ["X"]}, {"name": "a", "any": ["Y"]}]})
    with pytest.raises(ValueError):
        load_rules({"rules": [{"name": "a", "any": ["X"]}], "overrides": {"1": "nope"}})


def test_shipped_rules_on_known_products():
    rules, _ = load_rules()
    expected = {
        "JUMBO BAG RED RETROSPOT": "bags",
        "WHITE HANGING HEART T-LIGHT HOLDER": "candles_lights",
        "REGENCY CAKESTAND 3 TIER": "kitchen_tableware",
        "PAPER CHAIN KIT 50'S CHRISTMAS": "christmas",
        "CHOCOLATE HOT WATER BOTTLE": "textiles_cushions",
        "BLACK BAROQUE CARRIAGE CLOCK": "wall_decor",
        "Next Day Carriage": "non_product",
        "OVAL WALL MIRROR DIAMANTE": "wall_decor",
        "CARNIVAL BRACELET": "jewellery",
        "PARTY BUNTING": "party_giftwrap",
    }
    assert {d: classify(d, rules) for d in expected} == expected
