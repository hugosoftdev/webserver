import json
import sys
from helpers import getStrategiesNames,getModelsNames, getModelVersions, insert_simulation, insert_results,get_results, get_simulation, get_simulations
import os
from flask import Flask, make_response, request
import simulator
app = Flask(__name__)


@app.route('/simulate', methods=['POST'])
def create_simulation():
    configs = request.json
    print(configs)
    try:
        simulator.deploy_simulator(configs)
        content = json.dumps({"response": "ok"})
        status = 200
    except:
        e = sys.exc_info()[0]
        content = json.dumps({"error": e})
        status = 404
    return make_response(content, status, {'Content-Type': 'application/json'})

@app.route("/strategies", methods=['GET'])
def list_strategies():
    try:
        content = json.dumps({"strategies": getStrategiesNames()})
        status = 200
    except:
        e = sys.exc_info()[0]
        content = json.dumps({"error": e})
        status = 404
    return make_response(content, status, {'Content-Type': 'application/json'})

@app.route("/models", methods=['GET'])
def list_models():
    try:
        content = json.dumps({"models": getModelsNames()})
        status = 200
    except:
        e = sys.exc_info()[0]
        content = json.dumps({"error": e})
        status = 404
    return make_response(content, status, {'Content-Type': 'application/json'})

@app.route("/model_versions", methods=['GET'])
def list_model_versions():
    modelName= request.args.get('modelName')
    try:
        content = json.dumps({"versions": getModelVersions(modelName)})
        status = 200
    except:
        e = sys.exc_info()[0]
        content = json.dumps({"error": e})
        status = 404
    return make_response(content, status, {'Content-Type': 'application/json'})

@app.route("/simulation", methods=['POST'])
def add_simulation():
    simulation = request.json
    print(simulation)
    try: 
       _id= insert_simulation(simulation)
       print("Inserted ID: ", _id)
       return make_response(json.dumps({"simulationId": str(_id)}), 200, {'Content-Type': 'application/json'})
    except:
       e = sys.exc_info()[0]
       content = json.dumps({"error": e})
       status = 404
       return make_response(content,status, {"Content-Type": 'application/json'})

@app.route("/simulation_results", methods=['POST'])
def add_simulation_results():
    data= request.json
    print(data)
    try: 
       insert_results(data)
       return make_response(json.dumps({"inserted":True}), 200, {'Content-Type': 'application/json'})
    except:
       e = sys.exc_info()[0]
       content = json.dumps({"error": e})
       status = 404
       return make_response(content,status, {"Content-Type": 'application/json'})

@app.route("/simulation_results", methods=['GET'])
def get_simulation_results():
    simulation_id= request.args.get('simulationId')
    print(simulation_id)
    try: 
       return make_response(json.dumps({"data":get_results(simulation_id)}), 200, {'Content-Type': 'application/json'})
    except:
       e = sys.exc_info()[0]
       content = json.dumps({"error": e})
       status = 404
       return make_response(content,status, {"Content-Type": 'application/json'})

@app.route("/simulation", methods=['GET'])
def get_simulation_data():
    simulation_id= request.args.get('simulationId')
    print(simulation_id)
    try: 
       return make_response(json.dumps({"data":get_simulation(simulation_id)}), 200, {'Content-Type': 'application/json'})
    except:
       e = sys.exc_info()[0]
       content = json.dumps({"error": e})
       status = 404
       return make_response(content,status, {"Content-Type": 'application/json'})

@app.route("/simulations", methods=['GET'])
def get_simulations_data():
    try:
       return make_response(json.dumps({"data":get_simulations()}), 200, {'Content-Type': 'application/json'})
    except:
       e = sys.exc_info()[0]
       content = json.dumps({"error": e})
       status = 404
       return make_response(content,status, {"Content-Type": 'application/json'})





