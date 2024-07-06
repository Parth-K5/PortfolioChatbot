from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS, cross_origin
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
import jwt

app = Flask(__name__)

CORS(app)

app.secret_key = str(uuid4())
app.permanent_session_lifetime = timedelta(minutes=5)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = app.secret_key

MAX_LIMIT_TEXT = 600
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
        session['chatHistory']['log'] = []
        session['chatHistory']['log'] = []
        session['chatHistory']['lastRequest'] = ''
        session['chatHistory']['lastReply'] = ''
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

    if not session['chatHistory']['log']:
        session['chatHistory']['log'] = [{"role": "system", "content": tuning.data_short}]
        print("System context given to GPT")
        print(f"Initialized chat history with GPT parameters using ({tuning.count_tokens(tuning.data_short)}) tokens")
    else:
        print("Found existing context from previous replies")

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
            if keycodes.index(keycode) == 5:
                print(f"SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                return f"You have {MAX_QUERY_LIMIT-session['cached-query-count'][str(identifier)]} queries left out of the {MAX_QUERY_LIMIT} total set"


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

    #print(f"{session['cached-query-count'][str(identifier)]} requests during session for {client}")
    queryMap[str(identifier)] += 1
    TOKEN_COUNT[str(identifier)] += response[1]
    print(f"**** {str(client)} with UID: {identifier} has used up {queryMap[str(identifier)]}/{MAX_QUERY_LIMIT} queries and {TOKEN_COUNT[str(identifier)]} tokens in the session.****")

    session.modified = True
    
    return response[0]
    #except:
        #print("**** Hit OpenAI Rate Limit ****")

        #return "Uh oh I'm a little tired. Ask me something later"

API_SESSIONS = {}
API_USAGE = {}

@cross_origin()
@app.route("/api/send-message", methods=['POST'])
def send_message_api():

    global API_SESSIONS
    global MAX_QUERY_LIMIT
    global API_USAGE

    API_SESSIONS = API_SESSIONS
    MAX_QUERY_LIMIT = MAX_QUERY_LIMIT
    API_USAGE = API_USAGE

    session_id = request.json.get('sessionId') or str(uuid4())

    # Store session ID in session
    session['session_id'] = session_id
    # Retrieve or initialize user's API call count

    if str(session_id) not in API_SESSIONS:
        session['api_calls'] = session.get('api_calls', 0)
        API_SESSIONS[str(session_id)] = session['api_calls']
        API_USAGE[str(session_id)] = 0
        print(f"Initialized new API source with ID: {session_id}")

    else:
        session['api_calls'] = API_SESSIONS[str(session_id)]

    print(f"\n\nAPI DATA: {API_SESSIONS}")

    # Retrieve other data from the request
    message = request.json.get('message')
    chat_history = request.json.get('chatHistory')
    print(f"Received API request from user {session['session_id']} | Message: {message} ({len(message)})")
    if len(message) > 100:
        return jsonify({'error': f'ChatBot has been tampered with. Please reload the page.'}), 400

    chatHistory = request.json.get('chatHistory')
    if not chatHistory or chatHistory == []:
        chatHistory.insert(0, {"role": "system", "content": tuning.data_short})
    print(f"Received following chat_history: {chatHistory}")
    if message:
        # Process the message using your chatbot logic
        
        keycodes = open("../PortfolioChatBot Resources/OpenAI/overrides.txt", 'r').readlines()

        if keycodes[-1][-1] != "\n":
            keycodes[-1] = keycodes[-1]+"\n"

        for keycode in keycodes:
            if message == keycode[:-1]:
                if keycodes.index(keycode) == 0:
                    API_SESSIONS[str(session_id)] = 0
                    session.modified = True
                    print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                    return jsonify({'session_id': session_id, 'api_calls': session['api_calls'], 'response': f"Override accepted. SessionAPI for user {str(session_id)} has been cleared. Reload the page."})
                if keycodes.index(keycode) == 1:
                    API_SESSIONS = []
                    session.modified = True
                    print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                    return jsonify({'session_id': session_id, 'api_calls': session['api_calls'], 'response': f"Override accepted. System variable SessionAPI has been cleared. Reload the page."})
                if keycodes.index(keycode) == 2:
                    MAX_QUERY_LIMIT = 999
                    print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                    return jsonify({'session_id': session_id, 'api_calls': session['api_calls'], 'response': "Override accepted. APILimit set to unlimited. Reload the page"})
                if keycodes.index(keycode) == 3:
                    MAX_QUERY_LIMIT = 10
                    session.modified = True
                    print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                    return jsonify({'session_id': session_id, 'api_calls': session['api_calls'], 'response': "Override accepted. APILimit reset to 10. Reload the page"})
                if keycodes.index(keycode) == 4:
                    print(f"***** SYSTEM ADMIN: COMMAND CODE [{message}] ACCEPTED *****")
                    shutdown = threading.Thread(target=commence_shutdown, name="Shutdown ChatBot")
                    shutdown.start()
                    shutdown.join()
                    return jsonify({'session_id': session_id, 'api_calls': session['api_calls'], 'response': "Override accepted. ChatBot terminated."})
                if keycodes.index(keycode) == 5:
                    metrics = f"UID: {str(session_id)} has used up {API_SESSIONS[str(session_id)]} API requests and {API_USAGE[str(session_id)]} tokens."
                    return jsonify({'session_id': session_id, 'api_calls': session['api_calls'], 'response': metrics})

        if API_SESSIONS[str(session_id)] >= MAX_QUERY_LIMIT:
            return jsonify({'session_id': session_id, 'api_calls': session['api_calls'], 'response': "Reached API Limit"})

        response = gen.gpt_gen_API(message, MAX_LIMIT_TEXT, chatHistory)
        API_SESSIONS[str(session_id)] += 1
        session['session_id'] = session_id 
        print(f"ID: {session_id} has made {API_SESSIONS[str(session_id)]} requests using the API totaling {response[1]} tokens")
        API_USAGE[str(session_id)] += response[1]
        return jsonify({'session_id': session_id, 'api_calls': session['api_calls'], 'response': response[0]})
    else:
        return jsonify({'error': 'Message not provided'}), 400
    
if __name__ == "__main__":
    Flask.run(app)
