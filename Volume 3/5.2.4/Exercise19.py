import pprint as pp
from SortUtils import SortUtils
import math
def stackPermute(target, debug=True):
    n = math.ceil(math.log(len(target), 2))
    stacks = [[] for x in range(n)]
    incoming = list(range(2**n))
    output = []
    actionSequence = []
    # pp.pprint(target)

    def enterStacks():
        if debug:
            print('Push ' + str(incoming[0]) + ' to stack [0]')
        stacks[0].append(incoming.pop(0))
        actionSequence.append(0)

    def popStack(stackNum):
        if n == stackNum + 1:
            exitStacks()
        elif n > stackNum and stackNum >= 0:
            actionSequence.append(stackNum+1)
            if debug:
                print('Pop ' + str(stacks[stackNum][-1]) + ' from stack[' + str(stackNum) + ']')
            stacks[stackNum+1].append(stacks[stackNum].pop())
        else:
            raise Exception('Invalid stack index.')

    def exitStacks():
        actionSequence.append(n)
        output.append(stacks[-1].pop())
        if debug:
            print('Output from stack [' + str(n-1) + ']: ' + str(output))

    def filterTarget(lowerIndex, regionWidth):
        upperIndex = 2 ** regionWidth + lowerIndex
        # print(str(lowerIndex) + ':' + str(upperIndex-1))
        return [x for x in target if x in range(lowerIndex, upperIndex)]

    def stackOffset(frameMin, frameMax, value):
        frameSize = frameMax - frameMin + 1
        threshold = frameSize//2
        offset = 0
        while frameSize - threshold > 1 and (value - frameMin) >= threshold:
            offset += 1
            threshold = (threshold + frameSize) // 2
        # print('frameSize', frameSize, 'frameMin', frameMin, 'frameMax', frameMax, 'value', value, 'offset', offset)
        return offset

    def moveFromStackToStack(stackB, stackA):
        if stackB == -1:
            enterStacks()
            stackB = 0
        for i in range(stackB, stackA):
            popStack(i)

    def doPermute(lowerIndex, regionWidth, downRight=False):
        if len(incoming) == 0:
            return
        # Two parts, first recursively form stacks from smaller minN
        # Second, stitch together to form majN

        # Base case, minN = 1
        filtered = filterTarget(lowerIndex, regionWidth)
        if regionWidth == 1:
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

        doPermute(lowerIndex, regionWidth - 1, downRight=not downRight)

        # stitch together from previous stacks
        frameMin = min(filtered)
        frameMax = max(filtered)
        hasTakenFromIncoming = False
        for val in reversed(filtered) if downRight else filtered:
            offset = stackOffset(frameMin, frameMax, val)
            if regionWidth - offset - 1 <= 0:
                if val == frameMax - 1:
                    if hasTakenFromIncoming:
                        moveFromStackToStack(0, regionWidth)
                    else:
                        moveFromStackToStack(-1, regionWidth)
                    hasTakenFromIncoming = True
                    continue
                elif val == frameMax:
                    if hasTakenFromIncoming:
                        moveFromStackToStack(-1, regionWidth)
                    else:
                        enterStacks()
                        moveFromStackToStack(-1, regionWidth)
                    hasTakenFromIncoming = True
                    continue
                else:
                    raise Exception('This should never happen')
            moveFromStackToStack(regionWidth - offset - 1, regionWidth)

        doPermute(lowerIndex + 2**regionWidth, regionWidth - 1, downRight=downRight)

    doPermute(lowerIndex=0, regionWidth=n, downRight=False)

    return output, actionSequence


if __name__ == '__main__':
    lst = SortUtils.shuffled(list(range(2**10)))
    result, actions = stackPermute(lst, debug=True)
    # result = stackPermute([12, 14, 3, 8, 1, 6, 15, 5, 0, 10, 9, 4, 13, 7, 11, 2])
    # stackPermute([12, 14, 2, 8, 1, 6, 15, 5, 0, 10, 9, 4, 13, 7, 11, 3])
    # stackPermute([0, 3, 1 ,2])
    print('Expected: ', lst)

    print('Actual:   ', result)

    print(actions)