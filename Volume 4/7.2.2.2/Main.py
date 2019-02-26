from McGregor import McGregor
from SATUtils import SATUtils

def Exercise17():
    print(McGregor.testLimits([3, 10], viewProgress=True))

def Exercise18():
    for i in range(3,20):
        print(i, int(McGregor.viewMinAssignments(i) / 6))

def Exercise19():
    tst = McGregor(4,4,variant='maxTwo')
    pass

if __name__ == "__main__":
    Exercise19()