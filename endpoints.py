import json
import database
import sys
import os
from flask import Flask, make_response, request

app = Flask(__name__)

db = database.Database()
db.initialize()

@app.route('/task', methods=['POST'])
def create_task():
    value = request.json["value"]
    try:
        db.insert(value)
        content = json.dumps({"response": "ok"})
        status = 200
    except:
        e = sys.exc_info()[0]
        content = json.dumps({"error": e})
        status = 404
    return make_response(content, status, {'Content-Type': 'application/json'})

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    content = json.dumps({"response": "ok"})
    return make_response(content, 200, {'Content-Type': 'application/json'})


@app.route('/task/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    value = request.json["value"]
    try:
        db.update(task_id, value)
        content = json.dumps({"response": "ok"})
        status = 200
    except:
        e = sys.exc_info()[0]
        content = json.dumps({"error": e})
        status = 404
    return make_response(content, status, {'Content-Type': 'application/json'})

@app.route('/task', methods=['GET'])
def read_tasks():
    try:
        content = json.dumps(db.readAll("tarefas"))
        status = 200
    except:
        e = sys.exc_info()[0]
        content = json.dumps({"error": e})
        status = 404
    return make_response(content, status, {'Content-Type': 'application/json'})


@app.route('/task/<int:task_id>', methods=['GET'])
def read_task(task_id):
    try:
        content = json.dumps(db.read(task_id))
        status = 200
    except:
        e = sys.exc_info()[0]
        content = json.dumps({"error": e})
        status = 404
    return make_response(content, status, {'Content-Type': 'application/json'})


@app.route('/task/<int:task_id>', methods=['DELETE'])
def remove_tasks(task_id):
    try:
        db.remove(task_id)
        content = json.dumps({"response": "ok"})
        status = 200
    except:
        e = sys.exc_info()[0]
        content = json.dumps({"error": e})
        status = 404
    return make_response(content, status, {'Content-Type': 'application/json'})
