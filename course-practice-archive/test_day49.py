from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
import datetime

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpeg"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_path(filename):
    ext = filename.rsplit(".", 1)[1].lower()
    if ext == "pdf":
        folder = "uploads/documents"
    elif ext in {"png", "jpg", "jpeg"}:
        folder = "uploads/images"
    else:
        folder = "uploads/other"
    os.makedirs(folder, exist_ok=True)
    return folder

def unique_filename(filename):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{filename}"

@app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    return "File too large - maximum 2MB", 413

@app.route("/upload", methods=["GET", "POST"])
def upload():
    uploaded = []
    files = request.files.getlist("documents")
    if request.method == "POST":
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = unique_filename(filename)
                folder = get_upload_path(filename)
                filepath = os.path.join(folder, filename)
                file.save(filepath)
                uploaded.append({
                    "filename": filename,
                    "size": os.path.getsize(filepath),
                    "path": filepath
                })

        return jsonify({
            "message": f"{len(uploaded)} file(s) uploaded successfully",
            "files": uploaded
        }), 200
    return render_template("test_upload.html")

if __name__ == "__main__":
    app.run(debug=True)

    