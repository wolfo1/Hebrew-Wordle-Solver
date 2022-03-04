import itertools
import math
import sys
import re
from collections import defaultdict

HEBREW_LETTERS = "אבגדהוזחטיכלמנסעפצקרשת"
ENGLISH_LETTERS = "abcdefghijklmnopqrstuvwxyz"
FINAL_TO_REGULAR = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
REGULAR_TO_FINAL = {'כ': 'ך', 'מ': 'ם', 'נ': 'ן', 'פ': 'ף', 'צ': 'ץ'}
REGEX = "[{a}]{{1}}[{b}]{{1}}[{c}]{{1}}[{d}]{{1}}[{e}]{{1}}"
GREEN = '2'
YELLOW = '1'
GREY = '0'
PLACEHOLDER = "X"


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


class WordleSolver:
    def __init__(self):
        self.guess = [''] * 5
        self.excluded_for_letter = [''] * 5
        self.patterns = {''.join(i): 0 for i in itertools.product("012", repeat=5)}

    # not working
    def word_filter(self, word, ):
        pass

    def atLeast_filter(self, word: str, filters: list[tuple[str, int]]) -> bool:
        """
        function checks if the word has each letter AT LEAST the number of occurrences specified in the filters.
        :param word: a string.
        :param filters: a list of tuples, each containing a character and number of occurrences.
        :return: true if word follows the filters, false otherwise.
        """
        return all(word.count(character) >= frequency
                   for character, frequency in filters)

    def exactly_filter(self, word: str, filters: list[tuple[str, int]]) -> bool:
        """
        function checks if the word has each letter EXACTLY the number of occurrences specified in the filters.
        :param word: a string.
        :param filters: a list of tuples, each containing a character and number of occurrences.
        :return: true if word follows the filters, false otherwise.
        """
        return all(word.count(character) == frequency
                   for character, frequency in filters)

    def filter_word(self, exactly, not_included, included, word):
        occurrences = {}
        for k in range(5):
            if word[k] in not_included:
                return False
            if self.guess[k] != '' and self.guess[k] != word[k]:
                return False
            if word[k] in occurrences:
                occurrences[word[k]] += 1
            else:
                occurrences[word[k]] = 1
            if word[k] in self.excluded_for_letter[k]:
                return False
        for key in exactly:
            if occurrences.get(key) != exactly.get(key):
                return False
        for letter in included:
            if letter not in word:
                return False
        return True

    """test"""

    def filter_pattern(self, pattern, word, wordlist):
        self.excluded_for_letter = [''] * 5
        exactly = {}
        not_included = set()
        included = set()
        for j in range(5):
            if pattern[j] == GREEN:
                included.add(word[j])
                self.guess[j] = word[j]
            elif pattern[j] == YELLOW:
                included.add(word[j])
                self.excluded_for_letter[j] += word[j]
            elif pattern[j] == GREY:
                if word[j] not in included:
                    not_included.add(word[j])
                else:
                    exactly[word[j]] = sum(
                        [1 for letter in word if letter == word[j] and (pattern[j] == 1 or pattern[j] == 2)])
        new_list = []
        for w in wordlist:
            if self.filter_word(exactly, not_included, included, w):
                new_list.append(w)
        return new_list

    def filterPattern(self, pattern, word, wordlist) -> list[str]:
        # letters = [HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS, HEBREW_LETTERS]
        letters = [ENGLISH_LETTERS, ENGLISH_LETTERS, ENGLISH_LETTERS, ENGLISH_LETTERS, ENGLISH_LETTERS]
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
        filtered_words = list(filter(lambda word: self.atLeast_filter(word, atLeast_filters), filtered_words))
        filtered_words = list(filter(lambda word: self.exactly_filter(word, exactly_filters), filtered_words))
        # filtered_words = list(filter(lambda word: word_filter(word, at_least, exactly, letters), wordlist))
        return filtered_words

    def getPattern(self, guess, solution):
        pattern = GREY * len(guess)
        letter_counts = defaultdict(int)
        # get the count for each letter in the solution
        for letter in solution:
            letter_counts[letter] += 1
        # first find all green letters.
        for i in range(len(guess)):
            if guess[i] == solution[i]:
                pattern = pattern[:i] + GREEN + pattern[i + 1:]
                letter_counts[guess[i]] -= 1
        # mark all yellow an grey letters.
        for i in range(len(guess)):
            if letter_counts[guess[i]] > 0 and pattern[i] == GREY:
                pattern = pattern[:i] + YELLOW + pattern[i + 1:]
                letter_counts[i] -= 1
        return pattern

    def calculateFastEntropy(self, guess, solutions) -> float:
        self.patterns = dict.fromkeys(self.patterns, 0)
        for solution in solutions:
            pattern = self.getPattern(guess, solution)
            self.patterns[pattern] += 1
        # calculate the entropy of the guess
        solutions_count = len(solutions)
        entropy = 0
        for pattern in self.patterns:
            probability = self.patterns[pattern] / solutions_count
            if probability > 0:
                entropy += probability * math.log2(1 / probability)
        return entropy


    def calculateEntropy(self, guess, wordlist) -> float:
        """
        function calculates what is the expected information that will be given by the word for a given list of words.
        :param guess: word to calculate expected information from.
        :param wordlist: list of possible solutions.
        :return: float, what is the expected information. lower is better.
        """
        total_words = len(wordlist)
        entropy = 0
        # iterate over all possible patterns (grey, yellow, green)
        for pattern in self.patterns.keys():
            filtered_words = self.filterPattern(pattern, guess, wordlist)
            probability = len(filtered_words) / total_words
            if probability != 0:
                entropy += probability * math.log2(1 / probability)
        return entropy

    def solve(self, solution, wordlist):
        for i in range(5):
            max_entropy = 0
            max_word = ""
            for word in wordlist:
                entropy = self.calculateFastEntropy(word, wordlist)
                if entropy > max_entropy:
                    max_word = word
                    max_entropy = entropy
            pattern = self.getPattern(max_word, solution)
            if pattern == "22222":
                return i
            wordlist = self.filterPattern(pattern, max_word, wordlist)
        return 0


if __name__ == '__main__':
    filename = sys.argv[1]
    words = getWordList(filename)
    solver = WordleSolver()
    # print(solver.calculateEntropy("מגבלה", words))
    print(solver.solve("crate", words))
    """
    results = []
    for word in words:
        results.append((word, calculateEntropy(word, words)))
    results.sort(key=lambda x: x[1], reverse=True)
    print(results)
    """
