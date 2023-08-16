import os
import datetime
import sys
import json
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

os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = "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"



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

    return jsonify(result=result)

"""@app.route("/", methods=["GET", "POST"])
def trainee_video_upload():
    print("here", flush=True)
    f = request.files['file']
    print("test", flush=True)
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], f))
    return render_template("about.html")"""

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