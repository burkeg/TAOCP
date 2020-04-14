import pprint as pp

def All2Digit():
    data = []
    for i in range(100):
        lineData = []
        for j in range(100):
            val = i*100 + j
            lineData.append(GetMiddle(val**2))
        data.append(lineData)
    return data

def GetMiddle(val):
    return (val // 100) % 1000

def Digits2Str(data):
    allStrs = []
    for i in range(100):
        lineStrs = []
        for j in range(100):
            lineStrs.append(str(data[i][j]))
        allStrs.append(', '.join([' '*(4-len(x)) + x for x in lineStrs]))
    print('\n'.join(allStrs))

def GetAllChains(data, tracker):
    chains = []
    sets = [[None for _ in range(100)] for _ in range(100)]
    for i in range(100):
        for j in range(100):
            currPath = []
            curr = (i, j)
            cnt = 0
            while True:
                currPath.append(curr)
                curr = GetNext(data[curr[0]][curr[1]])
                cnt += 1
                if curr == (i, j):
                    chains.append(currPath)
                    sets[i][j] = (currPath, True)
                    break
                if cnt == 1000:
                    sets[i][j] = (currPath, False)
                    break

    chainSets = set()
    for chain in chains:
        chainSets.add(frozenset(chain))
    tracker['b'][0] = len(chainSets)
    tracker['b'][1] = max([len(x) for x in chainSets])
    longestSequence = []
    longest = 0
    for i in range(100):
        for j in range(100):
            cleaned = CleanupSequence(sets[i][j][0], chains, tracker)
            if len(cleaned) > longest:
                longest = len(cleaned)
                longestSequence = cleaned
    tracker['c'] = longestSequence
    print([x for x in list(chainSets)])

def CleanupSequence(sequence, allChains, tracker):
    for i, val in enumerate(sequence):
        chain = GetChain(val, allChains, tracker)
        if chain is not None:
            return sequence[:i] + chain

def GetChain(val, allChains, tracker):
    for chain in allChains:
        if chain[0] == val:
            if chain[0] == (0, 0):
                tracker['a'] += 1
            return chain
    else:
        return None


def GetNext(val):
    return (val // 100, val % 100)

tracker = {'a':0, 'b':[0, 0], 'c':[]}
GetAllChains(All2Digit(), tracker=tracker)
pp.pprint(tracker)