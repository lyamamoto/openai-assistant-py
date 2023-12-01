from flask import Flask, request
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

from lib.credit_assistant import CreditAssistant
assistant = CreditAssistant("supersim-ass", "SuperSim")

import json

@app.route("/thread", methods=["GET"])
@cross_origin()
def getThread():
    return assistant.startNewThread().id

@app.route("/thread/<threadId>/message", methods=["GET"])
@cross_origin()
def getMessages(threadId: str):
    rawMessages = assistant.getMessages(threadId)
    messages = list(map(lambda message: {
        "id": message.id,
        "role": message.role,
        "body": message.content[0].text.value,
        "created_at": message.created_at,
    }, rawMessages)) if rawMessages is not None else []
    return json.dumps(messages)

@app.route("/thread/<threadId>/message", methods=["POST"])
@cross_origin()
def postMessage(threadId: str):
    requestBody = request.get_json()
    message = assistant.addMessage(threadId, requestBody["message"])
    return message.id

@app.route("/thread/<threadId>/run", methods=["POST"])
@cross_origin()
def runThread(threadId: str):
    run = assistant.runThread(threadId)
    return run.id

@app.route("/thread/<threadId>/run/<runId>/status", methods=["GET"])
@cross_origin()
def getRunStatus(threadId: str, runId: str):
    run = assistant.getRun(threadId, runId)
    return json.dumps(run.status)

if __name__ == "__main__":
    app.run()