// getElementById() : get element with given ID
// querySelector() : get element with a class attribute e.g. character-button
// setAttribute(A, B): sets an atribute A to B e.g. "id" to "health_points"


/// SECTIONS ///
// overall sheet
const characterSheet = document.getElementById("characterSheet")
// fluff information sub area
const characterFluff = document.getElementById("characterFluff");

/// BUTTONS ///
const FluffDropdownButton = document.getElementById("fluffDropDownButton");


/// FRONTEND FUNCTIONALITY ///

// flip fluff dropdown button symbol
characterFluff.addEventListener("shown.bs.collapse", () => {
    FluffDropdownButton.innerHTML = '<i class="bi bi-caret-up-fill"></i>';
});

characterFluff.addEventListener("hidden.bs.collapse", () => {
    FluffDropdownButton.innerHTML = '<i class="bi bi-caret-down-fill"></i>';
});


/// BACKEND COMUNICATION ///
async function updateCharacterSheet(characterId) {
    // load character data
    const response = await fetch(`/api/characters/${characterId}`);
    const result = await response.jason();
    
    if (!response.ok || !result.success) {
        console.error("Charakter konnte nicht geladen werden.");
        return;
    }

    document.getElementById("characterName").textContent = result.character.name;
}



