import sys
sys.path.append(r'C:\Users\gabburke\Documents\Personal\TAOCP\Volume 3\Sort Utils')
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
    counts = [0]*len(arr)
    for i in range(len(arr) - 1):
        for j in range(i+1, len(arr)):
            if arr[i] > arr[j]:
                counts[i] += 1
            else:
                counts[j] += 1
    outputArr = [None]*len(arr)
    for index in range(len(arr)):
        outputArr[counts[index]] = arr[index]
    return outputArr

def solve():
    unsorted = SortUtils.randomIntegerArray(10)
    sortedArr = ComparisonCounting(unsorted)
    print(unsorted)
    print(sortedArr)

if __name__ == '__main__':
    solve()