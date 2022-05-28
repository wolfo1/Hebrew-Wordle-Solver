import itertools
import math
import re
import json
from typing import List
from collections import defaultdict
from enum import Enum

WORD_LENGTH = 5
NUM_OF_TRIES = 6

# Hebrew meduyeket (מדויקת) data files
HEBREW_GUESSES_PATH = "database/hebrew_guesses.json"  # 3k possible guesses
MEDUYEKET_SOLUTIONS_PATH = "database/hebrew_solutions_meduyeket.json"
FIRST_WORDS_MEDUYEKET_PATH = "database/heb_first_words_meduyeket.json"
# English wordle data files
ENGLISH_GUESSES_PATH = "database/english_guesses.json"
ENGLISH_SOLUTIONS_PATH = "database/english_solutions.json"
FIRST_WORDS_ENGLISH_PATH = "database/english_first_word_scores.json"

# dict from finalized letters to regular and vice versa
ENGLISH_LETTERS = "abcdefghijklmnopqrstuvwxyz"
HEBREW_LETTERS = "אבגדהוזחטיכלמנסעפצקרשת"
FINAL_TO_REGULAR = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
REGULAR_TO_FINAL = {'כ': 'ך', 'מ': 'ם', 'נ': 'ן', 'פ': 'ף', 'צ': 'ץ'}
REGEX = "[{a}]{{1}}[{b}]{{1}}[{c}]{{1}}[{d}]{{1}}[{e}]{{1}}"
GREEN = '2'
YELLOW = '1'
GREY = '0'
# console msgs
START_PROMPT = "Choose mode:\n0: Hebrew.\n1: English.\n"
FAIL_MSG = "Failed to find the word in number of tries: "


class Language(Enum):
    HEBREW = 0
    ENGLISH = 1


def load_words_JSON(filepath: str) -> list[str]:
    """
    get word list from a given filepath.
    :param filepath: path to a JSON file
    :return: list of words.
    """
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    return data['words']


def atLeast_filter(word: str, char_frequencies: list[tuple[str, int]]) -> bool:
    """
    check if all characters in a given word appear at least the number of times desired.
    :param word: the word to check
    :param char_frequencies: a list of all characters, and their desired minimal frequency
    :return: True if all characters in word appear at least the number of times specified
            in char_frequencies, else False
    """
    return all(word.count(character) >= frequency
               for character, frequency in char_frequencies)


def exactly_filter(word: str, char_frequencies: list[tuple[str, int]]) -> bool:
    """
    check if all characters in a given word appear exactly the number of times desired.
    :param word: the word to check
    :param char_frequencies: a list of all characters, and their desired frequency
    :return: return True if all characters in word appear exactly the number of times
            specified in char_frequencies list, else False.
    """
    return all(word.count(character) == frequency
               for character, frequency in char_frequencies)


def get_pattern(guess: str, solution: str) -> str:
    """
    returns the pattern from a given guess and a given solution based on the
    wordle rules.
    :param guess: the guess
    :param solution: the solution
    :return: a string of 5 {0,1,2} of the pattern.
    """
    pattern = [GREY] * len(guess)
    letter_counts = {}
    # get the count for each letter in the solution
    for letter in solution:
        if letter in letter_counts:
            letter_counts[letter] += 1
        else:
            letter_counts[letter] = 1
    # first find all green letters.
    for i in range(len(guess)):
        if guess[i] == solution[i]:
            pattern[i] = GREEN
            letter_counts[guess[i]] -= 1
    # mark all yellow letters.
    for i in range(len(guess)):
        if guess[i] in letter_counts:
            if letter_counts[guess[i]] > 0 and pattern[i] == GREY:
                pattern[i] = YELLOW
                letter_counts[guess[i]] -= 1
    return ''.join(pattern)


def filter_words(pattern: str, guess: str, wordlist: List[str], language: Language) -> list[str]:
    """
    filter solution group based on the pattern user got from Wordle.
    :param wordlist: list of all possible words
    :param language: language the game is played in, Hebrew / English.
    :param pattern: the pattern the guess generated, a string of 5 {0,1,2}.
    :param guess: the guess user made
    """
    # letters that have to appear exactly number of times.
    if language == Language.HEBREW:
        letters = [HEBREW_LETTERS] * WORD_LENGTH
    else:
        letters = [ENGLISH_LETTERS] * WORD_LENGTH
    # letters that have to appear exactly number of times.
    exactly = defaultdict(int)
    # letters that have to appear at least number of times
    at_least = defaultdict(int)
    greys = []
    for j in range(5):
        if pattern[j] == GREY:
            letters[j] = letters[j].replace(guess[j], "")
            greys.append(guess[j])
        elif pattern[j] == YELLOW:
            if guess[j] in greys:
                return []
            letters[j] = letters[j].replace(guess[j], "")
            at_least[guess[j]] += 1
        elif pattern[j] == GREEN:
            letters[j] = guess[j]
            at_least[guess[j]] += 1
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
    return filtered_words


class WordleSolver:
    def __init__(self, language: Language = Language.ENGLISH):
        self.patterns = {''.join(i): 0 for i in itertools.product("012", repeat=WORD_LENGTH)}
        self.language = language
        if self.language == Language.HEBREW:
            self.guesses = load_words_JSON(HEBREW_GUESSES_PATH)
            self.solutions = load_words_JSON(MEDUYEKET_SOLUTIONS_PATH)
            self.first_words = load_words_JSON(FIRST_WORDS_MEDUYEKET_PATH)[:9]
        else:
            self.guesses = load_words_JSON(ENGLISH_GUESSES_PATH)
            self.solutions = load_words_JSON(ENGLISH_SOLUTIONS_PATH)
            self.first_words = load_words_JSON(FIRST_WORDS_ENGLISH_PATH)[:9]

    def process_heb_word(self, word: str) -> str:
        """
        turn the last letter to finalized ("ot sofit") later or vice versa.
        :param word: a hebrew word
        :return: the word with a finalized / de-finalized last letter.
        """
        if self.language != Language.HEBREW:
            return word
        if word[-1] in REGULAR_TO_FINAL:
            return word[:-1] + REGULAR_TO_FINAL[word[-1]]
        elif word[-1] in FINAL_TO_REGULAR:
            return word[:-1] + FINAL_TO_REGULAR[word[-1]]
        else:
            return word

    def fast_entropy(self, guess: str) -> float:
        """
        calculate entropy of a given guess - how much information will be attained from guessing the guess in average.
        a score of 1 means halving the solution group once.
        :param guess: the guess we are calculating entropy for
        :return: the entropy of the guess.
        """
        self.patterns = dict.fromkeys(self.patterns, 0)
        # count how many solutions go to each pattern the guess can generate
        for solution in self.solutions:
            pattern = get_pattern(guess, solution)
            self.patterns[pattern] += 1
        entropy = 0
        for pattern in self.patterns:
            probability = self.patterns[pattern] / len(self.solutions)
            if probability > 0:
                entropy += probability * math.log2(1 / probability)
        return entropy

    def calculate_first_word_fast(self) -> None:
        """
        Calculate entropies for the first word used, and store results in a JSON file.
        """
        res = []
        for guess in self.guesses:
            res.append((guess, round(self.fast_entropy(guess), 4)))
        res.sort(key=lambda x: x[1], reverse=True)
        filepath = [FIRST_WORDS_ENGLISH_PATH, FIRST_WORDS_MEDUYEKET_PATH][self.language == Language.HEB_WORDLE]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({"words": res}, f, ensure_ascii=False)

    def virtual_solve(self, solution: str) -> int:
        """
        tests the program on a given solution - the program will try to solve the game.
        :param solution: given solution
        :return: how many guesses it took to solve the given solution.
                 -1 if program failed to find given solution in 6 guesses or under.
        """
        for i in range(NUM_OF_TRIES):
            if len(self.solutions) == 1:
                max_word = self.solutions[0]
            elif i == 0:
                max_word = self.first_words[0][0]
            else:
                max_entropy = -1
                max_word = ""
                # find the word with the highest entropy and guess it.
                for word in self.guesses:
                    entropy = self.fast_entropy(word)
                    if entropy > max_entropy:
                        max_word = word
                        max_entropy = entropy
            print(i + 1, self.process_heb_word(max_word))
            pattern = get_pattern(max_word, solution)
            if pattern == GREEN * WORD_LENGTH:
                return i + 1
            self.solutions = filter_words(pattern, max_word, self.solutions, self.language)
        return -1

    def interactive_solve(self) -> (str, int):
        """
        interactive solve - user enter his guess and the pattern the official wordle site returned him,
        and the program will suggest the top 5 words to guess.
        :return: tuple (final solution, number of guesses)
        """
        for i in range(NUM_OF_TRIES):
            # stop cases: potential solution group size is lower than 2.
            if len(self.solutions) == 1:
                return self.process_heb_word(self.solutions[0]), i + 1
            elif len(self.solutions) == 2:
                print("potential solutions are:\n", [self.process_heb_word(word) for word in self.solutions])
            # the top guesses are pre-calculated for the first word.
            elif i == 0:
                print("Top guesses:\n", [(self.process_heb_word(word), score) for word, score in self.first_words])
            # else, calculate what are the best cases and print them to the user.
            else:
                results = []
                print(self.solutions)
                for guess in self.guesses:
                    results.append((self.process_heb_word(guess), round(self.fast_entropy(guess), 2)))
                results.sort(key=lambda x: x[1], reverse=True)
                print("Top guesses are:\n", results[:5])

            # get user's guess & Wordle's generated pattern from user
            guess = self.process_heb_word(input("Enter your guess:\n"))
            pattern = input("Enter pattern: (0 for grey, 1 for yellow, 2 for green. i.e \'00112\')\n")
            if pattern == GREEN * WORD_LENGTH:
                return self.process_heb_word(guess), i + 1
            self.solutions = filter_words(pattern, guess, self.solutions, self.language)
        return FAIL_MSG, NUM_OF_TRIES


def run_solver(language: Language) -> None:
    solver = WordleSolver(language)
    print(solver.interactive_solve())


if __name__ == '__main__':
    language = Language.HEBREW
    # while True:
    #     try:
    #         langauge = Language(int(input(START_PROMPT)))
    #         break
    #     except ValueError:
    #         continue
    run_solver(language)
