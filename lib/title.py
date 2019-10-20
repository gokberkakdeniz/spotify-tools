#!/usr/bin/env python3

from re import sub as replace
from itertools import chain as flatten


def tokenize(text):
    """Simple word tokenizer like nltk.word_tokenize
    
    Arguments:
        text {str} -- A string
    
    Returns:
        List -- A list of tokens
    """
    tokenized = []
    chunk = ""

    for char in text:
        if char in " ":
            if not chunk == "":
                tokenized.append(chunk)
                chunk = ""
        elif char in "([{":
            tokenized.append(char)
        elif char in "/}])":
            if not chunk == "":
                tokenized.append(chunk)            
            tokenized.append(char)
            chunk = ""
        else:
            chunk += char
    if not chunk == "":
        tokenized.append(chunk)

    return tokenized


def fractionate(tokenized):
    """Groups tokenized string
    
    Arguments:
        tokenized {List} -- Tokenized string
    Return:
        list -- A list of list of tokens
    """

    fractions = []
    chunk = []
    
    for token in tokenized:
        if token in "([{":
            if not len(chunk) == 0:
                fractions.append(chunk)
                chunk = []
            chunk.append(token)
        elif token in "/-" and len(chunk) > 0 and not chunk[0] in "([{":
            fractions.append(chunk)
            chunk = list()
            chunk.append(token)
        elif token in "}])":
            chunk.append(token)
            if not len(chunk) == 0:
                fractions.append(chunk)
            chunk = []
        else:
            chunk.append(token)
    if not len(chunk) == 0:
        fractions.append(chunk)

    return fractions


def defragment(tokenized):
    """Converts token list to string
    
    Arguments:
        tokenized {list} -- Tokenized string
    
    Return:
        str -- Rebuilt string
    """

    title = ""
    for token in tokenized:
        if token in "([{":
            title += token
        elif token in "}])":
            title = title[:-1] + token + " "
        else:
            title += token + " "
    return replace(r"(?<=\d)( \/ )(?=\d)", "/", title[:-1])


def distill(text):
    return replace("[^0-9a-zA-Z]+", "", text).lower()


def is_year(text):
    return len(text) == 4 and text.isdigit()


def ratio_test(group, threshold):
    keywords = [
        "album",
        "alternate",
        "anniversary",
        "bonus",
        "deluxe",
        "digital",
        "edition",
        "from",
        "live",
        "mono",
        "recorded",
        "remaster",
        "remastered",
        "rerecorded",
        "sessions",
        "single",
        "soundtrack",
        "special",
        "spotify",
        "studio",
        "studios",
        "sxsw",
        "unreleased",
        "version"
    ]

    group = list(filter(lambda token: len(token) > 1, group))
    if len(group) == 0:
        return 0
    ratio = len(list(filter(lambda token: distill(token) in keywords or is_year(token), group))) / len(group)

    return ratio < threshold


def phrase_test(group):
    phrases = [
        "album version",
        "intro version",
        "session version",
        "hall version",
        "anniversary version",
        "recorded at",
        "recorded in",
        "recorded live at",
        "recorded during",
        "live at",
        "live from",
        "spotify session",
        "jim eno session",
        "john peel session",
        "from tokyo disneysea",
        "lennon legend version",
        "curated by",
        "ep version",
        "саундтрек к компьютерной игре"
    ]

    joined = " ".join(group).lower()

    for phrase in phrases:
        if phrase in joined:
            return False
    return True


def clean(title, tests=None):
    """Returns copy of title without unnecessary parts
    
    Arguments:
        title {str} -- Song title
    
    Keyword Arguments:
        tests {list} -- List of test functions (default: {[lambda group: ratio_test(group, 0.5), phrase_test]})
    
    Returns:
        str -- Copy of title without unnecessary parts
    """

    if tests is None:
        tests = [lambda group: ratio_test(group, 0.5), phrase_test]

    tokenized = tokenize(title)
    grouped = fractionate(tokenized)
    if len(grouped) == 1:
        return title
    else:
        simplified = [grouped[0]] + list(filter(lambda group: all([f(group) for f in tests]), grouped[1:]))
        if len(simplified) == len(grouped):
            return title
        flat = list(flatten(*simplified))
        unified = defragment(flat)
        return unified
