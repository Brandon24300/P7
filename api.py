from typing import Optional

import pandas as pd


from flask import Flask, render_template, jsonify
from flask import request
import json
import requests

    

df = pd.read_csv('data/application_train.csv')
df_score = pd.read_csv('log_reg_baseline.csv')

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"

@app.route('/dashboard/')
def dashboard():
    return render_template("dashboard.html")

@app.route('/api/clients/')
def clients():
    args = request.args
    fields = args['fields']
    # Si l'utilisateur demande des champs en particulier alors on lui renvoie que cela
    if fields:
        fields = fields.split(",")
    else:
        fields = df.columns.values

    return jsonify({
      'status': 'ok', 
      'data': df[[fields]].to_dict(orient='records')
    })

@app.route('/api/clients/score')
def clients():
    args = request.args
    identifiant = args['id']

    return jsonify({
      'status': 'ok', 
      'data': []
    })

if __name__ == "__main__":
    app.run(debug=True)