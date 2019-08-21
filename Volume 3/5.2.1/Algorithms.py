import sys
import pyoeis
import random as rand
import copy
from SortUtils import SortUtils
# https://buildmedia.readthedocs.org/media/pdf/pyoeis/latest/pyoeis.pdf

def StraightInsertionSort(R, key=lambda x:x):
    N = len(R)
    for j in range(1, N):
        i = j-1
        currKey = key(R[j])
        currVal = R[j]
        while currKey < key(R[i]):
            R[i+1]= R[i]
            i -= 1
            if i < 0:
                break
        R[i+1] = currVal
    return R

def ShellSort(R, hLst, key=lambda x:x):
    # R: Records
    # increments: The sequence of increments used to control the sorting process
    # N: Number of records
    # s: index of
    N = len(R)
    for s in reversed(range(len(hLst))):
        h = hLst[s]
        for j in range(h-1, N):
            i = j-h
            currKey = key(R[j])
            currVal = R[j]
            while currKey < key(R[i]):
                R[i+h]= R[i]
                i -= h
                if i < 0:
                    break
            R[i+h] = currVal
    return R


def solve():
    OEIS = pyoeis.client.OEISClient()
    incrementList = OEIS.get_by_id('A003586').unsigned(55)
    unsorted = SortUtils.randomIntegerArray(100)
    unsorted = [rand.randint(50,55) for x in range(200000)]
    # unsorted = [rand.randint(50,60) for x in range(500)]
    # unsorted = [5,5,5,5,6,2,3,0]
    # [503, 87, 512, 61, 908, 170, 897, 275, 653, 426, 154, 509, 612, 677, 765, 703]
    # unsorted = SortUtils.KnuthExample()
    sortedArr = ShellSort(unsorted, incrementList)
    # sortedArr = StraightInsertionSort(unsorted)
    for a, b in zip(sortedArr, sorted(unsorted)):
        if a != b:
            break
    else:
        print('Matches:', sortedArr)
        return
    print("No match.")

if __name__ == '__main__':
    solve()