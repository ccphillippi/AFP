import nltk
f=open('1.txt')
TXT=f.readlines()
temp=""
art=[]
for i in TXT[:70]:
    if i.strip()=="":
        art.append(temp)
        temp=""
    else:
        temp=temp + " " + i[:len(i)-2]

for i in art:
    print i