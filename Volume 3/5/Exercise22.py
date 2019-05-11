import pprint as pp
import random as rand
import itertools
import copy

def solve():
    adjMat = ((0, 1, 0, 0),
              (0, 0, 1, 1),
              (1, 0, 1, 1),
              (0, 1, 0, 0))
    # adjMat = [[1, 1, 1, 0],
    #           [0, 0, 0, 1],
    #           [1, 1, 0, 0],
    #           [0, 0, 0, 1]]
    pp.pprint(adjMat)
    print('by dest')
    pp.pprint(sortByNumDest(adjMat))
    print('by src')
    pp.pprint(sortByNumSrc(adjMat))
    print('by dest bin')
    pp.pprint(sortByBinValDest(adjMat))
    print('by src bin')
    pp.pprint(sortByBinValSrc(adjMat))
    genAllVariants(adjMat)

def genAllVariants(adjMat):
    colsSwitched = itertools.permutations(adjMat)
    bothSwitched = set()
    for colSwitched in colsSwitched:
        bothSwitched = bothSwitched.union(set(itertools.permutations(flipped(colSwitched))))
    return bothSwitched

def sortByNumDest(adjMat):
    return sorted(adjMat, key=sum, reverse=True)

def sortByNumSrc(adjMat):
    return flipped(sorted(flipped(adjMat), key=sum, reverse=True))

def sortByBinValDest(adjMat):
    return sorted(adjMat, key=lambda lst: sum([x*2**-i for i,x in enumerate(lst)]), reverse=True)

def sortByBinValSrc(adjMat):
    return flipped(sorted(flipped(adjMat), key=lambda lst: sum([x*2**-i for i,x in enumerate(lst)]), reverse=True))


def flipped(adjMat):
    flipped = [list(x) for x in adjMat]
    for i in range(len(adjMat)):
        for j in range(len(adjMat[i])):
            flipped[j][i] = adjMat[i][j]
    flipped = tuple([tuple(x) for x in flipped])
    return flipped



if __name__ == "__main__":
    solve()