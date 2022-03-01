import itertools
import sys
import re


HEBREW_LETTERS = "אבגדהוזחטיכלמנסעפצקרשת"
ENGLISH_LETTERS = "abcdefghijklmnopqrstuvwxyz"
FINAL_TO_REGULAR = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
REGULAR_TO_FINAL = {'כ': 'ך', 'מ': 'ם', 'נ': 'ן', 'פ': 'ף', 'צ': 'ץ'}
KEYWORDS = [''.join(i) for i in itertools.product("012", repeat=5)]
REGEX = "[{a}]{{1}}[{b}]{{1}}[{c}]{{1}}[{d}]{{1}}[{e}]{{1}}"
GREEN = '2'
YELLOW = '1'
GREY = '0'


def filter_words(text: str, filters: list) -> bool:
    return all(text.count(character) == frequency
               for character, frequency in filters)


def getWordList(filename) -> list[str]:
    f = open(filename, "r", encoding="utf-8")
    wordlist = f.read().splitlines()
    f.close()
    return wordlist


def calculateExpectedValue(word, wordlist) -> float:
    results = []
    for i in range(243):
        pattern = KEYWORDS[i]
        print("pattern: " + pattern)
        # letters = [HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS]
        letters = [ENGLISH_LETTERS, ENGLISH_LETTERS, ENGLISH_LETTERS, ENGLISH_LETTERS, ENGLISH_LETTERS]
        # mustHave holds how many occurrences each letter has to appear in the solution (yellow or green letters)
        # mustHave = {"א": 0, "ב": 0, "ג": 0, "ד": 0, "ה": 0, "ו": 0, "ז": 0, "ח": 0, "ט": 0, "י": 0, "כ": 0,
        #            "ל": 0, "מ": 0, "נ": 0, "ס": 0, "ע": 0, "פ": 0, "צ": 0, "ק": 0, "ר": 0, "ש": 0, "ת": 0}
        mustHave = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0, 'i': 0, 'j': 0, 'k': 0, 'l': 0,
                    'm': 0, 'n': 0, 'o': 0, 'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0, 'u': 0, 'v': 0, 'w': 0, 'x': 0,
                    'y': 0, 'z': 0}
        greys = set()
        for j in range(5):
            if pattern[j] == GREY:
                # only add letter to greys if it hasn't appeared as yellow \ green before.
                if mustHave[word[j]] == 0:
                    greys.add(word[j])
            elif pattern[j] == YELLOW:
                letters[j] = letters[j].replace(word[j], "")
                greys.discard(word[j])
                mustHave[word[j]] += 1
            elif pattern[j] == GREEN:
                letters[j] = word[j]
                mustHave[word[j]] += 1
        print(mustHave)
        print(letters)
        for j in range(5):
            letters[j] = ''.join('' if c in greys else c for c in letters[j])
        fltrs = [(k, v) for k, v in mustHave.items() if v > 0]
        r = REGEX.format(a=letters[0], b=letters[1], c=letters[2], d=letters[3], e=letters[4])
        regex = re.compile(r)
        newWordList = list(filter(regex.match, wordlist))
        newWordList = list(filter(lambda word: filter_words(word, fltrs), newWordList))
        results.append(len(newWordList))
        print(newWordList)
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
