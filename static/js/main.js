
// CHARACTER SELECTION

// character list
const characterList = document.getElementById("characterList")

characterList.addEventListener("click", async (event) => {

    // CASE 1 : delete character

    const deleteButton = event.target.closest(".delete-character")

    // abbort if no button was clicked
    if (deleteButton && characterList.contains(deleteButton)) {
        // get parent row
        const row = deleteButton.parentElement;

        // get corresponding character button
        const characterButton = row.querySelector(".character-button");
        // get character ID
        const characterID = characterButton.dataset.characterId;

        if (await deleteCharacter(characterID)) {
            console.log("Charakter löschen:", characterID);
            // delete character button
            row.remove();
        } 

        return;
    } 

    // CASE 2 : select character
    const clickedButton = event.target.closest(".character-button")

    // abbort if no button was clicked
    if (!clickedButton || !characterList.contains(clickedButton)) {
        return;
    } 

    // Select the clicked character
    clickedButton.classList.add("selected");
    clickedButton.setAttribute("aria-pressed", "true");

    // unselect all other characters
    characterList.querySelectorAll(".character-button").forEach(b => {
        if (b != clickedButton) {
            b.classList.remove("selected");
            b.setAttribute("aria-pressed", "false");
        }
    });


    // get character ID
    const char_id = clickedButton.dataset.characterId;

    console.log("Ausgewählt:", char_id);

    // functio in character_tableau.js
    updateCharacterSheet(char_id)
});


// CHARACTER IMPORT

// modal for character import
const addCharacterModal = document.getElementById("addCharacterModal");

// Import selection method window
const ImportMethodSelection = document.getElementById("characterImportMethodSelection");

// Import form PDF window
const CharacterPdfSelection = document.getElementById("characterPDFSelection");
//const ManuelCharacterForm = document.getElementById("manuelCharacterForm");
//const CharacterLinkInput = document.getElementById("characterLinkInput");

// get buttons
const AddFromPDFButton = document.getElementById("addFromPdf");
const BackToImportMethodsButton = document.getElementById("backToImportMethods");
const ImportCharacterFromPDFButton = document.getElementById("importCharacterFromPDF");
const characterPDFDropdown = document.getElementById("characterPDF");
const characterPDFUpload = document.getElementById("characterPDFUpload"); 

// load "import from PDF" - page
AddFromPDFButton.addEventListener("click", async () => {
    ImportMethodSelection.classList.add("d-none");
    CharacterPdfSelection.classList.remove("d-none");

    pdfFiles = await loadAvailablePDFs();

    // replace the content of the drop down menue by this HTML
    characterPDFDropdown.innerHTML = '<option value="">Bitte auswählen...</option>';

    // create <option> objects and add them to the drop down
    pdfFiles.forEach(filename => {
        const option = document.createElement("option");

        option.value = filename;
        option.textContent = filename;

        characterPDFDropdown.appendChild(option);
    });
});

// go back to method selection page
BackToImportMethodsButton.addEventListener("click", () => {
    CharacterPdfSelection.classList.add("d-none");
    ImportMethodSelection.classList.remove("d-none");
});

// go back when closing modal
addCharacterModal.addEventListener("hidden.bs.modal", () => {
    CharacterPdfSelection.classList.add("d-none");
    ImportMethodSelection.classList.remove("d-none");
});

// fill PDF drop-down menue
async function loadAvailablePDFs() {
    // calls the function get_character_pdfs() denoted by @app.get("/api/characters/pdfs") in app.py
    const response = await fetch("/api/characters/pdfs");

    // get file names form json
    const pdfFiles = await response.json();

    return pdfFiles;
}

// reset PDF dropwodn when PDF is searched for by path
characterPDFUpload.addEventListener("change", () => {
    if (characterPDFUpload.files.length > 0) {
        characterPDFDropdown.value = "";
    }
});

// reset PDF dropwodn when PDF is searched for by path
characterPDFDropdown.addEventListener("change", () => {
    if (characterPDFDropdown.value != "") {
        characterPDFUpload.value = "";
    }
});

// send loading request for character PDF
ImportCharacterFromPDFButton.addEventListener("click", () => {
    // get file name form drop down
    const filename = characterPDFDropdown.value

    // check if it is empty
    if (filename === "") {
        alert("Bitte wähle zuerst eine PDF aus.");
        return;
    }

    addCharacter(filename);

    // Modal schließen
    const modalElement = document.getElementById("addCharacterModal");
    const modal = bootstrap.Modal.getInstance(modalElement);

    modal.hide();
});

// adds a character to the character list
async function addCharacter(filename) {

    // call add_character() function and send data
    try {
        const response = await fetch("/api/characters", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                filename: filename
            })
        });

        // read output
        const result = await response.json()

        if (!response.ok || !result.success) {
            alert(result.error || "Der Charakter konnte nicht geladen werden.");
            return;
        }

        // create alignment element
        const row = document.createElement("div")
        row.className = "d-flex align-items-stretch"

        // create character button
        const ch_button = document.createElement("button");
        ch_button.type = "button";
        ch_button.className = "btn btn-sm character-button flex-grow-1";
        ch_button.dataset.characterId = result.character.id;
        ch_button.setAttribute("aria-pressed", "false");

        // create arrow icon
        const arrow_icon = document.createElement("i");
        arrow_icon.className = "bi bi-play character-arrow";

        // add icon and character name to the button
        ch_button.appendChild(arrow_icon);
        ch_button.appendChild(document.createTextNode(result.character.name));

        // delete button
        const del_icon = document.createElement("i");
        del_icon.className = "bi bi-x-lg";

        const del_button = document.createElement("button");
        del_button.type = "button";
        del_button.className = "btn btn-sm btn-outline-danger border-0 delete-character";
        del_button.setAttribute("aria-label", "Charakter löschen");
        del_button.appendChild(del_icon);

        row.appendChild(ch_button);
        row.appendChild(del_button);

        // CONTINUE HERE ADD DELETE FUNCTION TO DELETE BUTTON

        characterList.appendChild(row) ;

        // add message to console log
        console.log("Charakter geladen:", result.character.name);

    } catch (error) {
        console.error("Fehler beim Import:", error);
        alert("Die Verbindung zum Server ist fehlgeschlagen.");
    }
    
};


// delece a character form the character list
async function deleteCharacter(char_id) {

    // call delete_character() function and send data
    try {
        const response = await fetch(`/api/characters/${char_id}`, {
            method: "DELETE"
        });


        // read output
        const result = await response.json();

        if (!response.ok || !result.success) {
            alert(result.error || "Beim Löschen des Characters ist ein Fehler aufgetreten.");
            return false;
        }

        // add message to console log
        console.log("Charakter gelöscht, ID:", char_id);

        return true;

    } catch (error) {
        console.error("Fehler beim Löschen:", error);
        alert("Die Verbindung zum Server ist fehlgeschlagen.");
        return false;
    }
};
