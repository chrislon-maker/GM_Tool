from flask import Flask, jsonify, render_template, request
from services.pdf_character_loader import load_character_from_pdf
from models.properties import TalentDefinition
from models.status_effect import Pain
from models.enums import TalentId

from services.talent_check_handler import TalentCheckHandler

from pathlib import Path
from uuid import uuid4
import random, os, threading, webbrowser


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


# create a compact JSON with relevant data for frontend
@app.get("/api/characters/<characterId>")
def get_character(characterId):
    creature = loaded_characters.get(characterId)

    if characterId not in loaded_characters.keys():
        return jsonify({
            "success": False,
            "error": "Charakter nicht gefunden."
        }), 404

    data = {}
    data["success"] = True
    data["character"] = {}

    data["character"]["advantages"] = creature.advantages
    data["character"]["disadvantages"] = creature.disadvantages
    data["character"]["Lep_current"] = creature.LeP.current
    data["character"]["Lep_maximum"] = creature.LeP.maximum
    data["character"]["Asp_current"] = creature.AsP.current
    data["character"]["Asp_maximum"] = creature.AsP.maximum
    data["character"]["Kap_current"] = creature.KaP.current
    data["character"]["Kap_maximum"] = creature.KaP.maximum
    data["character"]["GS_current"] = creature.GS.current
    data["character"]["ZK_current"] = creature.ZK.current
    data["character"]["SK_current"] = creature.SK.current
    data["character"]["INI_current"] = creature.INI.current
    data["character"]["pain_level"] = creature.status_level(Pain)
    data["character"]["id"] = characterId
    data["character"]["name"] = creature.name
    data["character"]["profession"] = creature.profession
    data["character"]["species"] = creature.species
    data["character"]["gender"] = creature.gender
    data["character"]["attributes"] = {attribute.value: value for attribute, value in creature.attributes.items()}

    return jsonify(data)


@app.post("/character/update_resource")
def update_character_resource():
    data = request.get_json()

    character = loaded_characters[data["character_id"]]
    resource = data["resource"]
    value = data["value"]

    if resource == "lep":
        current = character.LeP.current
        if value < current and value != current:
            character.get_damage(current-value)
        else:
            character.heal(value-current)
        painlevel = character.status_level(Pain)
        return jsonify({"pain_level": painlevel})
    elif resource == "asp":
        character.AsP.set_to(value)
        return jsonify({"success": True})
    elif resource == "kap":
        character.KaP.set_to(value)
        return jsonify({"success": True})
    return jsonify({"success": False})



@app.post("/api/characters")
def add_character():

    # get value of key "filename" form the json file
    data = request.get_json(silent=True)
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




@app.delete("/api/characters/<character_id>")
def delete_character(character_id):

    if character_id not in loaded_characters.keys():
        return jsonify({
            "success": False,
            "error": "Charakter nicht gefunden."
        }), 404

    del loaded_characters[character_id]

    return jsonify({
        "success": True
    })      



# get a list of talents form that category
@app.get("/api/talents")
def get_talent_list():
    category = request.args.get("category")
    talent_names = [
        talent.name.value  
        for talent in TalentDefinition._definitions.values()
        if talent.category.value == category
    ]

    return jsonify(talent_names)

# get info about a specific talent and relevant character info
@app.get("/api/characters/<character_id>/talents/<talent_name>/check-info")
def get_talent_check_info(character_id, talent_name):
    talent = TalentDefinition._definitions[TalentId(talent_name)]
    character = loaded_characters[character_id]
    manuel_mod = int(request.args.get("manuel_mod")) | 0 

    conditions = TalentCheckHandler.conditions(character, talent, manuel_mod)

    info = {}

    # get talent info
    info["talent"] = {}

    info["talent"]["attributes"] = [attribute[0].value for attribute in conditions.attributes]
    info["talent"]["category"] = talent.category.value
    info["talent"]["tags"] = [tag.value for tag in talent.tags]
    #print(talent.attributes)

    # get character info
    info["character"] = {}
    info["character"]["attributes"] = [attribute[1] for attribute in conditions.attributes]
    info["character"]["FW"] = conditions.target_value

    info["character"]["status_effects"] = {}

    for modifier in conditions.status_effect_mods:
        info["character"]["status_effects"][modifier.source_name] = {"level": modifier.level, "additive": modifier.modifier.additive, "multiplicative": modifier.modifier.multiplicative}
        
    info["character"]["external_modifier"] = conditions.external_mod
    info["character"]["final_modifier"] = conditions.final_mod.additive
    info["character"]["status_effect_mods"] = conditions.final_mod.additive - conditions.external_mod

    return jsonify(info)


# get info about a specific talent and relevant character info
@app.get("/api/characters/<character_id>/talents/<talent_name>/perform_check")
def perform_talent_check(character_id, talent_name):
    talent = TalentDefinition._definitions[TalentId(talent_name)]
    character = loaded_characters[character_id]
    manuel_mod = int(request.args.get("manuel_mod")) | 0 

    result = TalentCheckHandler.resolve(character, talent, manuel_mod)

    info = {}
    info["rolls"] = result.roll
    info["fp_left"] = result.remaining
    info["crit"] = result.crit
    info["success"] = result.success
    info["QS"] = result.quality_level
    info["diff"] = result.remaining - result.conditions.target_value
    info["final_mod"] = result.conditions.final_mod.additive
    info["attributes"] = [attribute[1] for attribute in result.conditions.attributes] 

    return jsonify(info)


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
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1, open_browser).start()
    # run flast server created above
    app.run(
        debug=True
    )