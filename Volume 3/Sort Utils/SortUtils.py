import random as rand
import copy

class SortUtils:
    @staticmethod
    def KnuthExample():
        return [503, 87, 512, 61, 908, 170, 897, 275, 653, 426, 154, 509, 612, 677, 765, 703]

    @staticmethod
    def randomIntegerArray(highest, lowest = 0):
        return SortUtils.shuffled(list(range(lowest, highest)))

    @staticmethod
    # Knuth Shuffle A.K.A. Fisher-Yates Shuffle
    def shuffle(arr):
        for i in range(len(arr) - 1):
            j = rand.randint(i, len(arr) - 1)
            tmp = arr[i]
            arr[i] = arr[j]
            arr[j] = tmp

    @staticmethod
    # Knuth Shuffle A.K.A. Fisher-Yates Shuffle
    def shuffled(arr):
        arrCpy = copy.deepcopy(arr)
        for i in range(len(arrCpy) - 1):
            j = rand.randint(i, len(arrCpy) - 1)
            tmp = arrCpy[i]
            arrCpy[i] = arrCpy[j]
            arrCpy[j] = tmp
        return arrCpy