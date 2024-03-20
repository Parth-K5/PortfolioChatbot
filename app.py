from flask import Flask, render_template, request, jsonify, session, abort, redirect
import torch
import generation
import threading
import time
import os
from datetime import timedelta
from uuid import uuid4
import time
import logging
import tuning

app = Flask(__name__)
app.secret_key = str(uuid4())
app.permanent_session_lifetime = timedelta(minutes=5)

MAX_LIMIT_TEXT = 50
MAX_QUERY_LIMIT = 10
TOKEN_COUNT = {}
RECENT_UID = ""

gen = generation.Trainer()


queryMap = {}
conversations = {}
#is_online = True

def commence_shutdown():
    time.sleep(5)
    os._exit(0)




@app.route("/")
def home():
    global MAX_LIMIT_TEXT
    global MAX_QUERY_LIMIT
    global queryMap
    global conversations
    global TOKEN_COUNT

    MAX_LIMIT_TEXT = MAX_LIMIT_TEXT
    MAX_QUERY_LIMIT = MAX_QUERY_LIMIT
    TOKEN_COUNT = TOKEN_COUNT
    queryMap = queryMap
    conversations = conversations

    client = f"{request.remote_addr}"
    #client = f"{request.remote_addr}:{request.environ.get('REMOTE_PORT')}"

    print(f"Connected: {client}")

    #is_online = True

    identifier = uuid4()

    if 'cached-query-count' not in session or len(queryMap) == 0:
        session['cached-query-count'] = {}
        session['cached-query-count'][str(identifier)] = 0
        TOKEN_COUNT[str(identifier)] = 0
        queryMap[str(identifier)] = 0
        conversations[str(identifier)] = []
        print(f"Registered {identifier} under {request.remote_addr} to {session['cached-query-count'][str(identifier)]}")

    if 'chatHistory' not in session:
        session['chatHistory'] = {}
        session['chatHistory']['log'] = [{"role": "system", "content": tuning.data_short}]
        session['chatHistory']['lastRequest'] = ''
        session['chatHistory']['lastReply'] = ''
        print(f"Initialized chat history with GPT parameters using ({tuning.count_tokens(tuning.data_short)}) tokens")
    #print(queryMap)

    #if str(client) not in queryMap:
        #queryMap[str(client)] = 0
    return render_template('index.html')

@app.route("/get", methods=['GET', 'POST'])
def chat():

    global MAX_LIMIT_TEXT
    global MAX_QUERY_LIMIT
    global queryMap
    global TOKEN_COUNT
    global conversations

    MAX_LIMIT_TEXT = MAX_LIMIT_TEXT
    MAX_QUERY_LIMIT = MAX_QUERY_LIMIT
    TOKEN_COUNT = TOKEN_COUNT
    conversations = conversations
    queryMap = queryMap

    try:
        identifier = list(session['cached-query-count'].keys())[0]
    except KeyError:
        return "Oops. The page needs to be reloaded"
    #print(f"Found cached identifier: {identifier}")

    client = f"{request.remote_addr}"
    #client = f"{request.remote_addr}:{request.environ.get('REMOTE_PORT')}"

    message = request.form["msg"]

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
                queryMap[str(identifier)] = 0
                session['chatHistory']['log'].clear()
                session.clear()
                for key in list(session.keys()):
                    session.pop(key)
                session.modified = True
                print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                return f"Override accepted. QueryMap for user {identifier}@{client} has been cleared. Reload the page."
            if keycodes.index(keycode) == 1:
                queryMap.clear()
                session['chatHistory']['log'].clear()
                app.secret_key = str(uuid4())
                session.clear()
                for key in list(session.keys()):
                    session.pop(key)
                session.modified = True
                print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                return f"Override accepted. System variable QueryMap has been cleared. Reload the page."
            if keycodes.index(keycode) == 2:
                queryMap[str(identifier)] = 0
                session['chatHistory']['log'].clear()
                session.clear()
                for key in list(session.keys()):
                    session.pop(key)
                session.modified = True
                MAX_QUERY_LIMIT = 999
                print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                return "Override accepted. QueryLimit set to unlimited. Reload the page"
            if keycodes.index(keycode) == 3:
                queryMap[str(identifier)] = 0
                MAX_QUERY_LIMIT = 10
                session['chatHistory']['log'].clear()
                session.clear()
                for key in list(session.keys()):
                    session.pop(key)
                session.modified = True
                print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                return "Override accepted. QueryLimit reset to 10. Reload the page"
            if keycodes.index(keycode) == 4:
                print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                shutdown = threading.Thread(target=commence_shutdown, name="Shutdown ChatBot")
                shutdown.start()
                shutdown.join()
                return "Override accepted. ChatBot terminated."

    prompt = message

    if session['cached-query-count'][str(identifier)] >= MAX_QUERY_LIMIT:
            print("Session request limit hit")
            print("GPT--> ****[Sleep response posted]****")
            return "It's getting late, I'm going to go sleep 😴"

    if prompt == session['chatHistory']['lastRequest']:
        print("Duplicate request handled")
        return session['chatHistory']['lastReply']

    #try:
    #print("\n")
    session['chatHistory']['log'].append({"role": "user", "content": prompt})
    start_gen = time.perf_counter()
    response = gen.gpt_gen(prompt, MAX_LIMIT_TEXT, session['chatHistory']['log'])
    print(f"GPT ({response[1]} tokens)--> {response[0]}")
    
    session['cached-query-count'][str(identifier)] += 1
    session['chatHistory']['lastRequest'] = prompt
    session['chatHistory']['lastReply'] = response[0]
    session['chatHistory']['log'].append({"role": "assistant", "content": response[0]})

    print(f"{session['cached-query-count'][str(identifier)]} requests during session for {client}")
    queryMap[str(identifier)] += 1
    TOKEN_COUNT[str(identifier)] += response[1]
    print(f"**** {str(client)} with UID: {identifier} has used up {queryMap[str(identifier)]}/{MAX_QUERY_LIMIT} queries and {TOKEN_COUNT[str(identifier)]} tokens in the session.****")

    session.modified = True
    
    return response[0]
    #except:
        #print("**** Hit OpenAI Rate Limit ****")

        #return "Uh oh I'm a little tired. Ask me something later"
    
if __name__ == "__main__":
    Flask.run(app)
