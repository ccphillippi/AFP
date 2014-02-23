import nltk
from os import listdir

keyword="google"
path="/Users/Lee/Dropbox/AFPdb/Corpus/LexisNexis/"
year=listdir(path)
year.remove('.DS_Store')

year=["2012"]

for y in year:
    month=listdir(path+y)
    month.remove('.DS_Store')
    for m in month:
        day=listdir(path+y+"/"+m)
        day.remove('.DS_Store')
        for d in day:
            Sent=[]
            Newspaper=listdir(path+y+"/"+m+"/"+d)
            #Newspaper.remove('.DS_Store')
            for np in Newspaper:
                News=listdir(path+y+"/"+m+"/"+d+"/"+np)
                for file in News:
                    f=open(path+y+"/"+m+"/"+d+"/"+np+"/"+file)
                    TXT[0]=f.readlines()
                    TXT=TXT.replace("\r", "");
                    TXT=TXT.replace("|", ".");
                    TXT=TXT.replace("\n", "");                    
                    Sent=Sent+nltk.sent_tokenize(TXT)
'''                    
for i in Sent:
    Sent_Split=i.lower().split()
    if len(Sent_Split)>0:
        if Sent_Split[0] in Mon:
            date=str(dic[Sent_Split[0]])+"/"+Sent_Split[1][0:len(Sent_Split[1])-1]+"/"+Sent_Split[2]
    if keyword.lower() in Sent_Split:
        Key_Sent.append((date,i.lower()))

        
f=open('SP5.txt')
TXT=f.readlines()

temp=""
art=[]
for i in TXT:
    if i.strip()=="":
        art.append(temp+ "\n")
        temp=""
    else:
        temp=temp + " " + i[:len(i)-2]
print "done with combining paragraph"
TXT=art

date=""
Sent=[]
Mon=["january","february","march","april","may","june","july","august","september","october","november","december"]
dic=dict(zip(Mon,range(1,13)))
for i in xrange(0,len(TXT)):
    TXT[i]=TXT[i].replace("\r", "");
    TXT[i]=TXT[i].replace("|", ".");
    TXT[i]=TXT[i].replace("\n", "");
    TXT[i]=TXT[i].replace("S&P 500", "S&P500");
    TXT[i]=TXT[i].replace("S.&P. 500", "S&P500");
    TXT[i]=TXT[i].replace("S.& P. 500", "S&P500");
    TXT[i]=TXT[i].replace("Standard & Poor's 500", "S&P500");
    TXT[i]=TXT[i].replace("Standard & Poor 500", "S&P500"); 
    Sent=Sent+nltk.sent_tokenize(TXT[i])
    
Key_Sent=[]
keyword="s&p500"
for i in Sent:
    Sent_Split=i.lower().split()
    if len(Sent_Split)>0:
        if Sent_Split[0] in Mon:
            date=str(dic[Sent_Split[0]])+"/"+Sent_Split[1][0:len(Sent_Split[1])-1]+"/"+Sent_Split[2]
    if keyword.lower() in Sent_Split:
        Key_Sent.append((date,i.lower()))
#f=open("news_sentence5","w")
#f.writelines(Key_Sent)
#f.close()
for i in Key_Sent:
    print i[0]+" @ "+ i[1]
#print len(Key_Sent)
#txt=nltk.data.load('NEWS.txt','text')
#print txt

#S=nltk.tokenize(txt)
'''