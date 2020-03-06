# from chaizi import chaizi读取
from .chaizi import chaizi
from .zhuanhuan import *

def extent(sensitive_word):
    n = 1
    total_fanti_list = []
    total_jianti_list = []
    if len(sensitive_word)<=4:
        total_fanti_list.append(hk2s(sensitive_word))
        total_jianti_list.append(s2hk(sensitive_word))
    if n == 1:
        total_chaizi_list = []
        total_pinyin_list = []
        total_shouzimu_list = []
        for word in total_jianti_list:
            word = word.strip()
            chaizi_list = []
            pinyin_list = []
            shouzimu_list = []
            for i in word:
                chaizi_result = chaizi(i)
                chaizi_list.append(chaizi_result)
                pinyin_list.append(get_pinyin(i))
                shouzimu_list.append(get_acronym(i))
            total_chaizi_list.append(chaizi_list)
            total_pinyin_list.append(pinyin_list)
            total_shouzimu_list.append(shouzimu_list)

        for word in total_jianti_list:
            zi_list = list(word)
            id_list = []
            for a in range(4):
                for b in range(4):
                    for c in range(4):
                        for d in range(4):
                            id_list.append([a,b,c,d])#e,f
            new_word_list = []
            for id in id_list:
                newword = ''
                for i in range(len(zi_list)):
                        try:
                            if id[i] == 0:
                                newword=newword+zi_list[i]
                            if id[i] == 1:
                                newword = newword + total_shouzimu_list[total_jianti_list.index(word)][i]
                            if id[i] == 2:
                                newword = newword + total_chaizi_list[total_jianti_list.index(word)][i]
                            if id[i] == 3:
                                newword=newword+total_pinyin_list[total_jianti_list.index(word)][i]
                        except:
                            continue
                if newword!='':
                    new_word_list.append(newword)
            set1 = set(new_word_list)
    if n == 1:
        total_chaizi_list = []
        total_pinyin_list = []
        total_shouzimu_list = []
        for word in total_fanti_list:
            word = word.strip()
            chaizi_list = []
            pinyin_list = []
            shouzimu_list = []
            for i in word:
                chaizi_result = chaizi(i)
                chaizi_list.append(chaizi_result)
                pinyin_list.append(get_pinyin(i))
                shouzimu_list.append(get_acronym(i))
            total_chaizi_list.append(chaizi_list)
            total_pinyin_list.append(pinyin_list)
            total_shouzimu_list.append(shouzimu_list)

        for word in total_fanti_list:
            zi_list = list(word)
            id_list = []
            for a in range(4):
                for b in range(4):
                    for c in range(4):
                        for d in range(4):
                            for e in range(4):
                                for f in range(4):
                                    id_list.append([a, b, c, d, e, f])
            new_word_list = []
            for id in id_list:
                newword = ''
                for i in range(len(zi_list)):
                    # print(word)
                    if id[i] == 0:
                        newword = newword + zi_list[i]
                    if id[i] == 1:
                        newword = newword + total_shouzimu_list[total_fanti_list.index(word)][i]
                    if id[i] == 2:
                        newword = newword + total_chaizi_list[total_fanti_list.index(word)][i]
                    if id[i] == 3:
                        newword = newword + total_pinyin_list[total_fanti_list.index(word)][i]

                new_word_list.append(newword)
            set2 = set(new_word_list)
            total_set = set1 | set2
            total_set.remove(sensitive_word)
    return total_set
