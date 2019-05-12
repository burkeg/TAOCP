# sort random directed graphs so that isomorphic ones are grouped together
import pprint as pp
import random as rand
import itertools
import copy

base = 5

def solve():
    # generate random graphs
    numGraphs = 100
    randomGraphs = [intToAdjMat(x) for x in rand.sample(range(2**(base**2)), numGraphs)]
    graphSet = set()
    randomGraphs.sort(key=lambda adjMat:(tuple(sorted([sum(x) for x in adjMat])), tuple(sorted([sum(x) for x in flipped(adjMat)]))))
    randomGraphKeys = [(tuple(sorted([sum(x) for x in adjMat])), tuple(sorted([sum(x) for x in flipped(adjMat)]))) for adjMat in randomGraphs]
    streak = set()
    for i, key in enumerate(randomGraphKeys):
        if i==0:
            continue
        if key == randomGraphKeys[i-1]:
            streak.add(randomGraphs[i])
            streak.add(randomGraphs[i-1])
        else:
            if len(streak) != 0:
                print('Isomorphic group:')
                pp.pprint(streak)
            streak = set()
    if len(streak) != 0:
        print('Isomorphic group:')
        pp.pprint(streak)
    tst = 0

def testAllPermutations():
    for i in range(2**(base**2)):
    # for i in [316]:
        # adjMat = ((0, 1, 0, 0),
        #           (0, 0, 1, 1),
        #           (1, 0, 1, 1),
        #           (0, 1, 0, 0))
        # adjMat = [[1, 1, 1, 0],
        #           [0, 0, 0, 1],
        #           [1, 1, 0, 0],
        #           [0, 0, 0, 1]]
        adjMat= intToAdjMat(i)
        unmoddedVariants = list(genAllVariants(adjMat))
        sortedVariants = set()
        for i, variant in enumerate(unmoddedVariants):
            # sortedVariants.add(sortByBinValSrc(sortByNumDest(variant)))
            # sortedVariants.add(sortByNumDest(sortByBinValSrc(sortByNumDest(variant))))
            # sortedVariants.add(sortByBinValSrc(sortByNumDest(variant)))
            # sortedVariants.add(sortByNumSrc(sortByBinValSrc(sortByNumDest(variant))))
            # sortedVariants.add(sortByBinValDest(sortByNumSrc(sortByBinValSrc(sortByNumDest(variant))))) # good
            # sortedVariants.add(sortByBinValDest(sortByBinValSrc(sortByBinValDest(sortByBinValSrc(variant)))))
            # sortedVariants.add(sortByBinValSrc(sortByNumDest(variant)))
            # sortedVariants.add(variant)
            # sortedVariants.add(sortByBinValSrc(sortByNumDest(sortByBinValDest(variant))))
            # sortedVariants.add(sortByBinValSrc(sortByNumSrc(sortByNumDest(sortByBinValDest(variant)))))
            # sortedVariants.add(sortByNumSrc(sortByBinValSrc(sortByNumDest(sortByBinValDest(variant)))))
            # sortedVariants.add(sortByBinValSrc(sortByBinValDest(variant)))
            # newSorted = sortByBinValDest(sortByNumSrc(sortByBinValSrc(sortByNumDest(variant))))
            sortedRowSums = tuple(sorted([sum(x) for x in adjMat]))
            sortedColSums = tuple(sorted([sum(x) for x in flipped(adjMat)]))
            newSorted = (sortedRowSums, sortedColSums)
            if len(sortedVariants) > 0 and newSorted not in sortedVariants:
                print('here')
            sortedVariants.add(newSorted) # good

        if len(sortedVariants) > 1:
            print('----------')
            pp.pprint(adjMat)
            pp.pprint(sortedVariants)
        else:
            pass
            print(len(sortedVariants))
    tmp = 0

def intToAdjMat(a):
    a = int(a)
    mat = []
    for i in range(base**2):
        if i % base == 0:
            mat.append([0]*base)
        mat[i//base][i % base] = 0 if (a >> i) % 2 == 0 else 1
    return tuple([tuple(x) for x in mat])


def genAllVariants(adjMat):
    # colsSwitched = list(itertools.permutations(flipped(adjMat)))
    # bothSwitched = set()
    # for colSwitched in colsSwitched:
    #     bothSwitched = bothSwitched.union(set(colsSwitched))
    #     # bothSwitched = bothSwitched.union(set([flipped(x) for x in itertools.permutations(flipped(colSwitched))]))
    perms = list(itertools.permutations(range(base)))
    bothSwitched = []
    for perm in perms:
        # swap rows
        tmp = [adjMat[x] for x in perm]
        # swap cols
        tmp = flipped([flipped(tmp)[x] for x in perm])
        bothSwitched.append(tmp)

    return bothSwitched

def sortByNumDest(adjMat, reverse=True):
    return tuple(sorted(adjMat, key=sum, reverse=reverse))

def sortByNumSrc(adjMat, reverse=True):
    return flipped(sorted(flipped(adjMat), key=sum, reverse=reverse))

def sortByBinValDest(adjMat, reverse=True):
    return tuple(sorted(adjMat, key=lambda lst: sum([x*2**-i for i,x in enumerate(lst)]), reverse=reverse))

def sortByBinValSrc(adjMat, reverse=True):
    return flipped(sorted(flipped(adjMat), key=lambda lst: sum([x*2**-i for i,x in enumerate(lst)]), reverse=reverse))


def flipped(adjMat):
    flipped = [list(x) for x in adjMat]
    for i in range(len(adjMat)):
        for j in range(len(adjMat[i])):
            flipped[j][i] = adjMat[i][j]
    flipped = tuple([tuple(x) for x in flipped])
    return flipped



if __name__ == "__main__":
    solve()