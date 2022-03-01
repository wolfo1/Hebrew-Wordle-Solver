import itertools
import math
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


def word_filter(word, atleast, exactly, letters):
    occurrences = defaultdict(int)
    for i in range(5):
        if word[i] not in letters[i]:
            return False
        occurrences[word[i]] += 1
    for key in occurrences:
        least = atleast[key]
        exact = exactly[key]
        if least > 0 and occurrences[word] < least:
            return False
        if 0 < exact != occurrences[word]:
            return False
    return True


def atLeast_filter(word: str, filters: list[tuple[str, int]]) -> bool:
    """
    function checks if the word has each letter AT LEAST the number of occurrences specified in the filters.
    :param word: a string.
    :param filters: a list of tuples, each containing a character and number of occurrences.
    :return: true if word follows the filters, false otherwise.
    """
    return all(word.count(character) >= frequency
               for character, frequency in filters)


def exactly_filter(word: str, filters: list[tuple[str, int]]) -> bool:
    """
    function checks if the word has each letter EXACTLY the number of occurrences specified in the filters.
    :param word: a string.
    :param filters: a list of tuples, each containing a character and number of occurrences.
    :return: true if word follows the filters, false otherwise.
    """
    return all(word.count(character) == frequency
               for character, frequency in filters)


def filterPattern(pattern, word, wordlist) -> list[str]:
    letters = [HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS]
    # letters = [ENGLISH_LETTERS, ENGLISH_LETTERS, ENGLISH_LETTERS, ENGLISH_LETTERS, ENGLISH_LETTERS]
    # letters that have to appear exactly number of times.
    exactly = defaultdict(int)
    # letters that have to appear at least number of times
    at_least = defaultdict(int)
    greys = []
    for j in range(5):
        if pattern[j] == GREY:
            letters[j] = letters[j].replace(word[j], "")
            greys.append(word[j])
        elif pattern[j] == YELLOW:
            if word[j] in greys:
                return []
            letters[j] = letters[j].replace(word[j], "")
            at_least[word[j]] += 1
        elif pattern[j] == GREEN:
            letters[j] = word[j]
            at_least[word[j]] += 1
    # if a letter was greyed & yellowed / green, move it to "exactly".
    for letter in greys:
        if at_least[letter] > 0:
            exactly[letter] = at_least[letter]
    greys = [x for x in greys if not at_least[x] > 0]
    # remove all completely greyed chars from possible letters.
    for j in range(5):
        letters[j] = ''.join('' if c in greys else c for c in letters[j])
    atLeast_filters = [(k, v) for k, v in at_least.items() if v > 0]
    exactly_filters = [(k, v) for k, v in exactly.items() if v > 0]
    # filter out words that don't comply with possible chars for each letter.
    r = re.compile(REGEX.format(a=letters[0], b=letters[1], c=letters[2], d=letters[3], e=letters[4]))
    filtered_words = list(filter(r.match, wordlist))
    # filter out based on atLeast and exactly dicts.
    filtered_words = list(filter(lambda word: atLeast_filter(word, atLeast_filters), filtered_words))
    filtered_words = list(filter(lambda word: exactly_filter(word, exactly_filters), filtered_words))
    # filtered_words = list(filter(lambda word: word_filter(word, at_least, exactly, letters), wordlist))
    return filtered_words


def calculateEntropy(word, wordlist) -> float:
    """
    function calculates what is the expected information that will be given by the word for a given list of words.
    :param word: word to calculate expected information from.
    :param wordlist: list of possible solutions.
    :return: float, what is the expected information. lower is better.
    """
    results = []
    total_words = len(wordlist)
    # iterate over all possible patterns (grey, yellow, green)
    for i in range(243):
        pattern = KEYWORDS[i]
        filtered_words = filterPattern(pattern, word, wordlist)
        probability = len(filtered_words) / total_words
        if probability != 0:
            results.append(probability * math.log2(1 / probability))
    entropy = sum(results)
    return entropy


def solve(solution, wordlist):
    for i in range(5):
        max_entropy = 0
        max_word = ""
        for word in wordlist:
            entropy = calculateEntropy(word, wordlist)
            if entropy > max_entropy:
                max_word = word
                max_entropy = entropy
        pattern = ""
        yellows = []
        for j in range(5):
            if max_word[j] == solution[j]:
                pattern += GREEN
            elif max_word[j] in solution:
                if max_word[j] in yellows:
                    pattern += GREY
                else:
                    pattern += YELLOW
            else:
                pattern += GREY
        if pattern == "22222":
            return i
        wordlist = filterPattern(pattern, max_word, wordlist)
    return 0


if __name__ == '__main__':
    filename = sys.argv[1]
    words = getWordList(filename)
    # test entire solve. currently 26m
    print(solve("מגבלה", words))
    """
    results = []
    for word in words:
        results.append((word, calculateEntropy(word, words)))
    results.sort(key=lambda x: x[1], reverse=True)
    print(results)
    """
