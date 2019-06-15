import sys
import random as rand
import copy
sys.path.append(r'C:\Users\gabburke\Documents\Personal\TAOCP\Volume 3\Sort Utils')
from SortUtils import SortUtils
from Algorithm_C import ComparisonCounting

def DistributionCounting(R):
    K = copy.deepcopy(R) # Keys are equivalent to records in this case.
    u = min(K)
    v = max(K)
    N = len(K)
    counts = [0]*(v-u+1)    # D1
    outputs = [None]*len(K)
    indexer = lambda x: x-u
    for j in range(N):      # D2
        counts[indexer(K[j])]+= 1   # D3
    # D4
    for i in range(u+1, v+1):
        counts[indexer(i)] = counts[indexer(i)] + counts[indexer(i-1)]
    for j in reversed(range(len(K))):   # D5
        i = counts[indexer(K[j])]
        outputs[indexer(i)-1] = R[j]
        counts[indexer(K[j])] = i - 1


    return outputs

def solve():
    unsorted = SortUtils.randomIntegerArray(10)
    unsorted = [rand.randint(50,60) for x in range(500)]
    # unsorted = [5,5,5,5,6,2,3,0]
    sortedArr2 = ComparisonCounting(unsorted)
    sortedArr = DistributionCounting(unsorted)
    print(unsorted)
    print(sortedArr)
    print(sortedArr2)

if __name__ == '__main__':
    solve()