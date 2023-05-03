import numpy as np

def find_cuts(path):
    """Approximates the exact points where the input signals differ"""
    # HLADANIE STRIHOV

    path = np.array(path)
    diffs = np.diff(path[:, 1])
    print(diffs)
    # diffs[0] = 0
    # diffs = np.append(diffs, (diffs[-1], diffs[-1]))
    # diffs = sig.medfilt(diffs,5)

    # tymto najdem cas/frame kedy sa signaly prestavaju rovnat
    # +1 or not +1?? to zalezi, ci pocitame sekundy on nultej alebo prvej
    # pocitajme od prvej (i guess)
    change_indices = np.where(diffs == 0)[0] + 1
    print(change_indices)

    # 3. eliminácia artefaktov vo vnútri strihu
    # t. j. obmedzenie minimálneho času medzi strihmi
    # na 10 rámcov (2.5s, strihy bližšie k sebe sa spoja)
    # tymto kodom som chcel eliminovat useky vo vnutri "strihu", kde sa pri dtw aj tak namapovali 3 a viac prvky po sebe "presne"
    # tj v "path" ako "[(150,100), (151,100), (152,100),--> (153,101), (154,102), (155,103) <--, (156,103), (157,103), (158,103)]"
    # diffs2 = np.diff(change_indices) 
    # real_change = np.where(diffs2-1 > 10)[0] + 1
    real_change = np.where(np.diff(change_indices)-1 > 10)[0] + 1
    print(real_change) 

    # tymto splitnem/odlisim rozne strihy od seba
    result = np.split(change_indices, real_change)
    indexes_of_change = [(indexes[-1], indexes.size) for indexes in result]
    indexes_of_change = np.array(indexes_of_change)
    # minimalna dlzka strihu musi byt amp*10 = 2.5s,
    # tym sa vyhladia nahodne nuly (tj. strihy) co vzniknu dtw algoritmom o dlzke 10, teda 2.5s
    # cuts = indexes_of_change[np.where(indexes_of_change[:, 1] > 10)]

    return indexes_of_change

if __name__ == "__main__":
    cuts = find_cuts([(0, 0), (1, 1), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 3), 
                      (9, 4), (10, 5), (11, 5), (12, 5), (13, 5), (14, 6), (15, 7), (16, 8)])
    print(cuts)
             