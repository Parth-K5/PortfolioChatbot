from flask import Flask, render_template, request, jsonify, session, abort, redirect
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging
import uuid
import generation
import threading
import time

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
logging.getLogger('transformers').setLevel(logging.ERROR)

app = Flask(__name__)

MAX_lIMIT_TEXT = 50
MAX_QUERY_LIMIT = 3


queryMap = {}
connMap = {}
#is_online = True


@app.route("/")
def home():
    client = f"{request.remote_addr}"
    #client = f"{request.remote_addr}:{request.environ.get('REMOTE_PORT')}"

    print(f"Connected: {client}")
    #is_online = True

    if str(client) not in queryMap:
        queryMap[str(client)] = 0
    return render_template('index.html')

@app.route("/get", methods=['GET', 'POST'])
def chat():

    client = f"{request.remote_addr}"
    #client = f"{request.remote_addr}:{request.environ.get('REMOTE_PORT')}"

    message = request.form["msg"]

    print(f"QueryMap: {queryMap}")

    print(f"Message Content Size: {len(message)} | Message Content: '{message}'")
    
    if len(message) > MAX_lIMIT_TEXT:
        print("**** Detected chatbot tampering. Reload demanded ****")
        return "The chatbot has been tampered with. Reload the page for proper functionality"
    if len(message) == 0:
        print("**** Message with no content received ****")
        return "Please type in a valid prompt"
    if message == "parthk2004xCLEAR":
        queryMap.clear()
        return "Override accepted. QueryMap has been cleared. Reload the page"


    prompt = message

    if queryMap[str(client)] >= MAX_QUERY_LIMIT:
            print("GPT--> ****[Sleep response posted]****")
            return "It's getting late, I'm going to go sleep 😴"

    try:
        response = generation.gpt_gen(prompt, MAX_lIMIT_TEXT)

        queryMap[client] += 1
        print(f"**** {str(client)} has used up {queryMap[str(client)]}/{MAX_QUERY_LIMIT} queries ****")
    
        return response
    except:
        print("**** Hit OpenAI Rate Limit ****")
        return "Uh oh I'm a little tired. Ask me something later"
    
if __name__ == "__main__":
    app.run()
