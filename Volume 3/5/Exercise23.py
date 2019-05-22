# Find all k-cliques of people in a group of 4096 people, all of which know roughly 100 others
# Can assume no clique is over size
import pprint as pp
import random as rand
import itertools
import copy

def solve():
    numPeople = 100
    acquaintencesPerPerson = 30
    friendAdjList = [rand.sample([person for person in range(numPeople) if person != me], acquaintencesPerPerson) for me in range(numPeople)]
    friendAdjList = [set() for _ in range(numPeople)]
    for me in range(numPeople):
        # a valid choice for a new acquantance is someone who doesn't already know me that isn't also me
        valid = set([person for person in range(numPeople) if person != me]).symmetric_difference(friendAdjList[me])
        for otherPerson in rand.sample(list(valid), int(acquaintencesPerPerson/2)):
            friendAdjList[otherPerson].add(me)
            friendAdjList[me].add(otherPerson)
    friendAdjList = [[x for x in y] for y in friendAdjList]
    # friendAdjMatrix = [[1 if x in friendAdjList[curr] else 0 for x in range(numPeople)] for curr in range(numPeople)]
    print(findAllKCliques(friendAdjList, 4))
    print(sum([len(x) for x in friendAdjList])/len(friendAdjList))
    tmp = 0
    pass

def findAllKCliques(friendList, k):
    numPeople = len(friendList)

    cliqueSet = set()
    # base case
    if k == 2:
        for person, friends in enumerate(friendList):
            for friend in friends:
                cliqueSet.add(frozenset([person, friend]))
        return cliqueSet
        pass
    else:
        k_minus_one_cliques = findAllKCliques(friendList, k-1)
        # build up the list of k-cliques from k-1-cliques
        for clique in k_minus_one_cliques:
            sharedNodes = set(friendList[next(iter(clique))])
            # for each node in the clique, see if there is a node that all clique members share
            for neighbors in [set(friendList[x]) for x in clique]:
                sharedNodes = sharedNodes.intersection(neighbors)
            # for each node that is a neighbor with every other node in the clique, generate a new k-clique
            for node in sharedNodes:
                cliqueSet.add(frozenset(clique.union(set([node]))))
        return cliqueSet


    tmp = 0
    pass

if __name__ == "__main__":
    solve()