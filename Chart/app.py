import os
from flask import Flask, jsonify
from flask_cors import CORS
import DBSCAN_classifier as model_report
app = Flask(__name__)
#enabled cross origin request for local develpment
CORS(app)
def getModelInfo():
    data = model_report.returnable('.lc')
    X = data['x']
    Y = data['y']
    MF = data['time_of_occurances']
    TOC = data['time_corresponding_peak_flux']
    return X,Y,MF,TOC
    
    
@app.route('/data', methods=['GET'])
def get_data():
    X,Y,MF,TOC = getModelInfo()
    return jsonify(X,Y,MF,TOC)

if __name__=='__main__':
    app.run(debug=True)