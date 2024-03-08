from openai import OpenAI
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging


client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=open("../PortfolioChatBot Resources/OpenAI/key.txt", 'r').read(),
)

def gpt_gen(prompt, allocatedTokens):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=allocatedTokens
    )
    print(f"GPT ----> {response.choices[0].message.content}")
    #print(response.choices[0].message.content.strip())
    return response.choices[0].message.content.strip()

def dialo_gen(prompt):

    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large")
    model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-large")
    logging.getLogger('transformers').setLevel(logging.ERROR)
    
    prompt_ids = tokenizer.encode(str(prompt) + tokenizer.eos_token, return_tensors='pt')

    bot_ids = torch.cat([history_ids, prompt_ids], dim=-1)

    history_ids = model.generate(bot_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

    return tokenizer.decode(history_ids[:, bot_ids.shape[-1]:][0], skip_special_tokens=True)

#a = chat_gpt('Write me a 1 page essay about Feudalism in Japan')
#print(a)