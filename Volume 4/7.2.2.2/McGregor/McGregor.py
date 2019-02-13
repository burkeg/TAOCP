from dpll import solve
import math
import pprint as pp

class McGregor:
    def  __init__(self, n):
        if (n < 3):
            raise ValueError()
        self.n = n
        self.nodeDict = dict()
        for i in range(n+1):
            for j in range(n):
                self.nodeDict[(i,j)] = set()
        self.populateConnections()
        pp.pprint(self.nodeDict)


    def populateConnections(self):
        for node in self.nodeDict.keys():
            # Handle row 0
            if node[0] is 0:
                if node[1] is 0:
                    self.nodeDict[node].add((0,1))    #node to right
                    self.nodeDict[node].add((1,1))    #node to bottom right
                    self.nodeDict[node].add((self.n,self.n-1))    #node above
                    for index in range(math.floor(self.n/2)+1):
                        self.nodeDict[node].add((self.n,index))    #nodes across bottom row
                elif node[1] is self.n-1:
                    self.nodeDict[node].add((node[0],node[1]-1))    #node to left
                    self.nodeDict[node].add((node[0]+1,node[1]))    #node to bottom left
                    self.nodeDict[node].add((self.n,self.n-1))    #node surrounding
                else:
                    self.nodeDict[node].add((self.n,self.n-1))    #node above
                    self.nodeDict[node].add((node[0],node[1]-1))    #node to left
                    self.nodeDict[node].add((node[0],node[1]+1))    #node to right
                    self.nodeDict[node].add((node[0]+1,node[1]))    #node to bottom left
                    self.nodeDict[node].add((node[0]+1,node[1]+1))    #node to bottom right
            # Handle row 1
            elif node[0] is 1:
                if node[1] is 0:
                    self.nodeDict[node].add((0,0))    #node to left
                    for index in range(math.floor(self.n/2), self.n):
                        self.nodeDict[node].add((self.n,index))    #nodes across bottom row
                elif node[1] is 1:
                    self.nodeDict[node].add((0,0))    #node to left
                    self.nodeDict[node].add((node[0]-1,node[1]))    #node above
                    self.nodeDict[node].add((self.n,0))    #node to lower bottom left
                    self.nodeDict[node].add((self.n-1,0))    #node to lower bottom right
                    self.nodeDict[node].add((node[0]+1,node[1]+1))    #node to upper bottom right
                    self.nodeDict[node].add((node[0],node[1]+1))    #node to right
                elif node[1] is self.n-1:
                    self.nodeDict[node].add((node[0]+1,node[1]))    #node to bottom left
                    self.nodeDict[node].add((node[0],node[1]-1))    #node to left
                    self.nodeDict[node].add((node[0]-1,node[1]-1))    #node to upper left
                    self.nodeDict[node].add((node[0]-1,node[1]))    #node to upper right
                    self.nodeDict[node].add((self.n-node[0]+1,node[1]-(node[0]-1)))    #node to lower bottom right
                    self.nodeDict[node].add((self.n-node[0], node[1]-(node[0]-1)-1))    #node to lower bottom left
                else:
                    self.nodeDict[node].add((node[0]-1,node[1]-1))    #node to upper left
                    self.nodeDict[node].add((node[0]-1,node[1]))    #node to upper right
                    self.nodeDict[node].add((node[0],node[1]-1))    #node to left
                    self.nodeDict[node].add((node[0],node[1]+1))    #node to right
                    self.nodeDict[node].add((node[0]+1,node[1]))    #node to bottom left
                    self.nodeDict[node].add((node[0]+1,node[1]+1))    #node to bottom right
            # Handle row 2
            elif node[0] is 2:
                pass



if __name__ == "__main__":
    #solve('small_instances.txt')
    mg = McGregor(4)
