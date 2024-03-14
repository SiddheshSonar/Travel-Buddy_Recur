from langchain.schema import HumanMessage, AIMessage
from langchain_community.chat_models.huggingface import ChatHuggingFace
from langchain.prompts import PromptTemplate
from flask import Flask, jsonify, request
from langchain_community.llms import HuggingFaceHub
from flask_cors import CORS
import yfinance as yf
import os
import requests
import json
import base64
from flask import Flask, jsonify, request

from dotenv import load_dotenv, get_key
load_dotenv()

app = Flask(__name__)

CORS(app)

os.environ["HUGGINGFACEHUB_API_TOKEN"] = get_key(key_to_get="HUGGINGFACEHUB_API_KEY",dotenv_path=".env")

llm = HuggingFaceHub(
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
    task="text-generation",
    model_kwargs={
        "max_new_tokens": 512,
        "top_k": 30,
        "temperature": 0.3,
        "repetition_penalty": 1.03,
    },
)

def chatwithbot(txt:str):
    chat_model = ChatHuggingFace(llm=llm)
    user_template= PromptTemplate(template="{user_input}", input_variables=["user_input"])
    messages = [
    HumanMessage(content="..."),
    AIMessage(content="You're a helpful travel planner and tour guide, user asks their query and you have to respond accuretly and strictly in same language."),
    HumanMessage(content=user_template.format(user_input=txt)),
    ]
    res = chat_model(messages).content
    return res


@app.route('/chat',methods=["POST"])
def chat():
    try:
        txt = request.form['text']
        res = chatwithbot(txt)
        res = str(res)
        last_inst_index = res.rfind("[/INST]")
        res = res[last_inst_index + len("[/INST]"):].strip()
        print(res)
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/classify-image', methods=['POST'])
def classify_image():
    try:
        url = "https://picarta.ai/classify"
        api_token = "08CPS63DU3BANXP5EBC8"
        headers = {"Content-Type": "application/json"}

        # Read the image from a local file
        with open("./Taj-Mahal.jpg", "rb") as image_file:
            img_path = base64.b64encode(image_file.read()).decode('utf-8')

        # Prepare the payload
        payload = {"TOKEN": api_token, "IMAGE": img_path}

        # Send the POST request with the payload as JSON data
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            return jsonify(result)
        else:
            return jsonify({"error": f"Request failed with status code: {response.status_code}"})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)