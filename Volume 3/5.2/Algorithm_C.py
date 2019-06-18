import sys
import random as rand
sys.path.append(r'C:\Users\gabburke\Documents\Personal\TAOCP\Volume 3\SortUtils')
from SortUtils import SortUtils

def reconstructFromInversionCount(arr, inversions):
    sortedArr = []
    for i in reversed(range(len(arr))):
        sortedArr.insert(inversions[i], arr[i])
    return sortedArr

def ComparisonCountingWeird(arr):
    counts = [0]*len(arr)
    for i in range(len(arr) - 1):
        for j in range(i+1, len(arr)):
            if arr[i] > arr[j]:
                counts[i] += 1
    return reconstructFromInversionCount(arr, counts)

def ComparisonCounting(arr):
    # C1
    counts = [0]*len(arr)
    # C2
    # for i in reversed(range(len(arr) - 1)):
    for i in range(1, len(arr)):
        # C3
        # for j in range(i+1, len(arr)):
        for j in range(i):
            # C4
            if arr[i] > arr[j]:
                counts[i] += 1
            else:
                counts[j] += 1
    outputArr = [None]*len(arr)
    for index in range(len(arr)):
        outputArr[counts[index]] = arr[index]
    return outputArr

def solve():
    # unsorted = SortUtils.randomIntegerArray(10)
    # unsorted = SortUtils.KnuthExample()
    unsorted = [rand.randint(50,55) for x in range(20)]
    sortedArr = ComparisonCounting(unsorted)
    for a, b in zip(sortedArr, sorted(unsorted)):
        if a != b:
            break
    else:
        print('Matches:', sortedArr)
        return
    print("No match.", sortedArr)

if __name__ == '__main__':
    solve()