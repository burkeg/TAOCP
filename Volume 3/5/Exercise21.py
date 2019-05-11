import pprint as pp
import random as rand
import itertools
# find a set of 5 letter anagrams with 10 words in them other than the one in the book
# https://github.com/dwyl/english-words
def load_words():
    with open('words_alpha.txt') as word_file:
        valid_words = set(word_file.read().split())

    return valid_words


def solve(anagramSize=5, minCluster=10):
    words = load_words()
    words = sorted([(x, ''.join(sorted(list(x)))) for x in words], key=lambda x: x[1])
    groups = []
    for key, group in itertools.groupby(words, lambda x: x[1]):
        nextGroup = [thing for thing in group if len(thing[0]) == anagramSize]
        if len(nextGroup) >= minCluster:
            groups.append(nextGroup)
    groups = sorted([(len(x), x) for x in groups], key= lambda x: x[0])
    for thing in groups:
        pp.pprint(thing)



if __name__ == "__main__":
    # for x in range(8):
    #     for y in range(8):
    #         print(x, y, getDistance(x,y))
    solve(anagramSize=8, minCluster=2)