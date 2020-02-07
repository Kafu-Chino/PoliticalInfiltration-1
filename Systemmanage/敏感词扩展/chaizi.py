chaizidict = {}
with open('chaizi-jt.txt','r',encoding='utf-8')as f:
    lines = f.readlines()
    # print(len(lines))
    for line in lines:
        # print(repr(line))
        new = line.strip().split('\t')
        # print(new)
        if len(new)==2:
            chaizidict[new[0]] = new[1]
        else:
            chaizidict[new[0]] = new[2]

def chaizi(text):
    new_str = ''
    for i in text:
        if i in chaizidict.keys():
            if len(chaizidict[i])>2:
                new_str = new_str+chaizidict[i]
            else:
                new_str = new_str + i
            # print(new_str)
        else:
            new_str = new_str + i
    s = new_str.replace(' ','')
    return s





