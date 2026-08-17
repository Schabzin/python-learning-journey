import datetime
import os
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request
from flask import send_from_directory, render_template

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg"}

app = Flask(__name__)

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
    ext = filename.rsplit(".", 1)[1].lower()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{filename}"



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
    return render_template("uploads.html")
    
@app.route("/files")
def list_files():
    all_files = []
    for folder in ["documents", "images", "other"]:
        path = os.path.join("uploads", folder)
        if os.path.exists(path):
            for filename in os.listdir(path):
                all_files.append({
                    "filename": filename,
                    "folder": folder,
                    "size": os.path.getsize(os.path.join(path, filename))
                })
    return jsonify(all_files)

@app.route("/download/<folder>/<filename>")
def download(folder, filename):
    directory = os.path.join("uploads", folder)
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)