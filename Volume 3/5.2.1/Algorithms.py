import sys
import random as rand
import copy
sys.path.append(r'C:\Users\gabburke\Documents\Personal\TAOCP\Volume 3\Sort Utils')
from SortUtils import SortUtils

def StraightInsertionSort(R, key=lambda x:x):
    K = key
    N = len(R)
    for j in range(1, N):
        i = j-1
        currKey = K(R[j])
        currVal = R[j]
        while currKey < K(R[i]):
            R[i+1]= R[i]
            i -= 1
            if i < 0:
                break
        R[i+1] = currVal
    return R


def solve():
    unsorted = SortUtils.randomIntegerArray(10)
    # unsorted = [rand.randint(50,60) for x in range(500)]
    # unsorted = [5,5,5,5,6,2,3,0]
    # [503, 87, 512, 61, 908, 170, 897, 275, 653, 426, 154, 509, 612, 677, 765, 703]
    # unsorted = SortUtils.KnuthExample()
    sortedArr = StraightInsertionSort(unsorted)
    for a, b in zip(sortedArr, sorted(unsorted)):
        if a != b:
            break
    else:
        print(sortedArr)
        return
    print("Don't match.")

if __name__ == '__main__':
    solve()