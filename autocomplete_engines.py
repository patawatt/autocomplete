"""Autocomplete engines

=== Module description ===
This file contains code for the three different autocomplete engines:

- LetterAutocompleteEngine   -> generates a list of words that start with a
                                user-input character string.
- SentenceAutocompleteEngine -> generates a list of sentences that start with
                                a user-input character string.
- MelodyAutocompleteEngine   -> generates a list of melodies that start with a
                                melody input by the user as a character string.

"""
from __future__ import annotations
import csv
from typing import Any, Dict, List, Optional, Tuple

from melody import Melody
from prefix_tree import SimplePrefixTree, CompressedPrefixTree


################################################################################
# Text-based Autocomplete Engines
################################################################################
class LetterAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few letters.

    The *prefix sequence* for a string is the list of characters in the string.
    This can include space characters.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters.

    === Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a text file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Each line of the specified file counts as one input string.
        Note that the line may or may not contain spaces.
        Each string will be sanitized, and if the resulting string contains
        at least one alphanumeric character, it is inserted into the
        Autocompleter.

        *Lines that do not contain at least one
         alphanumeric character will be skipped*

        When each string is inserted, it is given a weight of one.
        Note that it is possible for the same string to appear on more than
        one line of the input file; this would result in that string getting
        a larger weight (because of how Autocompleter.insert works).
        """
        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree(config['weight_type'])
        elif config['autocompleter'] == 'compressed':
            self.autocompleter = CompressedPrefixTree(config['weight_type'])

        # Opens the file and iterates over the lines of the file
        with open(config['file'], encoding='utf8') as f:
            for line in f:
                prefix = [c.lower() for c in line if c.isalnum() or c == ' ']
                clean = ''.join(prefix)
                if len(clean) >= 1:
                    self.autocompleter.insert(clean, 1.0, prefix)

    def autocomplete(self, prefix: str,
                     limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        ordered in non-increasing weight.

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string will be transformed into a list
        of letters before being passed to the Autocompleter.

        Preconditions:
            limit is None or limit > 0
            <prefix> contains only lowercase alphanumeric characters and spaces
        """
        prefix_lst = [c for c in prefix]
        return self.autocompleter.autocomplete(prefix_lst, limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix string.

        Note that the given prefix string will be transformed into a list
        of letters before being passed to the Autocompleter.

        Precondition: <prefix> contains only lowercase alphanumeric characters
                      and spaces.
        """
        prefix_lst = [c for c in prefix]
        self.autocompleter.remove(prefix_lst)


class SentenceAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few words.

    A *word* is a string containing only alphanumeric characters.
    The *prefix sequence* for a string is the list of words in the string
    (separated by whitespace). The words themselves do not contain spaces.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters.

    === Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a CSV file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Precondition:
        The given file is a *CSV file* where each line has two entries:
            - the first entry is a string
            - the second entry is the a number representing the weight of that
              string

        Note that the line may or may not contain spaces.
        Each string will be sanitized, and if the resulting string contains
        at least one word, it is inserted into the Autocompleter.

        *Skip lines that do not contain at least one alphanumeric character!*

        When each string is inserted, it is given the weight specified on the
        line from the csv file.
        Note that it is possible for the same string to appear on more than
        one line of the input file; this would result in that string getting
        a larger weight.
        """

        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree(config['weight_type'])
        elif config['autocompleter'] == 'compressed':
            self.autocompleter = CompressedPrefixTree(config['weight_type'])

        with open(config['file']) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                dirty, weight_str = line[0], line[1]
                chars = [c.lower() for c in dirty if c.isalnum() or c == ' ']
                clean = ''.join(chars)
                prefix = clean.split()
                weight = float(weight_str)
                if len(clean) >= 1:
                    self.autocompleter.insert(clean, weight, prefix)

    def autocomplete(self, prefix: str,
                     limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        ordered in non-increasing weight.

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Preconditions:
            limit is None or limit > 0
            <prefix> contains only lowercase alphanumeric characters and spaces
        """
        prefix_lst = prefix.split()
        return self.autocompleter.autocomplete(prefix_lst, limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Precondition: <prefix> contains only lowercase alphanumeric characters
                      and spaces.
        """
        prefix_lst = prefix.split()
        self.autocompleter.remove(prefix_lst)


################################################################################
# Melody-based Autocomplete Engines
################################################################################
class MelodyAutocompleteEngine:
    """An autocomplete engine that suggests melodies based on a few intervals.

    The values stored are Melody objects, and the corresponding
    prefix sequence for a Melody is its interval sequence.

    Because the prefix is based only on interval sequence and not the
    starting pitch or duration of the notes, it is possible for different
    melodies to have the same prefix.

    # === Private Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a CSV file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Precondition:
        The given file is a *CSV file* where each line has the following format:
            - The first entry is the name of a melody (a string).
            - The remaining entries are grouped into pairs
              where the first number in each pair is a note pitch,
              and the second number is the corresponding duration.

            HOWEVER, there may be blank entries (stored as an empty string '');
            as soon as you encounter a blank entry, stop processing this line
            and move onto the next line the CSV file.

        Each melody is be inserted into the Autocompleter with a weight of 1.
        """
        # We haven't given you any starter code here! You should review how
        # you processed CSV files on Assignment 1.

        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree(config['weight_type'])
        elif config['autocompleter'] == 'compressed':
            self.autocompleter = CompressedPrefixTree(config['weight_type'])

        with open(config['file']) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:

                prefix = []
                song = []
                i = 1
                song.append((int(line[i]), int(line[i + 1])))
                i += 2
                while line[i] != '':
                    song.append((int(line[i]), int(line[i + 1])))
                    prefix.append(int(line[i])-int(line[i - 2]))
                    i += 2
                    try:
                        isinstance(line[i], str)
                    except IndexError:
                        break
                melody = Melody(line[0], song)
                self.autocompleter.insert(melody, 1.0, prefix)

    def autocomplete(self, prefix: List[int],
                     limit: Optional[int] = None) -> List[Tuple[Melody, float]]:
        """Return up to <limit> matches for the given interval sequence.

        The return value is a list of tuples (melody, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given interval sequence.

        Precondition:
            limit is None or limit > 0
        """

        return self.autocompleter.autocomplete(prefix, limit)

    def remove(self, prefix: List[int]) -> None:
        """Remove all melodies that match the given interval sequence.
        """

        self.autocompleter.remove(prefix)


###############################################################################
# Sample runs
###############################################################################
def sample_letter_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the letter autocomplete engine."""
    engine = LetterAutocompleteEngine({
        # NOTE: you should also try 'data/lotr.txt' for the file.
        'file': 'data/lotr.txt',
        'autocompleter': 'compressed',
        'weight_type': 'sum'
    })
    word_result = engine.autocomplete('frodo d', 20)
    print(word_result)
    return word_result


def sample_sentence_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the sentence autocomplete engine."""
    engine = SentenceAutocompleteEngine({
        'file': 'data/google_searches.csv',
        'autocompleter': 'compressed',
        'weight_type': 'sum'
    })
    sentence_result = engine.autocomplete('how to', 20)
    print(sentence_result)
    return sentence_result


def sample_melody_autocomplete() -> None:
    """A sample run of the melody autocomplete engine."""
    engine = MelodyAutocompleteEngine({
        'file': 'data/songbook.csv',
        'autocompleter': 'compressed',
        'weight_type': 'sum'
    })
    melodies = engine.autocomplete([0, 0], 20)

    names_list = []
    for i in melodies:
        names_list.append((i[0].name, i[1]))
    print(names_list)
    for melody, _ in melodies:
        melody.play()

    return melodies, names_list


if __name__ == '__main__':
    # import python_ta
    # python_ta.check_all(config={
    #     'allowed-io': ['__init__'],
    #     'extra-imports': ['csv', 'prefix_tree', 'melody']
    # })

    # This is used to increase the recursion limit so that your sample runs
    # work even for fairly tall simple prefix trees.
    import sys
    sys.setrecursionlimit(5000)
    # sample_melody_autocomplete()
    result = sample_melody_autocomplete()

