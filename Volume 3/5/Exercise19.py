import pprint as pp
import random as rand
# Given a million distinct 30-bit binary words what's a good way to find all complementary pairs present

def solve():
    maxWord = 2**30-1
    numWords = 1_000_000
    words = rand.sample(range(maxWord+1), numWords)

    # sort the words
    words.sort()
    i = 0
    j = len(words)-1
    pairs = []
    while i < j:
        total = words[i] + words[j]
        if total > maxWord:
            j -= 1
        elif total < maxWord:
            i += 1
        else:
            pairs.append((words[i], words[j]))
            i += 1
            j -= 1
    pp.pprint(pairs)

if __name__ == "__main__":
    solve()