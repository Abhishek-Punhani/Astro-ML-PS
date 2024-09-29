import os
from flask import Flask, jsonify
from flask_cors import CORS
app = Flask(__name__)
#enabled cross origin request for local develpment
CORS(app)
def getDbData():
    #currently the function returns sample data instead of postgres
    #later on we will fetch the data using sqlalchemy once added to database
    print(os.getcwd())
    f = open("icdata.txt", "r")
    data = f.readlines()
    X=[]
    Y=[]
    ind = 3000
    for ele in data:
        if(ind==0):
            break
        ele = ele[:-1]
        a = ele.split(" ")
        try:
            y = a[12]
            x = a[3]
            X.append(int(x))
            Y.append(int(y))
        except:
            continue
        ind-=1
    return X,Y

@app.route('/data', methods=['GET'])
def get_data():
    X,Y = getDbData()
    return jsonify(X,Y)

if __name__=='__main__':
    app.run(debug=True)