import os
import datetime
import sys
import json
import time
import os

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import LanceDB
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
import lancedb
import openai

from flask import Flask, render_template, request, jsonify
from langchain.text_splitter import RecursiveCharacterTextSplitter
from werkzeug.utils import secure_filename

<<<<<<< HEAD
os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = "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"
=======
from deep_motion import DeepMotionHandler
from sketchfab import SketchfabHandler

os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = "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"
>>>>>>> 323598a121e41dd3b6f065742568eb04930e8170



loader = DirectoryLoader("../langchain_documents/")

loaded_documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=100)
documents = text_splitter.split_documents(loaded_documents)
#documents = TextSplitter().split_documents(documents)
print(type(documents))
embeddings = OpenAIEmbeddings()

db = lancedb.connect("../lanceDB")
table = db.open_table("my_table")
#
# table = db.create_table(
#     "my_table",
#     data=[
#         {
#             "vector": embeddings.embed_query("Hello World"),
#             "text": "Hello World",
#             "id": "1",
#         }
#     ],
#     mode="overwrite",
#
# )

docsearch = LanceDB.from_documents(documents, embeddings, connection=table)

UPLOAD_FOLDER = '/uploaded_videos'
ALLOWED_EXTENSIONS = {'mp4', 'mov'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

current_convert_config = {"trainee_url": "", "coach_url": ""}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/shottracer")
def shottracer():
    print("here", flush=True)
    return render_template("shottracer.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/process', methods=['POST'])
def process():
    print("in process", flush=True)
    print(request.data, flush=True)
    data = json.loads(request.data)

    result = data['value']
    

    current_convert_config["trainee_url"] = "static/videos/" + result

    print("selected trainee: " + current_convert_config["trainee_url"], flush=True)

    return jsonify(result=result)

@app.route('/coach_select', methods=["POST"])
def coach_select():

    data = json.loads(request.data)
    result = data['value']


    current_convert_config["coach_url"] = "static/videos/" + result
    print("selected coach: " + current_convert_config["coach_url"], flush=True)

    return jsonify(result=result)

@app.route('/convert', methods=["POST"])
def convert():
    print("converting", flush=True)

    if current_convert_config["trainee_url"] == "" or current_convert_config["coach_url"] == "":
        print(current_convert_config)
        return current_convert_config

    deep_motion = DeepMotionHandler()

    trainee_resp, trainee_input = deep_motion.new_job(current_convert_config["trainee_url"], download=False)
    coach_resp, coach_input = deep_motion.new_job(current_convert_config["coach_url"], download=False)

    trainee_fbx = deep_motion.download_job(trainee_resp, trainee_input)
    coach_fbx = deep_motion.download_job(coach_resp, coach_input)

    print(trainee_fbx, flush=True)
    print(coach_fbx, flush=True)

    sketchfab_handler = SketchfabHandler()
    trainee_url = sketchfab_handler.upload(trainee_fbx)
    coach_url = sketchfab_handler.upload(coach_fbx)

    print(trainee_url, flush=True)
    print(coach_url, flush=True)

    while not sketchfab_handler.poll_processing_status(trainee_url) or not sketchfab_handler.poll_processing_status(coach_url):
        time.sleep(1)

    return [trainee_url.rsplit('/', 1)[-1], coach_url.rsplit('/', 1)[-1]]


@app.route("/search", methods=["POST"])
def docSearch():
    print("in search", flush=True)
    print(request.data, flush=True)
    data = json.loads(request.data)
    question = data['question']
    docs = docsearch.similarity_search(question)

    prompt = f"""Given the question: {question} and this context: {docs}
    Answer the question as best as possible. Use any relevant information from the context to
    enrich your answer.
    Final Answer:
    """

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )

    generated_text = response.choices[0].text

    return jsonify(result=generated_text)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)