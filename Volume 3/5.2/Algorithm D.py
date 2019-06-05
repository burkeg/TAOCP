import sys
sys.path.append(r'C:\Users\gabburke\Documents\Personal\TAOCP\Volume 3\Sort Utils')
from SortUtils import SortUtils

def DistributionCounting(arr):
    u = min(arr)
    v = max(arr)
    counts = [0]*(v-u+1)
    outputs = [0]*len(arr)
    for j in range(len(arr)):
        counts[arr[j]-u]+= 1
    for i in range(1, v-u+1):
        counts[i] = counts[i] + counts[i-1]
    for j in reversed(range(len(arr))):
        i = counts[arr[j]-u]-1
        outputs[i] = arr[j]
        counts[arr[j]] = i - 1


    return outputs

def solve():
    unsorted = SortUtils.randomIntegerArray(10)
    unsorted = [5,5,5,5,6,2,3]
    sortedArr = DistributionCounting(unsorted)
    print(unsorted)
    print(sortedArr)

if __name__ == '__main__':
    solve()