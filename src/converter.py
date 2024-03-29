from __future__ import annotations

import re
from pathlib import Path
from typing import Literal, Union

import json

__punctuation = [ord(x) for x in "、。・「」"]

__prolonged_sound_mark = "ー"  # Also known as Chōonpu
__prolonged_sound_mark_point = ord("ー")

_following_vowel = json.load((Path(__file__) / ".." / "data" / "kana_map.json").resolve().open())
_kana_to_romanji = json.load((Path(__file__) / ".." / "data" / "romanji.json").resolve().open())
_romanji_to_kana = json.load((Path(__file__) / ".." / "data" / "romanji2.json").resolve().open())
_map_punctuation = {
    "english": {
        ".": "。",
        ",": "、",
        '"': "「」",
    },
    "japanese": {
        "、": ",",
        "。": ".",
        "・": "",
        "「": '"',
        "」": '"',
    }
}

__vowels = "aeiou"


def __convert(kana: str,
              to: Literal["katakana", "hiragana"],
              use_prolonged_mark: bool,
              ignore: Union[set, None] = None):
    """
    Converst hiragana to katakana or katakana to hiragana.
    :param kana: String of the charactest to convert.
    :param to: Either 'hiragana' or 'katakana'.
    :param use_prolonged_mark: Whether to replace duplicate vowels with Chōonpu
    :ignore set of characters that should be added as is
    :return: Converted string.
    """
    ignore = ignore or set()
    offset = 96 if to == "katakana" else -96
    valid_range = (12353, 12438) if to == "katakana" else (12353 + 96, 12438 + 96)
    output = []
    for character in kana:
        if character in ignore:
            output.append(character)
            continue
        code_point = ord(character)
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
        elif character == " ":
            output.append(" ")
        else:
            raise ValueError(f"Unkown character {character}")

    if use_prolonged_mark:
        __replace_with_prolonged_mark(output, to)

    return "".join(output)


def __replace_with_prolonged_mark(output, to):
    for i in range(1, len(output)):
        try:
            extension = _following_vowel[to][output[i - 1]]
            if extension == output[i]:
                output[i] = __prolonged_sound_mark
        except KeyError:
            pass


def hiragana_to_katakana(kana, use_prolonged_mark=True,
              ignore: Union[set, None] = None):
    return __convert(kana, "katakana", use_prolonged_mark, ignore)


def katakana_to_hiragana(kana, use_prolonged_mark=False,
              ignore: Union[set, None] = None):
    return __convert(kana, "hiragana", use_prolonged_mark, ignore)


def hiragana_to_romanji(kana,
              ignore: Union[set, None] = None):
    return katakana_to_romanji(hiragana_to_katakana(kana), ignore)


def katakana_to_romanji(kana,
              ignore: Union[set, None] = None):
    output = []
    ignore = ignore or set()

    duplicate_consonant = False
    previous_kana = ""
    for character in kana:
        if character in ignore:
            output.append(character)
            continue
        char_code = ord(character)
        if character in "ァィゥェォ":
            output[-1] = _kana_to_romanji[character][0]
        elif character in "ャュョ":
            if previous_kana not in "シジチヂ":
                output[-1] = "y"
            else:
                output.pop()
            output.append(_kana_to_romanji[character][1])
        elif character in __punctuation:
            output.append(_map_punctuation[character])
        elif character == "ッ":
            duplicate_consonant = True
        elif char_code == __prolonged_sound_mark_point:
            last = output[-1]
            output.append(last)
        elif 12353 + 96 <= char_code <= 12438 + 96:
            romanji = _kana_to_romanji[character]
            if duplicate_consonant:
                output.append(romanji[0])
                duplicate_consonant = False
            output.extend(romanji)
        elif character == " ":
            output.append(" ")
        else:
            raise ValueError(f"Unkown character {character}")
        previous_kana = character

    return "".join(output)


def romanji_to_katakana(romanji: str, use_prolonged_mark=True,
              ignore: Union[set, None] = None):
    romanji = romanji.lower()
    ignore = ignore or set()

    for f, s in [(r"c[^h]", lambda x: "k" + x.group(0)[1:]), ("x", "ks"), ("q", "k"), ("l", "r"), ("v", "b")]:
        romanji = re.sub(f, s, romanji)

    words = []
    for word in romanji.split():
        out = []
        i = 0
        previous_consonant = False
        while i < len(word):
            if word[i] in ignore:
                if previous_consonant:
                    __end_word(out, previous_consonant)
                out.append(word[i])
                i += 1
                continue

            if romanji[i] in __vowels:
                if not previous_consonant:
                    out.append(_romanji_to_kana[""][word[i]])
                else:
                    out.append(_romanji_to_kana[previous_consonant][word[i]])
                previous_consonant = False
            else:
                if previous_consonant:
                    if word[i] == "y":
                        previous_consonant = f"{previous_consonant}y"
                    elif word[i - 1] == word[i]:
                        if word[i] in "nm":
                            out.append("ン")
                        else:
                            out.append("ッ")
                        previous_consonant = word[i]
                    elif word[i - 1: i + 1] in _romanji_to_kana:
                        previous_consonant = word[i - 1: i + 1]
                    else:
                        if previous_consonant == "t":
                            out.append("ト")
                        else:
                            out.append(_romanji_to_kana[previous_consonant]["u"])
                        previous_consonant = word[i]
                else:
                    previous_consonant = word[i]
            i += 1

        if previous_consonant:
            __end_word(out, previous_consonant)

        if use_prolonged_mark:
            __replace_with_prolonged_mark(out, "katakana")
        words.append("".join(out))
    return " ".join(words)


def __end_word(out, previous_consonant):
    if previous_consonant == "t":
        out.append("ト")
    elif previous_consonant == "m":
        try:
            out.pop()
        except IndexError:
            pass
        out.append("ム")
    elif previous_consonant != "n":
        out.append(_romanji_to_kana[previous_consonant]["u"])
    else:
        out.append("ン")


def romanji_to_hiragana(romanji, use_prolonged_mark=False,
              ignore: Union[set, None] = None):
    return katakana_to_hiragana(romanji_to_katakana(romanji, use_prolonged_mark, ignore))


if __name__ == '__main__':
    romanji_to_katakana("gamma")
