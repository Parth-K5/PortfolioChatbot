from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging
import generation

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
logging.getLogger('transformers').setLevel(logging.ERROR)

app = Flask(__name__)

queryMap = {}
#is_online = True

@app.route("/")
def home():
    print(f"Connected: {request.remote_addr}")
    #is_online = True

    if str(request.remote_addr) not in queryMap:
        queryMap[str(request.remote_addr)] = 0
    return render_template('index.html')

MAX_lIMIT_TEXT = 50
MAX_QUERY_LIMIT = 3

@app.route("/get", methods=['GET', 'POST'])
def chat():

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

        queryMap[str(request.remote_addr)] += 1
        print(f"**** {request.remote_addr} has used up {queryMap[(str(request.remote_addr))]}/{MAX_QUERY_LIMIT} queries ****")
        
        return response
    except:
        print("**** Hit OpenAI Rate Limit ****")
        return "Uh oh I'm a little tired. Ask me something later"
    
if __name__ == "__main__":
    app.run()
