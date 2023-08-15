import os
import datetime
import sys
import json

from flask import Flask, render_template, request, jsonify

from werkzeug.utils import secure_filename

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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)