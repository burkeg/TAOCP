# Given 2,999,999 pairs of unique contiguous links in random order, reconstruct the original
# sequence with <1000 passes through the data
import pprint as pp
import random as rand
import itertools
import copy
from SortUtils import SortUtils
from llist import dllist, dllistnode


class Card:
    def __init__(self, me, front):
        self.me = me
        self.front = front

    def __str__(self):
        return str((self.me, self.front))

class Deck:
    def __init__(self, size):
        self.size = size
        self.cards = []
        self.originalSequence = None
        self.createDeck()

    def __len__(self):
        return len(self.cards)

    def createDeck(self):
        self.cards = []
        sequence = list(range(self.size))
        SortUtils.shuffle(sequence)
        for i, j in zip(range(self.size-1), range(1, self.size)):
            self.cards.append(Card(sequence[i], sequence[j]))
        self.originalSequence = copy.deepcopy(self.cards)
        SortUtils.shuffle(self.cards)


class Coalescer:
    def __init__(self, deck, maxNucleationSites = 2):
        self.deck = deck
        self.maxNucleationSites = maxNucleationSites
        self.nucleationSites = [None] * self.maxNucleationSites
        self.visited = [False] * len(self.deck)
        self.recoverSequence()

    def addNewSite(self, index):
        for i in range(self.maxNucleationSites):
            if self.nucleationSites[i] is None:
                if self.visited[index] == False:
                    self.nucleationSites[i] = dllist([self.deck.cards[index]])
                    return
                else:
                    raise Exception('Card already accounted for.')
        raise Exception('Tried to add a new nucleation site but all were already filled.')

    def attemptNucleate(self, index):
        currCard = self.deck.cards[index]
        for site in self.nucleationSites:
            if site is not None:
                # The current person belongs to the back of this line
                if site.first.value.me == currCard.front:
                    site.appendleft(currCard)
                    self.visited[index] = True
                    return True
                # The current person belongs to the front of this line
                elif site.last.value.front == currCard.me:
                    site.appendright(currCard)
                    self.visited[index] = True
                    return True
                # The current person doesn't belong to this line
                else:
                    pass
            # there's room for a new nucleation site
            else:
                self.addNewSite(index)
                self.visited[index] = True
                return True
        return False

    def mergeExistingSites(self):
        while True:
            found = False
            for A in range(self.maxNucleationSites-1):
                if self.nucleationSites[A] is None:
                    continue
                for B in range(1, self.maxNucleationSites):
                    if self.nucleationSites[B] is None:
                        continue
                    # first person in line A belongs to the back of line B
                    if self.nucleationSites[A].last.value.front == self.nucleationSites[B].first.value.me:
                        self.nucleationSites[A].extendright(self.nucleationSites[B])
                        self.nucleationSites[B] = None
                        found = True
                    # last person in line A belongs to the front of line B
                    elif self.nucleationSites[A].first.value.me == self.nucleationSites[B].last.value.front:
                        self.nucleationSites[B].extendright(self.nucleationSites[A])
                        self.nucleationSites[A] = None
                        # break out of the inner loop since A no longer exists
                        break
                        found = True
            if not found:
                break

    def recoverSequence(self):
        numPasses = 0
        numFound = 0
        while numFound < len(self.deck):
            for index in range(len(self.deck)):
                # https://hearthstone.gamepedia.com/Nat_Pagle
                # Ha! Caught one!
                # short-circuit and skip attempt if node already visited
                if not self.visited[index] and self.attemptNucleate(index):
                    numFound += 1
                    self.mergeExistingSites()
                # pp.pprint([[str(y) for y in x] for x in self.nucleationSites if x is not None])
            numPasses += 1
            print(numFound, numPasses)

def solveWithCheating():
    # 100,000 10: 2515
    # 100,000 1: 42070
    Coalescer(Deck(10000), maxNucleationSites=100)

def getRandSequence(size):
    lst = SortUtils.randomIntegerArray(size-1)
    return [(x, x+1) for x in lst]

def renameRandSequence(initSeq, doNothing=False):
    if doNothing:
        return initSeq, list(range(len(initSeq)+1))
    N = len(initSeq)
    key = SortUtils.randomIntegerArray(N+1)
    newSeq = [(key[x[0]], key[x[1]]) for x in initSeq]
    return newSeq, key

def getPairsFromFirstIteration(sortedByFirst, sortedBySecond):
    firstPos = 0
    secondPos = 0
    twoSpaced = []
    lastPair = None
    secondHighest = None
    highest = sortedByFirst[0][0]
    foundFirst = None
    foundSecond = None
    allKeys = set()
    for front, back in sortedByFirst:
        allKeys.add(front)
        allKeys.add(back)
    highest = max(allKeys)
    allKeys.remove(highest)
    secondHighest = max(allKeys)
    # the pair (x_N-1, x_N) is the last person in line
    # the pairs (N-1, x_N-1) and (N, x_N) are saved
    while firstPos < len(sortedByFirst) and secondPos < len(sortedBySecond):
        # Found a pair (x_i, x_i+2)
        if sortedByFirst[firstPos][0] == sortedBySecond[secondPos][1]:
            twoSpaced.append((sortedBySecond[secondPos][0], sortedByFirst[firstPos][1]))
            firstPos += 1
            secondPos += 1
        elif sortedByFirst[firstPos][0] < sortedBySecond[secondPos][1]:
            foundFirst = firstPos
            firstPos += 1
        elif sortedByFirst[firstPos][0] > sortedBySecond[secondPos][1]:
            lastPair = sortedBySecond[secondPos]
            foundSecond = secondPos
            secondPos +=1

    if lastPair == None:
        # If we couldn't find the last Pair in our first pass, then by coincidence N = x_N
        # In this case, the last person of the list of people sorted by first will not be
        # the the "largest" name
        lastPair = sortedBySecond[secondPos]

    return (twoSpaced, lastPair, (secondHighest, lastPair[0]), (highest, lastPair[1]))

def solve():
    initSequence, key = renameRandSequence(getRandSequence(10), doNothing=False)
    print(initSequence)
    print(key)
    sortedByFirst = sorted(initSequence, key=lambda x:x[0])
    sortedBySecond = sorted(initSequence, key=lambda x:x[1])

    firstFile = getPairsFromFirstIteration(sortedByFirst, sortedBySecond)
    twoSpaced = firstFile[0]
    lastPair = firstFile[1]
    secondHighestLast = firstFile[2]
    highestLast = firstFile[3]
    print(firstFile)
    print(sortedByFirst)
    print(sortedBySecond)
    t = 2
    F = twoSpaced
    G = sorted(F, key=lambda x:x[1])
    H = sorted(F, key=lambda x:x[0])
    while 2*t < len(F):
        Fp = []
        Gp = []
        Hp = []
        Fpos = 0
        Gpos = 0
        Hpos = 0
        while Fpos < len(F):
            x = F[Fpos][0]
            xp = F[Fpos][1]
            y = G[Fpos][0]
            yp = G[Fpos][1]
            z = H[Fpos][0]
            zp = H[Fpos][1]
            if xp == z:
                Fp.append((x, xp))
                Fpos += 1
                Hpos += 1
            elif xp == yp:
                Gp.append((y-t, x))
                Fpos +=1
                Gpos += 1
            elif xp > yp:
                Gpos += 1
            elif xp > z:
                Hpos += 1
        t *= 2
        F = Fp
        G = sorted(G + Gp, key=lambda x: x[1])
    G = sorted(G, key=lambda x:x[0])

    return


if __name__ == "__main__":
    rand.seed()
    solve()

4