import re

import pymorphy2

# Initialize pymorphy2
morph = pymorphy2.MorphAnalyzer()

# Here we store words already parsed by pymorphy2
already_parsed = {}


def clear_text(text: str) -> str:
    tmp_string = ''

    # find all words
    for word in re.findall(r'\w+', text.lower()):

        # if we haven't parse word before
        if word not in already_parsed:
            # get normal form of word
            normal = morph.parse(word)[0].normal_form

            # save only if word was in dictionary
            already_parsed[word] = "" if word == normal else normal

        # append to out string
        tmp_string += already_parsed[word] + ' '

    # one whitespace between the words
    return ' '.join(list(filter(lambda x: len(x) > 0, tmp_string.split(" "))))


def text_sum(text: list) -> str:
    tmp_text = ""
    for i in text:
        tmp_text += i
        tmp_text += " "
    return tmp_text
