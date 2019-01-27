import random

from collections import defaultdict


class Chain:
    EOL = '|=|'
    SOL = '<->'

    def __init__(self, words):
        self.words = words
        self.total_words = {k: sum(num for num in v.values()) for k, v in self.words.items()}

        self.is_changed = False

    def _add_word(self, word, next_word):
        d = self.words[word]

        if next_word in d:
            d[next_word] += 1
        else:
            d[next_word] = 1

        if word not in self.total_words:
            self.total_words[word] = 0

        self.total_words[word] += 1

    def add_phrase(self, words):
        words = words.split(' ')

        if not words:
            return

        cur_word = self.SOL
        it = iter(words)
        cur_word2 = next(it)
        self._add_word(cur_word, cur_word2)
        for word in it:
            self._add_word((cur_word, cur_word2), word)
            cur_word = cur_word2
            cur_word2 = word
        self._add_word((cur_word, cur_word2), self.EOL)

        if not self.is_changed:
            self.is_changed = True

    def get_word(self, word):
        rnd = random.randint(0, self.total_words[word] - 1)
        cur = 0

        for word, num in self.words[word].items():
            if cur <= rnd < cur + num:
                return word
            cur += num

    def get_full_phrase(self, word=None, min_length=0):
        phrase = []

        prev_word = self.SOL
        if word is None:
            word = self.get_word(prev_word)
        next_word = word

        while next_word != self.EOL:
            # print(word, ','.join(hex(ord(w)) for w in word))
            if next_word not in (self.SOL, self.EOL):
                phrase.append(next_word)

            next_word = self.get_word((prev_word, word))

            if next_word == self.EOL and len(phrase) < min_length:
                if len(self.words[(prev_word, word)]) == 1:
                    prev_word = self.SOL
                    word = self.get_word(prev_word)
                    next_word = word
                next_word = self.SOL
            else:
                prev_word = word
                word = next_word

        phrase[0] = phrase[0].capitalize()
        return ' '.join(phrase) + '.'


    def to_dict(self):
        return {
            'words': self.words
        }

    def is_empty(self):
        return len(self.words) == 0

    @property
    def size(self):
        return len(self.words)

    @staticmethod
    def create_empty():
        return Chain(defaultdict(dict))

    @classmethod
    def load_from_dict(cls, data):
        return Chain(defaultdict(dict, data['words']))
