import sys
import random as rand
import copy
sys.path.append(r'C:\Users\gabburke\Documents\Personal\TAOCP\Volume 3\SortUtils')
from SortUtils import SortUtils
from Algorithm_C import ComparisonCounting

def DistributionCounting(R, key=lambda x:x):
    origKeys = [key(x) for x in R]
    u = min(origKeys)
    v = max(origKeys)
    N = len(origKeys)
    counts = [0]*(v-u+1)    # D1
    outputs = [None]*len(R)
    for j in range(N):      # D2
        counts[key(R[j]) - u]+= 1   # D3
    # D4
    for i in range(u+1, v+1):
        counts[i - u] = counts[i - u] + counts[i - 1 - u]
    for j in range(len(R)):   # D5
        i = counts[key(R[j]) - u]
        outputs[i-1] = R[j]
        counts[key(R[j]) - u] = i - 1


    return outputs

def solve():
    # unsorted = SortUtils.randomIntegerArray(1000)
    # unsorted = [rand.randint(50,55) for x in range(200000)]
    # unsorted = [5,5,5,5,6,2,3,0]
    # unsorted = SortUtils.KnuthExample()
    keyFunc = lambda x:abs(x)
    unsorted = list(reversed([x-10 for x in SortUtils.randomIntegerArray(20)]))
    sortedArr = DistributionCounting(unsorted, keyFunc)
    for a, b in zip(sortedArr, sorted(unsorted, key=keyFunc)):
        if a != b:
            break
    else:
        print('Matches:', sortedArr)
        return
    print("No match.", sortedArr)

if __name__ == '__main__':
    solve()