# Given 2,999,999 pairs of unique contiguous links in random order, reconstruct the original
# sequence with <1000 passes through the data
import pprint as pp
import random as rand
import itertools
import copy
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
        shuffle(sequence)
        for i, j in zip(range(self.size-1), range(1, self.size)):
            self.cards.append(Card(sequence[i], sequence[j]))
        self.originalSequence = copy.deepcopy(self.cards)
        shuffle(self.cards)


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

# Knuth Shuffle A.K.A. Fisher-Yates Shuffle
def shuffle(lst):
    for i in range(len(lst)-1):
        j = rand.randint(i, len(lst) - 1)
        tmp = lst[i]
        lst[i] = lst[j]
        lst[j] = tmp



def solveWithCheating():
    # 100,000 10: 2515
    # 100,000 1: 42070
    Coalescer(Deck(10000), maxNucleationSites=100)



if __name__ == "__main__":
    # rand.seed(0)
    solveWithCheating()

4