from openai import OpenAI
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging
import json
from tuning import *
import os
import sys
import openai
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader, TextLoader, WebBaseLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings


class Trainer:
    def __init__(self):
        self.dataset = []
        self.output_name = "dataset.jsonl"

        self.OPENAIClient = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=open("../PortfolioChatBot Resources/OpenAI/key.txt", 'r').read(),
        )
        os.environ['OPENAI_API_KEY'] = open("../PortfolioChatBot Resources/OpenAI/key.txt", 'r').read()

        #self.loader = TextLoader("data/data.txt")
        #self.vectorindex = VectorstoreIndexCreator().from_loaders([self.loader])

        #self.initialize_adv()

    def initialize_adv(self):
        self.textLoader = TextLoader("data/data.txt")
        self.documents = self.textLoader.load()

        self.template = """Answer the question in your own words from the 
        context given to you.
        If questions are asked where there is no relevant context available, please answer from 
        what you know.

        Context: {context}

        Human: {question}
        Assistant:"""

        self.prompt = PromptTemplate(input_variables=["context",  "question"], template=self.template)

        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        self.documents = self.text_splitter.split_documents(self.documents)

        self.embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

        self.vectorstore = Chroma.from_documents(self.documents, self.embedding_function)


        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def gpt_gen(self, prompt, allocatedTokens, history):
        response = self.OPENAIClient.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history,
            #messages=[{"role": "user", "content": prompt}],
            max_tokens=allocatedTokens,
        )
        print(f"GPT ----> {response.choices[0].message.content}")
        #print(response.choices[0].message.content.strip())
        return (response.choices[0].message.content.strip(), response.usage.completion_tokens)
    
    def personalized_gpt_gen(self, prompt, allocatedTokens, history):
        response = self.OPENAIClient.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history,
            #messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )
        print(f"GPT ----> {response.choices[0].message.content}")
        #print(response.choices[0].message.content.strip())
        return response.choices[0].message.content.strip()
    
    def dialo_gen(self, prompt):

        tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large")
        model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-large")
        logging.getLogger('transformers').setLevel(logging.ERROR)
        
        prompt_ids = tokenizer.encode(str(prompt) + tokenizer.eos_token, return_tensors='pt')

        bot_ids = torch.cat([history_ids, prompt_ids], dim=-1)

        history_ids = model.generate(bot_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

        return tokenizer.decode(history_ids[:, bot_ids.shape[-1]:][0], skip_special_tokens=True)

    def custom_gpt(self, query, TOKENS_ALLOCATED=50, chat_history=None):
        if not chat_history:
            chat_history = []
        resp = self.vectorindex.query(query, llm=ChatOpenAI(max_tokens=TOKENS_ALLOCATED))
        print(f"GPT ----> {resp}")
        return resp

    def custom_gpt_with_mem(self, prompt, TOKENS_ALLOCATED=50, chat_history=None):
        qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(max_tokens=50), retriever=self.vectorstore.as_retriever(), memory=self.memory,chain_type_kwargs={'prompt': prompt})
        response = qa({"query": prompt})
        print(f"GPT ----> {response}")
        return response

    def write_dataset(self, overwrite: bool, customName: str=None):
        
        training_data = self.dataset

        json_data = json.dumps(training_data, indent=2)

        if customName and os.path.exists(os.path.abspath(customName)) == False:
            if customName.split(".")[1] == "jsonl":
                output = customName
                print(f"Custom file name: {customName} accepted")
            else:
                return "Please n"
        else:
            output = self.output_name

        if os.path.exists(os.path.abspath(output)) and overwrite == False:
            return "Could not create dataset. Filename already exists and overwriting permissions not given"

        
        with open(output, 'w') as jsonl_file:
            for entry in self.dataset:
                json.dump(entry, jsonl_file)
                jsonl_file.write("\n")
        
        print(f"Training data has been saved to {output}")

    def add_response(self, question: str, answer: str):
        system = {"messages": [{"role": "system", "content": "You are an assistant. Answer the user with their questions"}]}
        prompt = {"role": "user", "content": question}
        completion = {"role": "assistant", "content": answer}
        system['messages'].append(prompt)
        system['messages'].append(completion)
        self.dataset.append(system)
        return "Added response to data"

    def add_responses(self):
        while True:
            question = input("Prompt: ")
            answer = input("Answer: ")
            print(f"'{question}' -> '{answer}'")
            confirm = input("Confirm(y/n). To leave, type 'done': ")
            if confirm == "y":
                system = {"messages": [{"role": "system", "content": "You are an assistant. Answer the user with their questions"}]}
                prompt = {"role": "user", "content": question}
                completion = {"role": "assistant", "content": answer}
                system['messages'].append(prompt)
                system['messages'].append(completion)
                self.dataset.append(system)
                print("Added response to data")
            elif confirm == "done":
                return
            else:
                print("Confirmation failed")

    def delete_response(self, question: str):
        for line in self.dataset:
            if question in line:
                item = self.dataset.pop(self.dataset.index(line))
            else:
                return f"Response not found: {item}"
        return f"Response deleted: {item}"

    def replace_dataset(self, newDataset: list):
        try:
            json.dumps(newDataset)
        except:
            return "Invalid format"
        self.dataset = newDataset
        return "Replaced dataset"
    
    def print_dataset(self):
        print("Current dataset:")
        print(self.dataset if self.dataset else "Empty")
    
#a = chat_gpt('Write me a 1 page essay about Feudalism in Japan')
#print(a)