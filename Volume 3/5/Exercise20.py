import pprint as pp
import random as rand
# Given 1000 30-bit binary words, find all pairs such that x_i = x_j except in at most 2 bit positions

def solve():
    maxWord = 2**30-1
    numWords = 1_000
    words = rand.sample(range(maxWord+1), numWords)

    # sort the words
    words.sort()
    pairs = [(words[i], words[j]) for i in range(numWords) for j in range(i+1,numWords) if getDistance(words[i], words[j]) <= 2]
    pp.pprint(pairs)
    for a,b in pairs:
        print("{0:b}".format(a))
        print("{0:b}".format(b))
        print('')

def getDistance(a, b, limit = 2):
    count = 0
    tmp = a^b
    while tmp:
        tmp &= tmp - 1
        count+=1
        if count > limit:
            break
    return count


if __name__ == "__main__":
    # for x in range(8):
    #     for y in range(8):
    #         print(x, y, getDistance(x,y))
    solve()