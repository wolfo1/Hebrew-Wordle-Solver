import itertools
import math
import re
from collections import defaultdict

WORD_LENGTH = 5
NUM_OF_TRIES = 6
HEBREW_LETTERS = "אבגדהוזחטיכלמנסעפצקרשת"
HEBREW_GUESSES = "hebrewwordlist.txt"
HEBREW_SOLUTIONS = "hebrewwordlist.txt"
ENGLISH_LETTERS = "abcdefghijklmnopqrstuvwxyz"
ENGLISH_GUESSES = "englishwordlist.txt"
ENGLISH_SOLUTIONS = "englishwordlist.txt"
FIRST_ENGLISH_GUESS = [('raise', 5.877), ('slate', 5.855), ('crate', 5.834), ('irate', 5.831), ('trace', 5.830)]
FIRST_HEBREW_GUESS = [('מילות', 5.985), ('מניות', 5.983), ('הורית', 5.960), ('מונית', 5.938), ('משרות', 5.935)]
FINAL_TO_REGULAR = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
REGULAR_TO_FINAL = {'כ': 'ך', 'מ': 'ם', 'נ': 'ן', 'פ': 'ף', 'צ': 'ץ'}
REGEX = "[{a}]{{1}}[{b}]{{1}}[{c}]{{1}}[{d}]{{1}}[{e}]{{1}}"
GREEN = '2'
YELLOW = '1'
GREY = '0'


def get_word_list(filename: str) -> list[str]:
    """
    get word list from a given filepath.
    :param filename:
    :return: list of words.
    """
    f = open(filename, "r", encoding="utf-8")
    wordlist = f.read().splitlines()
    f.close()
    return wordlist


def process_hebrew_word(word: str) -> str:
    """
    turn the last letter to finalised ("ot sofit") later or vice versa.
    :param word: a hebrew word
    :return: the word with a finalised / de-finalised last letter.
    """
    if word[-1] in REGULAR_TO_FINAL:
        return word[:-1] + REGULAR_TO_FINAL[word[-1]]
    elif word[-1] in FINAL_TO_REGULAR:
        return word[:-1] + FINAL_TO_REGULAR[word[-1]]
    else:
        return word


def atLeast_filter(word: str, filters: list[tuple[str, int]]) -> bool:
    return all(word.count(character) >= frequency
               for character, frequency in filters)


def exactly_filter(word: str, filters: list[tuple[str, int]]) -> bool:
    return all(word.count(character) == frequency
               for character, frequency in filters)


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


class WordleSolver:
    def __init__(self, hebrew: bool = False):
        self.patterns = {''.join(i): 0 for i in itertools.product("012", repeat=WORD_LENGTH)}
        self.hebrew = hebrew
        if self.hebrew:
            self.guesses = get_word_list(HEBREW_GUESSES)
            self.solutions = get_word_list(HEBREW_SOLUTIONS)
            self.first_words = FIRST_HEBREW_GUESS
        else:
            self.guesses = get_word_list(ENGLISH_GUESSES)
            self.solutions = get_word_list(ENGLISH_GUESSES)
            self.first_words = FIRST_ENGLISH_GUESS

    def filter_solutions(self, pattern: str, guess: str) -> None:
        """
        filter solution group based on the pattern user got from Wordle.
        :param pattern: a string of 5 {0,1,2}.
        :param guess: the guess
        """
        # letters that have to appear exactly number of times.
        if self.hebrew:
            letters = [HEBREW_LETTERS] * WORD_LENGTH
        else:
            letters = [ENGLISH_LETTERS] * WORD_LENGTH
        exactly = defaultdict(int)
        # letters that have to appear at least number of times
        at_least = defaultdict(int)
        greys = []
        for j in range(len(pattern)):
            if pattern[j] == GREY:
                letters[j] = letters[j].replace(guess[j], "")
                greys.append(guess[j])
            elif pattern[j] == YELLOW:
                if guess[j] in greys:
                    return
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
        for j in range(WORD_LENGTH):
            letters[j] = ''.join('' if c in greys else c for c in letters[j])
        atLeast_filters = [(k, v) for k, v in at_least.items() if v > 0]
        exactly_filters = [(k, v) for k, v in exactly.items() if v > 0]
        # filter out words that don't comply with possible chars for each letter.
        r = re.compile(
            REGEX.format(a=letters[0], b=letters[1], c=letters[2], d=letters[3], e=letters[4]))
        self.solutions = list(filter(r.match, self.solutions))
        # filter out based on atLeast and exactly letter count
        self.solutions = list(filter(lambda solution: atLeast_filter(solution, atLeast_filters), self.solutions))
        self.solutions = list(filter(lambda solution: exactly_filter(solution, exactly_filters), self.solutions))

    def calculate_entropy(self, guess: str) -> float:
        """
        calculate entropy of a given guess - how much information will be attained from guessing the guess in average.
        a score of 1 means halving the solution group once.
        :param guess:
        :return: the entropy of the guess.
        """
        self.patterns = dict.fromkeys(self.patterns, 0)
        # count how many solutions go to each pattern the guess can generate
        for solution in self.solutions:
            pattern = get_pattern(guess, solution)
            self.patterns[pattern] += 1
        solutions_count = len(self.solutions)
        entropy = 0
        for pattern in self.patterns:
            probability = self.patterns[pattern] / solutions_count
            if probability > 0:
                entropy += probability * math.log2(1 / probability)
        return entropy

    def virtual_solve(self, solution: str) -> int:
        """
        tests the program on a given solution - the program will try to solve the game.
        :param solution: given solution
        :return: how many guesses it took to solve the given solution.
                 -1 if program failed to find given solution in under 6 guesses.
        """
        for i in range(NUM_OF_TRIES):
            if len(self.solutions) == 1:
                return i + 1
            if i == 0:
                max_word = self.first_words[0][0]
            else:
                max_entropy = -1
                max_word = ""
                # find the word with the highest entropy and guess it.
                for word in self.guesses:
                    entropy = self.calculate_entropy(word)
                    if entropy > max_entropy:
                        max_word = word
                        max_entropy = entropy
                print(max_word)
            pattern = get_pattern(max_word, solution)
            if pattern == GREEN * WORD_LENGTH:
                return i + 1
            self.filter_solutions(pattern, max_word)
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
                return self.solutions[0], i + 1
            elif len(self.solutions) == 2:
                print("potential solutions are:\n", self.solutions)
            # the top guesses are pre-calculated for the first word.
            elif i == 0:
                print("Top guesses are:\n", self.first_words)
            # else, calculate what are the best cases and present them to the user.
            else:
                results = []
                for guess in self.guesses:
                    if self.hebrew:
                        guess = process_hebrew_word(guess)
                    results.append((guess, round(self.calculate_entropy(guess), 2)))
                results.sort(key=lambda x: x[1], reverse=True)
                print("Top guesses are:\n", results[:5])
            guess = input("Enter your guess:\n")
            # go from final letter to non-final letter.
            if self.hebrew:
                guess = process_hebrew_word(guess)
            pattern = input("Enter pattern: (0 for grey, 1 for yellow, 2 for green. i.e \'00112\')\n")
            if pattern == GREEN * WORD_LENGTH:
                return guess, i + 1
            self.filter_solutions(pattern, guess)
        return None, NUM_OF_TRIES


if __name__ == '__main__':
    solver = WordleSolver(True)
    print(solver.interactive_solve())
