import itertools
import sys
import re

HEBREW_LETTERS = "אבגדהוזחטיכלמנסעפצקרשת"
FINAL_TO_REGULAR = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
REGULAR_TO_FINAL = {'כ': 'ך', 'מ': 'ם', 'נ': 'ן', 'פ': 'ף', 'צ': 'ץ'}
LETTERS = "012"
KEYWORDS = [''.join(i) for i in itertools.product(LETTERS, repeat=5)]
EXPRESSION1 = "(?=[^\W"
EXPRESSION2 = "]*f{"
EXPRESSION3 = "})"


def getWordList(filename) -> list[str]:
    f = open(filename, "r", encoding="utf-8")
    wordlist = f.read().splitlines()
    f.close()
    return wordlist


def calculateExpectedValue(word, wordlist) -> float:
    results = []
    for i in range(3):
        pattern = KEYWORDS[i]
        print("pattern: " + pattern)
        letters = [HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS]
        mustHave = {"א": 0, "ב": 0, "ג": 0, "ד": 0, "ה": 0, "ו": 0, "ז": 0, "ח": 0, "ט": 0, "י": 0, "כ": 0,
                    "ל": 0, "מ": 0, "נ": 0, "ס": 0, "ע": 0, "פ": 0, "צ": 0, "ק": 0, "ר": 0, "ש": 0, "ת": 0}
        for j in range(5):
            if pattern[j] == '0':
                for k in range(5):
                    letters[k] = letters[k].replace(word[j], "")
            elif pattern[j] == '1':
                letters[j] = letters[j].replace(word[j], "")
                mustHave[word[j]] += 1
            elif pattern[j] == '2':
                letters[j] = word[j]
        r = "[" + letters[0] + "]{1}" + "[" + letters[1] + "]{1}" + "[" + letters[2] + "]{1}" + "[" + letters[3] + "]{1}" + "[" + letters[4] + "]{1}"
        print("first regex: " + r)
        r2 = "\\b"
        for letter in mustHave:
            if mustHave[letter] > 0:
                r2 += EXPRESSION1
                r2 += letter
                r2 += EXPRESSION2
                r2 += str(mustHave[letter])
                r2 += EXPRESSION3
        r2 += "\\w+\\b"
        print("second regex: " + r2)
        regex = re.compile(r)
        newWordList = list(filter(regex.match, wordlist))
        print(newWordList)
        regex = re.compile(r2)
        newWordList = list(filter(regex.match, newWordList))
        print(newWordList)
        results.append(len(newWordList))
    average = sum(results) / len(results)
    return average


def solve(wordList):
    guess = input("enter word:")
    result = input("enter result, 0 is grey, 1 orange, 2 green: (i.e 00001)")


if __name__ == '__main__':
    filename = sys.argv[1]
    words = getWordList(filename)
    print(calculateExpectedValue("לגמור", words))
    print(words)
