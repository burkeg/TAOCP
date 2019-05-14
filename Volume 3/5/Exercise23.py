# Find all k-cliques of people in a group of 4096 people, all of which know roughly 100 others
# Can assume no clique is over size
import pprint as pp
import random as rand
import itertools
import copy

def solve():
    numPeople = 30
    acquaintencesPerPerson = 6
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
    print(findAllKCliques(friendAdjList, 3))
    print(sum([len(x) for x in friendAdjList])/len(friendAdjList))
    tmp = 0
    pass

def findAllKCliques(friendList, k):
    numPeople = len(friendList)

    # base case
    if k == 3:
        cliqueSet = set()
        for curr in range(numPeople):
            # sort rows so curr's neighbor is at the top
            currNeighbors = sorted(friendList, key=lambda x: curr in x, reverse=True)
            for neighborList in [friendList[x] for ]
            while
        pass
    else:
        k_minus_one_cliques = findAllKCliques(friendList, k-1)
        # build up the list of k-cliques from k-1-cliques

    tmp = 0
    pass

if __name__ == "__main__":
    solve()