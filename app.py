from flask import Flask, render_template, request, jsonify, session
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging
import uuid
import generation

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
logging.getLogger('transformers').setLevel(logging.ERROR)

app = Flask(__name__)

queryMap = {}
connMap = {}
#is_online = True

@app.route("/")
def get_conn_id():
    if 'client_id' not in session:
        session['client_id'] = str(uuid.uuid64())
        connMap[session['client_id']] = request.remote_addr

    print(f"Client ID: {session['client_id']} - Connected clients: {connMap}")
    return f"Client ID: {session['client_id']} - Connected clients: {connMap}"

@app.route("/")
def home():

    client = f"{request.remote_addr}:{request.environ.get('REMOTE_PORT')}"

    print(f"Connected: {client}")
    #is_online = True

    if str(client) not in queryMap:
        queryMap[client] = 0
    return render_template('index.html')

MAX_lIMIT_TEXT = 50
MAX_QUERY_LIMIT = 3

@app.route("/get", methods=['GET', 'POST'])
def chat():

    client = f"{request.remote_addr}:{request.environ.get('REMOTE_PORT')}"

    message = request.form["msg"]

    print(queryMap)

    print(f"Message Content Size: {len(message)} | Message Content: '{message}'")
    if len(message) > MAX_lIMIT_TEXT:
        print("**** Detected chatbot tampering. Reload demanded ****")
        return "The chatbot has been tampered with. Reload the page for proper functionality"
    if len(message) == 0:
        print("**** Message with no content received ****")
        return "Please type in a valid prompt"
    prompt = message
    
    if queryMap[str(request.remote_addr)] >= MAX_QUERY_LIMIT:
            print("**** Sleep response posted ****")
            return "It's getting late, I'm going to go sleep 😴"

    try:
        response = generation.gpt_gen(prompt, MAX_lIMIT_TEXT)

        queryMap[client] += 1
        print(f"**** {client} has used up {queryMap[client]}/{MAX_QUERY_LIMIT} queries ****")
        
        return response
    except:
        print("**** Hit OpenAI Rate Limit ****")
        return "Uh oh I'm a little tired. Ask me something later"
    
if __name__ == "__main__":
    app.run()
