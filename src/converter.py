from __future__ import annotations
from pathlib import Path
from typing import Tuple, Literal

import json

__punctuation = [ord(x) for x in "、。・「」"]

__prolonged_sound_mark = "ー"  # Also known as Chōonpu
__prolonged_sound_mark_point = ord("ー")

_following_vowel = json.load((Path(__file__) / ".." / "data" / "kana_map.json").resolve().open())


def __convert(kana: str,
              to: Literal["katakana", "hiragana"],
              use_prolonged_mark: bool):
    """
    Converst hiragana to katakana or katakana to hiragana.
    :param kana: String of the charactest to convert.
    :param to: Either 'hiragana' or 'katakana'.
    :param use_prolonged_mark: Whether to replace duplicate vowels with Chōonpu
    :return: Converted string.
    """
    offset = 96 if to == "katakana" else -96
    valid_range = (12353, 12438) if to == "katakana" else (12353 + 96, 12438 + 96)
    output = []
    for character in kana:
        code_point = ord(character)
        print(code_point, valid_range, code_point + offset)
        if valid_range[0] <= code_point <= valid_range[1]:
            output.append(chr(code_point + offset))
        elif code_point in __punctuation:
            output.append(character)
        elif code_point == __prolonged_sound_mark_point:
            assert output
            if use_prolonged_mark:
                output.append(__prolonged_sound_mark)
            else:
                output.append(_following_vowel[to][output[-1]])
        else:
            raise ValueError(f"Unkown character {character}")

    if use_prolonged_mark:
        for i in range(1, len(output)):
            try:
                extension = _following_vowel[to][output[i - 1]]
                if extension == output[i]:
                    output[i] = __prolonged_sound_mark
            except KeyError:
                pass

    return "".join(output)


def hiragana_to_katakana(kana, use_prolonged_mark=True):
    return __convert(kana, "katakana", use_prolonged_mark)


def katakana_to_hiragana(kana, use_prolonged_mark=False):
    return __convert(kana, "hiragana", use_prolonged_mark)


def hiragana_to_romanji(kana):
    pass


def katakana_to_romanji(kana):
    pass


def romanji_to_katakana(romanji, use_prolonged_mark=True):
    pass


def romanji_to_hiragana(romanji, use_prolonged_mark=False):
    pass
