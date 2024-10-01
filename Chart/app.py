from flask import Flask, jsonify
from flask_cors import CORS
import DBSCAN_classifier as model_report
app = Flask(__name__)
#enabled cross origin request for local develpment
CORS(app)
def getModelInfo():
    #instead of running the model, data variable should take the response object from sql database
    data = model_report.returnable('.lc')
    X = data['x']
    Y = data['y']
    MF = data['time_of_occurances']
    TOC = data['time_corresponding_peak_flux']
    left = data['left']
    leftx = []
    lefty = []
    for ele in left:
        leftx.append(X[ele])
        lefty.append(Y[ele])
    #remove slicing later   
    return X[:6000],Y[:6000],MF[:100],TOC[0:100],leftx,lefty
    
    
@app.route('/data', methods=['GET'])
def get_data():
    X,Y,MF,TOC,leftx,lefty = getModelInfo()
    return jsonify(X,Y,MF,TOC,leftx,lefty)

if __name__=='__main__':
    app.run(debug=True)