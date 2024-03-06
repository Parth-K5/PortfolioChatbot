from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging


tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-large")
logging.getLogger('transformers').setLevel(logging.ERROR)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/get", methods=['GET', 'POST'])
def chat():
    message = request.form["msg"]
    input = message
    return get_reply(input)

def get_reply(text):
    for dialogue in range(5):
        prompt_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')

        bot_ids = torch.cat([history_ids, prompt_ids], dim=-1) if dialogue > 0 else prompt_ids

        history_ids = model.generate(bot_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

        return tokenizer.decode(history_ids[:, bot_ids.shape[-1]:][0], skip_special_tokens=True)
    
if __name__ == "__main__":
    app.run(debug=True)
