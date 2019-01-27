import os
import os.path
import json
import re
import glob
import string
import gzip
import pickle

from contextlib import contextmanager

from model import Chain


@contextmanager
def load_chain(filename):
    if not os.path.exists(filename):
        with gzip.open(filename, 'w') as f:
            pickle.dump(Chain.create_empty().to_dict(), f)

    with gzip.open(filename, 'r') as f:
        data = pickle.load(f)
    chain = Chain.load_from_dict(data)
    try:
        yield chain
    finally:
        ...
        # if chain.is_changed:
        #     with gzip.open(filename, 'w') as f:
        #         pickle.dump(chain.to_dict(), f, protocol=pickle.HIGHEST_PROTOCOL)


def _islatin(s):
    for c in s:
        if c in string.ascii_lowercase:
            return True
    else:
        return False


def _filter_word(words):
    EXTRA_LINE_END = '!?'
    REMOVE_SET = (set('•+…:«»') | set(string.punctuation)) - set(EXTRA_LINE_END)
    CONVERT_TO_SPACE = '-–— \t\n'
    TRANSLATE_TABLE = {ord(c): None for c in REMOVE_SET}
    TRANSLATE_TABLE.update({ord(c): ' ' for c in CONVERT_TO_SPACE})
    TRANSLATE_TABLE[ord('ё')] = 'е'

    res = []
    words = words[:]
    while words:
        word = words.pop()

        word = word.translate(TRANSLATE_TABLE)
        word = word.strip()
        word = word.lower()

        if len(word) == 0 or len(word) > 20:
            continue
        if len(word) == 1 and len(words) == 1:
            return None

        if word[-1] in EXTRA_LINE_END and len(word) != 1:
            words.insert(0, word[-1])
            word = word[:-1]

        if word in ('стр', 'изд'):
            continue
        if _islatin(word):
            continue
        if len(word) == 1 and word not in 'укваояис':
            continue

        res.append(word)
    return res


def parse_fb2(filename):
    try:
        with open(filename, 'r') as f:
            data = f.read()
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='cp1251') as f:
            data = f.read()

    return re.sub('<[^<]+>', "", data)


def filter_data(data):
    res = []
    for l in data:
        l = l.strip()
        words = l.split(' ')

        words = _filter_word(words)
        if words is None:
            continue

        res.append(' '.join(words))
    return res


def add_phrase(chain, lines):
    for phrase in lines:
        if len(' '.join(phrase)) == 0:
            continue
        chain.add_phrase(phrase)


def add_all_text_from_dir(directory, chain):
    for file in glob.glob(os.path.join(directory, '*.fb2')):
        print(file)
        text = parse_fb2(file)
        add_phrase(chain, filter_data(text.split('.')))

    print('shkvar')
    with open('data/shkvar.txt', 'r') as f:
        add_phrase(chain, (filter_data(f.read().split('&^**+|'))))

    print('russian_news')
    with open('data/russian_news_orig.txt', 'r') as f:
         i = 0
         for line in f:
             add_phrase(chain, filter_data((line,)))
             i += 1
             if i % 1000 == 0:
                 print(i)


def main():
    with load_chain('data.bin') as chain:
        add_all_text_from_dir('data', chain)
        print('Loaded. Total data: {}\n'.format(chain.size))

        for _ in range(6):
            print(chain.get_full_phrase(min_length=6))
            print()
        print(chain.get_full_phrase(min_length=6))

        try:
            while True:
                line = input('\n> ')
                data = filter_data([line])
                if not data:
                    continue
                chain.add_phrase(data[0])
                print('\n' + chain.get_full_phrase(data[0].split(' ')[-1], min_length=6))

        except (KeyboardInterrupt, EOFError):
            print('Пока.')

if __name__ == '__main__':
    main()
