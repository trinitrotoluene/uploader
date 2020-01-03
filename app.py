from flask import Flask, Response, request, send_file
from werkzeug.utils import secure_filename
from PIL import Image

import random, string, os, secrets, json, urllib

app = Flask(__name__)

VALID_EXTENSIONS = [ "png", "jpg", "jpeg", "gif", "mp4", "webp" ]
DESTINATION = "static"
FILE_NAME_LENGTH = 7
KEYS = "keys.json"

@app.route("/<filename>", methods=['GET'])
def showfile(filename):
    path = os.path.join(DESTINATION, filename)
    if is_safe_path(path) and os.path.exists(path):
        return send_file(path)
    else:
        return "Not Found", 404

@app.route("/upload", methods=["POST"])
def upload():
    # Validate Method and Content-Type
    if not request.method == "POST" or not request.content_type.split(";")[0] == "multipart/form-data":
        return "Bad Request", 400
    # Check for existence of a key in request headers
    if not request.headers.has_key("Authorization"):
        return "Unauthorized", 401 

    valid = False
    # Validate key and log it
    with open("keys.json", "r") as userfile:
        users = json.load(userfile)
        for key in users.keys():
            if request.headers["Authorization"] == key:
                valid = True
                # Log which user uploaded the file
    
    if not valid:
        return "Forbidden", 403
    
    # Try to load image
    filecontent = request.files["upload"]
    if not is_allowed_file(filecontent.filename):
        return "Bad Request", 400
    
    try:
        # Strip EXIF by loading and resaving the image
        image = Image.open(filecontent)
        
         # Save image with random filename
        filename = secrets.token_urlsafe(FILE_NAME_LENGTH) + "." + get_extension(filecontent.filename)

        targetpath = os.path.join(DESTINATION, filename)

        if is_safe_path(targetpath):
            image.save(targetpath)
        else:
            return "Bad Request", 400
        # Return JSON with URL
        return json.dumps({
            "url": urllib.parse.urljoin(request.host_url, filename)
        }), 200
    except:
        return "Bad Request", 400
   

if __name__ == "__main__":
    app.run(host='127.0.0.1')

def is_safe_path(path):
    return os.path.abspath(path).startswith(os.getcwd())

def get_extension(filename):
    return filename.rsplit(".", 1)[1].lower()

def is_allowed_file(filename):
    return '.' in filename and \
        get_extension(filename) in VALID_EXTENSIONS