from flask import Flask, render_template, request, jsonify, session, abort, redirect
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging
import generation
import threading
import time
import os

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
logging.getLogger('transformers').setLevel(logging.ERROR)

app = Flask(__name__)
app.secret_key = "parthk5101x"

MAX_LIMIT_TEXT = 50
MAX_QUERY_LIMIT = 3


queryMap = {}
connMap = {}
#is_online = True

def commence_shutdown():
    time.sleep(5)
    os._exit(0)


@app.route("/")
def home():
    global MAX_LIMIT_TEXT
    global MAX_QUERY_LIMIT

    MAX_LIMIT_TEXT = MAX_LIMIT_TEXT
    MAX_QUERY_LIMIT = MAX_QUERY_LIMIT

    client = f"{request.remote_addr}"
    #client = f"{request.remote_addr}:{request.environ.get('REMOTE_PORT')}"

    print(f"Connected: {client}")
    #is_online = True

    if str(client) not in queryMap:
        queryMap[str(client)] = 0
    return render_template('index.html')

@app.route("/get", methods=['GET', 'POST'])
def chat():

    global MAX_LIMIT_TEXT
    global MAX_QUERY_LIMIT

    MAX_LIMIT_TEXT = MAX_LIMIT_TEXT
    MAX_QUERY_LIMIT = MAX_QUERY_LIMIT



    client = f"{request.remote_addr}"
    #client = f"{request.remote_addr}:{request.environ.get('REMOTE_PORT')}"

    message = request.form["msg"]

    #print(f"QueryMap: {queryMap}")
    print("\n\n")
    print(f"Message Content Size: {len(message)} | Message Content: '{message}'")
    
    if len(message) > MAX_LIMIT_TEXT:
        print("**** Detected chatbot tampering. Reload demanded ****")
        return "The chatbot has been tampered with. Reload the page for proper functionality"
    if len(message) == 0:
        print("**** Message with no content received ****")
        return "Please type in a valid prompt"

    keycodes = open("../PortfolioChatBot Resources/OpenAI/overrides.txt", 'r').readlines()

    if keycodes[-1][-1] != "\n":
        keycodes[-1] = keycodes[-1]+"\n"

    for keycode in keycodes:
        if message == keycode[:-1]:
            if keycodes.index(keycode) == 0:
                queryMap.clear()
                print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                return "Override accepted. QueryMap has been cleared. Reload the page."
            if keycodes.index(keycode) == 1:
                queryMap.clear()
                MAX_QUERY_LIMIT = 999
                print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                return "Override accepted. QueryLimit set to unlimited. Reload the page"
            if keycodes.index(keycode) == 2:
                queryMap.clear()
                MAX_QUERY_LIMIT = 3
                print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                return "Override accepted. QueryLimit reset to 3. Reload the page"
            if keycodes.index(keycode) == 3:
                shutdown = threading.Thread(target=commence_shutdown, name="Shutdown ChatBot")
                shutdown.start()
                shutdown.join()
                print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                return "Override accepted. ChatBot terminated."

    prompt = message

    if 'requests' not in session:
        print(f"Initialized cache for {client}")

    session['requests'] = queryMap[str(client)]

    print(f"{session['requests']} requests during session for {client}")

    if session['requests'] >= MAX_QUERY_LIMIT:
            print("Session request limit hit")
            print("GPT--> ****[Sleep response posted]****")
            return "It's getting late, I'm going to go sleep 😴"

    try:
        response = generation.gpt_gen(prompt, MAX_LIMIT_TEXT)

        queryMap[client] += 1
        print(f"**** {str(client)} has used up {queryMap[str(client)]}/{MAX_QUERY_LIMIT} queries ****")
    
        return response
    except:
        print("**** Hit OpenAI Rate Limit ****")
        return "Uh oh I'm a little tired. Ask me something later"
    
if __name__ == "__main__":
    app.run()
