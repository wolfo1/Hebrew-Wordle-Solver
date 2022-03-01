import itertools
import sys
import re
from collections import defaultdict

HEBREW_LETTERS = "אבגדהוזחטיכלמנסעפצקרשת"
ENGLISH_LETTERS = "abcdefghijklmnopqrstuvwxyz"
FINAL_TO_REGULAR = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
REGULAR_TO_FINAL = {'כ': 'ך', 'מ': 'ם', 'נ': 'ן', 'פ': 'ף', 'צ': 'ץ'}
KEYWORDS = [''.join(i) for i in itertools.product("012", repeat=5)]
REGEX = "[{a}]{{1}}[{b}]{{1}}[{c}]{{1}}[{d}]{{1}}[{e}]{{1}}"
GREEN = '2'
YELLOW = '1'
GREY = '0'


def getWordList(filename) -> list[str]:
    """
    get word list from a given filepath.
    :param filename:
    :return: list of words.
    """
    f = open(filename, "r", encoding="utf-8")
    wordlist = f.read().splitlines()
    f.close()
    return wordlist


def atLeast_filter(word: str, filters: list[tuple[str, int]]) -> bool:
    """
    function checks if the word has each letter at least the number of occurrences specified in the filters.
    :param word: a string.
    :param filters: a list of tuples, each containing a character and number of occurrences.
    :return: true if word follows the filters, false otherwise.
    """
    return all(word.count(character) >= frequency
               for character, frequency in filters)


def exactly_filter(word: str, filters: list[tuple[str, int]]) -> bool:
    """
    function checks if the word has each letter at least the number of occurrences specified in the filters.
    :param word: a string.
    :param filters: a list of tuples, each containing a character and number of occurrences.
    :return: true if word follows the filters, false otherwise.
    """
    return all(word.count(character) == frequency
               for character, frequency in filters)


def calculateExpectedValue(word, wordlist) -> float:
    """
    function calculates what is the expected information that will be given by the word for a given list of words.
    :param word: word to calculate expected information from.
    :param wordlist: list of possible solutions.
    :return: float, what is the expected information. lower is better.
    """
    results = []
    # iterate over all possible patterns (grey, yellow, green)
    for i in range(243):
        pattern = KEYWORDS[i]
        # letters = [HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS]
        letters = [ENGLISH_LETTERS, ENGLISH_LETTERS, ENGLISH_LETTERS, ENGLISH_LETTERS, ENGLISH_LETTERS]
        # holds how many occurrences each letter has to appear in the solution. 0 is unknown.
        # mustHave = {"א": 0, "ב": 0, "ג": 0, "ד": 0, "ה": 0, "ו": 0, "ז": 0, "ח": 0, "ט": 0, "י": 0, "כ": 0,
        #            "ל": 0, "מ": 0, "נ": 0, "ס": 0, "ע": 0, "פ": 0, "צ": 0, "ק": 0, "ר": 0, "ש": 0, "ת": 0}
        # letters that have to appear exactly number of times.
        exactly = defaultdict(int)
        # letters that have to appear at least number of times
        atleast = defaultdict(int)
        greys = []
        for j in range(5):
            if pattern[j] == GREY:
                letters[j] = letters[j].replace(word[j], "")
                greys.append(word[j])
            elif pattern[j] == YELLOW:
                letters[j] = letters[j].replace(word[j], "")
                atleast[word[j]] += 1
            elif pattern[j] == GREEN:
                letters[j] = word[j]
                atleast[word[j]] += 1
        # if a letter was greyed & yellowed / green, move it to "exactly".
        for letter in greys:
            if atleast[letter] > 0:
                exactly[letter] = atleast[letter]
                greys.remove(letter)
        # remove all completely greyed chars from possible letters.
        for j in range(5):
            letters[j] = ''.join('' if c in greys else c for c in letters[j])
        atLeast_filters = [(k, v) for k, v in atleast.items() if v > 0]
        exactly_filters = [(k, v) for k, v in exactly.items() if v > 0]
        # filter out words that don't complie with possible chars for each letter.
        r = REGEX.format(a=letters[0], b=letters[1], c=letters[2], d=letters[3], e=letters[4])
        regex = re.compile(r)
        newWordList = list(filter(regex.match, wordlist))
        # filter out based on atLeast and exactly dicts.
        newWordList = list(filter(lambda word: atLeast_filter(word, atLeast_filters), newWordList))
        newWordList = list(filter(lambda word: exactly_filter(word, exactly_filters), newWordList))
        results.append(len(newWordList))
    average = sum(results) / len(results)
    return average


def solve(wordList):
    guess = input("enter word:")
    result = input("enter result, 0 is grey, 1 orange, 2 green: (i.e 00001)")


if __name__ == '__main__':
    filename = sys.argv[1]
    words = getWordList(filename)
    print(calculateExpectedValue("speed", words))
    print(words)
