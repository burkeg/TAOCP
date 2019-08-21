import pprint as pp
from SortUtils import SortUtils
import math
def stackPermute(target):
    n = math.ceil(math.log(len(target), 2))
    stacks = [[] for x in range(n)]
    incoming = list(range(2**n))
    output = []
    pp.pprint(target)

    def enterStacks():
        stacks[0].append(incoming.pop(0))

    def popStack(stackNum):
        if n == stackNum + 1:
            exitStacks()
        elif n > stackNum and stackNum >= 0:
            stacks[stackNum+1].append(stacks[stackNum].pop())
        else:
            raise Exception('Invalid stack index.')

    def exitStacks():
        output.append(stacks[-1].pop())
        print('Output: ' + str(output))

    def filterTarget(majN, minN):
        lowerIndex = 2**majN if majN > 0 else 0
        upperIndex = 2**minN + lowerIndex
        print(str(lowerIndex) + ':' + str(upperIndex-1))
        return [x for x in target if x in range(lowerIndex, upperIndex)]

    def stackOffset(frameMin, frameMax, value):
        frameSize = frameMax - frameMin
        threshold = frameSize//2
        offset = 0
        while frameSize - threshold >= 2 and value > threshold:
            offset += 1
            threshold = (threshold + frameSize ) // 2
        return offset

    def moveFromStackToStack(stackB, stackA):
        if stackB == -1:
            enterStacks()
            stackB = 0
        for i in range(stackB, stackA):
            popStack(i)

    def doPermute(majN, minN, downRight=False):
        print(downRight)
        # Two parts, first recursively form stacks from smaller minN
        # Second, stitch together to form majN

        # Base case, minN = 1
        filtered = filterTarget(majN,minN)
        print('')
        if minN == 1:
            # We want the lower value to go first when:
            #   * it is preceded by the higher value and we're downRight
            #   * it precedes the higher value and we're downLeft
            if downRight and (filtered[-1] == incoming[0]) or (not downRight) and (filtered[0] == incoming[0]):
                enterStacks()
                popStack(0)
                enterStacks()
                popStack(0)
            else:
                enterStacks()
                enterStacks()
                popStack(0)
                popStack(0)
            return

        doPermute(majN,minN-1, downRight=not downRight)

        # stitch together from previous stacks
        frameMin = min(filtered)
        frameMax = max(filtered)
        hasTakenFromIncoming = False
        for val in reversed(filtered) if downRight else filtered:
            offset = stackOffset(frameMin, frameMax, val)
            if minN - offset - 1 <= 0:
                if val == frameMax - 1:
                    if hasTakenFromIncoming:
                        moveFromStackToStack(0, minN)
                    else:
                        moveFromStackToStack(-1, minN)
                    hasTakenFromIncoming = True
                elif val == frameMax:
                    if hasTakenFromIncoming:
                        moveFromStackToStack(-1, minN)
                    else:
                        enterStacks()
                        moveFromStackToStack(-1, minN)
                    hasTakenFromIncoming = True
            else:
                moveFromStackToStack(minN - offset - 1, minN)

        doPermute(minN,minN-1, downRight=downRight)

        pass

    doPermute(majN=0, minN=4, downRight=False)


    pp.pprint(stacks)


if __name__ == '__main__':
    # stackPermute(SortUtils.shuffled(list(range(2**3))))
    stackPermute([12, 14, 3, 8, 1, 6, 15, 5, 0, 10, 9, 4, 13, 7, 11, 2])
    # stackPermute([12, 14, 2, 8, 1, 6, 15, 5, 0, 10, 9, 4, 13, 7, 11, 3])
    # stackPermute([0, 3, 1 ,2])