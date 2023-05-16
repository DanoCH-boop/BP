import numpy as np

def find_cuts(path):
    """Approximates the exact points where the input signals differ"""
    # HLADANIE STRIHOV
    path = np.array(path)
    sig_len = path[:, 0][-1]/4
   
    # minimalny cas medzi strihmi
    min_t_btw_cuts = 10  # 2.5s
    if sig_len > 20*60:
        min_t_btw_cuts = 20  # 5s
    if sig_len > 30*60:
        min_t_btw_cuts = 25  # 6.25s
    if sig_len > 45*60:
        min_t_btw_cuts = 30  # 7.5s
    if sig_len > 60*60:
        min_t_btw_cuts = 40 # 10s

    diffs = np.diff(path[:, 1])

    # DEV
    # print(diffs)
    # with open("file1.txt", "w") as f:
    #     for p in diffs:
    #         f.write(str(p)+ " ")
    # diffs = np.insert(diffs, 0, diffs[0])
    # diffs = np.insert(diffs, -1, diffs[-1])
    # diffs = sig.medfilt(diffs,5)
    # DEV

    # tymto najdem cas/frame kedy sa signaly prestavaju rovnat
    # +1 alebo nie +1?? to zalezi, ci pocitame sekundy on nultej alebo prvej
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
    real_change = np.where(np.diff(change_indices)-1 > min_t_btw_cuts)[0] + 1
    print(real_change) 

    # tymto splitnem/odlisim rozne strihy od seba
    result = np.split(change_indices, real_change)
    # ked je prvý strih blízko začiatku, spresni jeho určenie
    indexes = result[0]
    if indexes[0] < 20:
        indexes[-1] = indexes[0] + indexes.size
            
    indexes_of_change = [(indexes[-1], indexes.size) for indexes in result]
    # DEV
    # printable = [(indexes[0],indexes[-1], indexes.size) for indexes in result]
    # DEV

    indexes_of_change = np.array(indexes_of_change)

    # DEV
    # tym sa vyhladia nahodne nuly co vzniknu dtw algoritmom o dlzke 1
    # cuts =  indexes_of_change[np.where(indexes_of_change[:, 1] > 1)]
    # DEV

    return indexes_of_change

if __name__ == "__main__":
    cuts = find_cuts([(0, 0), (1, 1), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 3), 
                      (9, 4), (10, 5), (11, 5), (12, 5), (13, 5), (14, 6), (15, 7), (16, 8)])
    print(cuts)
             