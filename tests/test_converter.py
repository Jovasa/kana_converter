import pytest

from converter import hiragana_to_katakana, katakana_to_hiragana


def test_simple_hira_to_kata():
    kana = "あ"
    assert hiragana_to_katakana(kana) == "ア"

    assert hiragana_to_katakana("おはようございます") == "オハヨウゴザイマス"


def test_simple_kata_to_hira():
    assert katakana_to_hiragana("ア") == "あ"

    assert katakana_to_hiragana("オハヨウゴザイマス") == "おはようございます"


def test_punctuation():
    assert hiragana_to_katakana("「。」") == "「。」"
    assert katakana_to_hiragana("「。」") == "「。」"


def test_prolonged_mark():
    assert hiragana_to_katakana("あー", use_prolonged_mark=False) == "アア"
    assert hiragana_to_katakana("きゃー", use_prolonged_mark=False) == "キャア"

    assert hiragana_to_katakana("ああ", use_prolonged_mark=True) == "アー"
    assert hiragana_to_katakana("きゃあ", use_prolonged_mark=True) == "キャー"
