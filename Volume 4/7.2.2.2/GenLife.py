import cv2
import numpy as np
from Life import Life, LifeState

class GenLife:
    def __init__(self):
        self.strDict = dict()
        self.img = None
        self.key = ('ABCDEFGHIJ',
               'KLMNOPQRST',
               'UVWXYZ .,!',
               '?:;"\'$',
               '0123456789')
        self.loadFont()

    def stringToLife(self):
        pass

    def loadFont(self):
        img_path = r"C:\Users\Gabri\Documents\gitRepos\TAOCP\Volume 4\7.2.2.2\7x4 font_0.png"
        img = cv2.imread(img_path, 0)  # read image as grayscale. Set second parameter to 1 if rgb is required
        self.img = self.asBoolArr(img)
        for line in self.key:
            for character in line:
                self.strDict[character] = self.getSplice(character)


    def getSplice(self, character):
        # find location of character
        for i, line in enumerate(self.key):
            if character not in line:
                continue
            j = line.index(character)
            topLeft = (i*8, j*5)
            newSplice = []
            for iIdx in range(7):
                newRow = []
                for jIdx in range(4):
                    newRow.append(self.img[topLeft[0] + iIdx][topLeft[1] + jIdx])
                newSplice.append(newRow)
            return newSplice
        else:
            raise Exception('Character has no 7x4 font associated with it.')

    def asBoolArr(self, img):
        boolArr = []
        height, width = img.shape
        for i in range(height):
            boolRow = []
            for j in range(width):
                if img[i][j]:
                    boolRow.append(LifeState.DEAD)
                else:
                    boolRow.append(LifeState.ALIVE)
            boolArr.append(boolRow)
        return boolArr

def doStuff():
    letters = GenLife()
    for character in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ .,!?:;"\'$0123456789':
        life = Life(7, 4)
        for i in range(7):
            for j in range(4):
                life.game[0][i][j].state = letters.strDict[character][i][j]
        print(character, life.game)
if __name__ == '__main__':
    doStuff()