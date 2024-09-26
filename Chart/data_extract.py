import os
print(os.getcwd())
f = open("icdata.txt", "r")
data = f.readlines()
X=[]
Y=[]
ind = 200
for ele in data:
    if(ind==0):
        break
    ele = ele[:-1]
    a = ele.split(" ")
    try:
        x = a[12]
        X.append(int(x))
    except:
        continue
    ind-=1;
print(X)
