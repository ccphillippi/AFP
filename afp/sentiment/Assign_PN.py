#Load positive tweets into a list
f=open("news_sentence","r")
Key_Sent=f.readlines()
f.close()

p = open('postweets.txt', 'r')
postxt = p.readlines()
p.close()
#Load negative tweets into a list
n = open('negtweets.txt', 'r')
negtxt = n.readlines()
n.close()

n_len=len(postxt)+len(negtxt)
print "You have "+ str(n_len) +" in database."
print "You still have "+ str(len(Key_Sent)) +" to go."

for i in Key_Sent:
    input = raw_input(i+"==>")
    if input=="p":
        postxt.append(i);
    elif input =="n":
        negtxt.append(i);
    elif input !="0":
        break
    Key_Sent.remove(i)

f=open("news_sentence","w")
f.writelines(Key_Sent)
f.close()

f=open('postweets.txt', 'w')
f.writelines(postxt)
f.close()

f=open('negtweets.txt', 'w')
f.writelines(negtxt)
f.close()

print "done"