import nltk
from os import listdir
import string
import csv
import datetime

KeyWord=["google"]
path="/Users/Lee/Dropbox/AFPdb/SparseSent"
Mon=["January","February","March","April","May","June","July","August","September","October","November","December"]
dic_str_to_num=dict(zip(Mon,range(1,13)))
dic_num_to_str=dict(zip(range(1,13),Mon))

d1=datetime.date(2011,1,1)
d2=datetime.date(2013,12,31)
d=[]
for a in range((d2-d1).days+1):
    temp_date=d1+datetime.timedelta(a)
    d.append([str(temp_date.year)+"/"+str(temp_date.month)+"/"+str(temp_date.day),0])
dic=dict(d)

company=listdir(path)
fw=open("/Users/Lee/Dropbox/AFPdb/Occurance.csv","w")
for c in company:
    print c
    dic_temp=dict(dic)
    fr=open(path+"/"+c,"r")
    TXT=fr.readlines()
    fr.close()
    for i in range(len(TXT)):
        TXT[i]=TXT[i].split('@')
    for t in TXT:
        dic_temp[t[0]]+=1
    for t in dic_temp.items():
        fw.writelines(str(t[1])+",")
    fw.writelines("\n")
fw.close()