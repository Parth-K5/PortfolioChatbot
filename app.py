from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging
#import langfeatures
#import googletrans
import generation

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
logging.getLogger('transformers').setLevel(logging.ERROR)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

MAX_lIMIT = 50

@app.route("/get", methods=['GET', 'POST'])
def chat():
    message = request.form["msg"]
    print(f"Message Content Size: {len(message)}")
    if len(message) > MAX_lIMIT:
        print("Detected chatbot tampering. Reload demanded")
        return "The chatbot has been tampered with. Reload the page for proper functionality"
    input = message
    return generation.gpt_gen(input, MAX_lIMIT)

    
if __name__ == "__main__":
    app.run()
