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
        for word in words:
            self._add_word(cur_word, word)
            cur_word = word
        self._add_word(cur_word, self.EOL)

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

        if word is None:
            word = self.SOL

        while word != self.EOL:
            # print(word, ','.join(hex(ord(w)) for w in word))
            if word != self.SOL:
                phrase.append(word)

            word = self.get_word(word)
            if word == self.EOL and len(phrase) < min_length:
                old_word = phrase[-1]
                if len(self.words[old_word]) == 1:
                    word = self.SOL
                else:
                    word = old_word
                    phrase.pop()

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