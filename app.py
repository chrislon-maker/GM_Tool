from flask import Flask, jsonify, render_template, request
import threading
import webbrowser



app = Flask(__name__)


@app.route("/")
def index():
    """Display the main frontend page."""
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def process():
    """
    Receive data from the frontend and return a result.

    Replace the example processing with your existing backend function.
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "No JSON data was received."
        }), 400

    user_text = str(data.get("text", "")).strip()

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


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(
        debug=True
    )