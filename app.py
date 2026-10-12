from flask import Flask, jsonify, render_template, request
from services.pdf_character_loader import load_character_from_pdf
import threading
import webbrowser
from pathlib import Path
from uuid import uuid4


# create application
app = Flask(__name__)

# create app frontend
@app.route("/") # address "/" calls index()
def index():
    """Display the main frontend page."""
    return render_template("index.html")


CHARACTER_DIR = Path("data/characters")
loaded_characters = {}

# Search character PDFs and pass filenames to frontend for display
@app.get("/api/characters/pdfs")
def get_character_pdfs():
    pdf_files = [
        file.name
        for file in CHARACTER_DIR.glob("*.pdf")
        if file.is_file()
    ]

    return jsonify(sorted(pdf_files))


@app.post("/api/characters")
def add_character():

    # get value of key "filename" form the json file
    data = request.get_json("filename")
    if not data or not data.get("filename"):
        return jsonify({
            "success": False,
            "error": "Kein Dateiname übergeben."
        }), 400

    filename = data["filename"]

    # only allow for file names not paths
    if Path(filename).name != filename or Path(filename).suffix.lower() != ".pdf":
        return jsonify({
            "success": False,
            "error": "Ungültiger PDF-Dateiname."
        }), 400

    # add correct path to the file name
    pdf_path = CHARACTER_DIR / filename

    if not pdf_path.is_file():
        return jsonify({
            "success": False,
            "error": "PDF-Datei nicht gefunden."
        }), 404

    print("Ausgewählte PDF:", pdf_path)

    creature = load_character_from_pdf(str(pdf_path))

    if creature is None:
        return jsonify({
            "success": False,
            "error": "Die PDF enthält keine auslesbaren Formularfelder."
        }), 422

    character_id = str(uuid4())
    loaded_characters[character_id] = creature

    return jsonify({
        "success": True,
        "character": {
            "id": character_id,
            "name": creature.name
        }
    })


# only POST requests (send data to server)
@app.route("/api/process", methods=["POST"])
def process():
    """
    Receive data from the frontend and return a result.

    Replace the example processing with your existing backend function.
    """

    # receive data from the frontend, e.g. attack information
    # silent=True gives None in case of missing data instead of triggering an exception
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({
            "success": False,
            "error": "No JSON data was received."
        }), 400

    # check if there is a key "text"
    user_text = str(data.get("text", "")).strip()
    
    # if there is no "text" key raise error
    if not user_text:
        return jsonify({
            "success": False,
            "error": "Please enter some text."
        }), 400

    try:
        # Replace this with your own Python backend logic.
        result = user_text.upper()

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception:
        # In a production application, log the actual exception here.
        return jsonify({
            "success": False,
            "error": "The backend could not process the request."
        }), 500


# starts the application in the browser
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    # open prowser after 1 second
    threading.Timer(1, open_browser).start()
    # run flast server created above
    app.run(
        debug=True
    )