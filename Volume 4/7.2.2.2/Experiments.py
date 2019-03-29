from McGregor import McGregor
from SATUtils import SATUtils
from GraphColoring import GraphColoring
import pycosat
import math
import numpy as np
import pprint as pp

class Experiments:
    def __init__(self):
        pass

    @staticmethod
    def assertNoLoops(width, length):
        symbolDict = dict()
        for i in range(width*2-1):
            for j in range(length*2-1):
                # junctions
                if not ((i == 1 or i ==3) and (j == 1 or j ==3)) and (i+j)%2 == 0:
                    if '+' not in symbolDict:
                        symbolDict['+'] = [(i, j)]
                    else:
                        symbolDict['+'].append((i, j))

                # Lengthwise edges
                if (i+j) % 2 != 0 and j % 2 == 0:
                    if '|' not in symbolDict:
                        symbolDict['|'] = [(i, j)]
                    else:
                        symbolDict['|'].append((i, j))

                # crosswise edges
                if (i+j) % 2 != 0 and j % 2 != 0:
                    if '-' not in symbolDict:
                        symbolDict['-'] = [(i, j)]
                    else:
                        symbolDict['-'].append((i, j))

                # centers
                if (i == 1 or i ==3) and (j == 1 or j ==3):
                    if 'b' not in symbolDict:
                        symbolDict['b'] = [(i, j)]
                    else:
                        symbolDict['b'].append((i, j))


        nodeDict = dict()

        # At each junction in the puzzle, make sure all surrounding edges form a k-clique
        for junction in symbolDict['+']:
            nodesInClique = [x for x in symbolDict['-'] + symbolDict['|'] \
                             if (abs(x[0]-junction[0]) == 1 and abs(x[1]-junction[1]) == 0) \
                             or (abs(x[0]-junction[0]) == 0 and abs(x[1]-junction[1]) == 1)]
            for i, a in enumerate(nodesInClique):
                for b in nodesInClique[i+1:]:
                    if a != b:
                        if a not in nodeDict:
                            nodeDict[a] = [b]
                        else:
                            nodeDict[a].append(b)
                        if b not in nodeDict:
                            nodeDict[b] = [a]
                        else:
                            nodeDict[b].append(a)
        pp.pprint(symbolDict)
        pp.pprint(nodeDict)

        # define new external node that touches all centers on the outer ring
        symbolDict['b'].append((-1, -1))
        for edge in symbolDict['|'] + symbolDict['-']:
            if edge[0] == 1:
                pass



if __name__ == "__main__":
    Experiments.assertNoLoops(3, 3)