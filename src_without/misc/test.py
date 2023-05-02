def align_test():
    rem = []
    help = []
    h = []

    for i in range(2, 10):
        rem.append(i)
        h.append(i)
        
    help.append(h)
    h = []
    
    for i in range(20, 50):
        rem.append(i)
        h.append(i)
    help.append(h)
    h = []

    for i in range(100, 120):
        rem.append(i)
        h.append(i)
    help.append(h)
    h = []

    for i in range(500, 505):
        rem.append(i)
        h.append(i)
    help.append(h)
    h = []
    
    for i in range(600, 700):
        rem.append(i)
        h.append(i)
    help.append(h)
    
    pairs = [(10.0, 15.0), (25.0, 30.0)]
    while pairs[-1][1] < 2900 and len(pairs) < 50:
        last_pair = pairs[-1]
        next_pair = (last_pair[1] + 50.0, last_pair[1] + 150.0)
        pairs.append(next_pair)
    pairs = [pair[0] for pair in pairs]
    return rem, pairs, help

if __name__ == "__main__":
    import numpy as np
    rem, pairs, help = align_test()
    r = np.array([1,2,3])
    index = np.where([100 + 1 in subarr for subarr in help])[0]

    print(rem, pairs, help)
    print(index, help[index[0]])
    print(type(r), r)