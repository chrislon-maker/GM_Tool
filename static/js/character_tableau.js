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

const LeP_bar = document.getElementById("lepBar");
const AsP_bar = document.getElementById("aspBar");
const KaP_bar = document.getElementById("kapBar");

// update bar filling and text
function updateResourceSlider(slider) {
    const current = Number(slider.value);
    const max = Number(slider.max);

    const percent = max > 0
        ? current / max * 100
        : 0;

    slider.style.setProperty("--slider-percent", `${percent}%`);

    document.getElementById(slider.dataset.label).textContent = `${current} / ${max}`;
}


// bars event trigger
document.querySelectorAll(".resource-slider").forEach(slider =>{
    // update UI
    slider.addEventListener("input", () => {
        updateResourceSlider(slider);
    });

    // communicate with backend
    slider.addEventListener("change", async () => {
        const value = Number(slider.value);
        const resource = slider.dataset.resource;
        const character_id = document.getElementById("characterSheet").dataset.characterId;

        const result = await updateResourceBackend(character_id, resource, value);

        if (resource == "lep") {
            // update pain
            document.getElementById("pain_level").textContent = `${result.pain_level}`;
            //updatePainLevel();
        };
    });

    // update again
    updateResourceSlider(slider);

});

// change a resource in the backend
async function updateResourceBackend(character_id, resource, value) {
    const response = await fetch("/character/update_resource", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            character_id: character_id,
            resource: resource,
            value: value
        })
    });

    if (!response.ok) {
        throw new Error(`Fehler beim Aktualisieren von ${resource}`);
    }

    return await response.json();
}

// UPDATE CHARACTER INFO
async function updateCharacterSheet(characterId) {
    // load character data
    const response = await fetch(`/api/characters/${characterId}`);
    const result = await response.json();
    
    if (!response.ok || !result.success) {
        console.error("Charakter konnte nicht geladen werden.");
        return;
    }

    const character = result.character

    document.getElementById("characterSheet").dataset.characterId = characterId;

    // hidde initial character sheet and show the real one
    document.getElementById("noCharacterSelected").classList.add("d-none");
    document.getElementById("characterSheet").classList.remove("d-none");
    document.getElementById("characterSheet").classList.add("d-flex");

    /// FILL INFORMATION
    // name
    document.getElementById("characterName").innerHTML = character.name;

    // short info
    let short_info = ''
    // species
    if (character.species != "") {
        short_info += character.species
    }
    // gender
    if (character.gender == "m") {
        short_info += ' <i class="bi bi-gender-male"></i>'
    }  
    if (character.gender == "w") {
        short_info += ' <i class="bi bi-gender-female"></i>'
    }
    // profession
    if (character.profession != "") {
        short_info += ' · ' + character.profession
    }

    document.getElementById("characterShortInfo").innerHTML = short_info;

    // Eigenschaften
    document.getElementById("MU_value").innerHTML = character.attributes.MU;
    document.getElementById("KL_value").innerHTML = character.attributes.KL;
    document.getElementById("IN_value").innerHTML = character.attributes.IN;
    document.getElementById("CH_value").innerHTML = character.attributes.CH;
    document.getElementById("FF_value").innerHTML = character.attributes.FF;
    document.getElementById("GE_value").innerHTML = character.attributes.GE;
    document.getElementById("KO_value").innerHTML = character.attributes.KO;
    document.getElementById("KK_value").innerHTML = character.attributes.KK;

    document.getElementById("GS_value").innerHTML = character.GS_current;
    document.getElementById("INI_value").innerHTML = character.INI_current;
    document.getElementById("SK_value").innerHTML = character.SK_current;
    document.getElementById("ZK_value").innerHTML = character.ZK_current;

    // Bars
    document.getElementById("lepText").innerHTML = character.Lep_current + " / " + character.Lep_maximum;
    LeP_bar.max = `${character.Lep_maximum}`;
    LeP_bar.value= `${character.Lep_current}`;
    document.getElementById("lep_incapacitated").style.setProperty("left", `${100*5/character.Lep_maximum}%`);
    //LeP_bar.style.setProperty("--slider-percent", `${100*character.Lep_current/character.Lep_maximum}%`);
    updateResourceSlider(LeP_bar);
    // update pain
    /*
    if (character.Asp_maximum == 0) {
        document.getElementById("aspText").innerHTML = "-"
        document.getElementById("aspBar").setAttribute("style", "width: 0%;");
    } else {
        document.getElementById("aspText").innerHTML = character.Asp_current + " / " + character.Asp_maximum;
        document.getElementById("aspBar").setAttribute("style", 
            `width: ${100*character.Asp_current/character.Asp_maximum}%;
            background-color: color-mix(in srgb, var(--my-teal) 75%, transparent);`);
    }   
    */
    AsP_bar.max = `${character.Asp_maximum}`;
    AsP_bar.value= `${character.Asp_current}`;
    updateResourceSlider(AsP_bar);

    KaP_bar.max = `${character.Kap_maximum}`;
    KaP_bar.value= `${character.Kap_current}`;
    updateResourceSlider(KaP_bar);
    /*
    if (character.Kap_maximum == 0) {
        document.getElementById("kapText").innerHTML = "-"
        document.getElementById("kapBar").setAttribute("style", "width: 0%;");
    } else {
        document.getElementById("kapText").innerHTML = character.Kap_current + " / " + character.Kap_maximum;
        document.getElementById("kapBar").setAttribute("style", 
            `width: ${100*character.Kap_current/character.Kap_maximum}%;
            background-color: color-mix(in srgb, var(--my-teal) 75%, transparent);`);
    }
    */
    document.getElementById("pain_level").textContent = `${character.pain_level}`;

    // (Dis-)Advantages
    const advantages = document.getElementById("advantage_list");
    advantages.querySelectorAll(".advantage-item").forEach(item => item.remove());
    for (const advantage of character.advantages) { // for ... in... gives indicees instead of items
        const item = document.createElement("div");
        item.classList.add(
            "advantage-item", 
            "rounded", 
            "px-1", 
            "text-nowrap", 
            "flex-grow-1", 
            "text-center",
            "d-flex",
            "align-items-center",
            "justify-content-center"
        );
        item.innerHTML = advantage;
        advantages.appendChild(item);
    }

    const disadvantages = document.getElementById("disadvantage_list");
    disadvantages.querySelectorAll(".disadvantage-item").forEach(item => item.remove());
    // add items
    for (const disadvantage of character.disadvantages) {
        const item = document.createElement("div");
        item.classList.add(
            "disadvantage-item", 
            "rounded", 
            "px-1", 
            "text-nowrap", 
            "flex-grow-1", 
            "text-center",
            "d-flex",
            "align-items-center",
            "justify-content-center"
        );
        item.textContent = disadvantage;
        disadvantages.appendChild(item);
    }

}


/// TALENT CHECK
// get modal
const TalentCheckModal = document.getElementById("TalentCheckModal");
//
const TalentCategorySelection = document.getElementById("TalentCategorySelection");
// get category buttons
const physical_talents_btn = document.getElementById("physical_talents_btn");
const social_talents_btn = document.getElementById("social_talents_btn");
const nature_talents_btn = document.getElementById("nature_talents_btn");
const knowledge_talents_btn = document.getElementById("knowledge_talents_btn");
const crafting_talents_btn = document.getElementById("crafting_talents_btn");

physical_talents_btn.addEventListener("click", () =>{
    GetTalentList("Körpertalent");
});

social_talents_btn.addEventListener("click", () =>{
    GetTalentList("Gesellschaftstalent");
});

nature_talents_btn.addEventListener("click", () =>{
    GetTalentList("Naturtalent");
});

knowledge_talents_btn.addEventListener("click", () =>{
    GetTalentList("Wissenstalent");
});

crafting_talents_btn.addEventListener("click", () =>{
    GetTalentList("Handwerkstalent");
});


// get talent lists
const talent_selection = document.getElementById("talent_selection");
const talent_list = document.getElementById("talent_list");
const talent_check = document.getElementById("talent_check");

const modifierInput = document.getElementById("modifierInput") 

let baseModifier = [0, 0, 0];

// UPDATE ROLL MODIFIER
async function UpdateTalentCheckInfo() {
    const checked_talent = document.getElementById("checked_talent").textContent;
    const character_id = document.getElementById("characterSheet").dataset.characterId;
    const manuelModifier = Number(modifierInput.value) || 0;

    // get check infos
    const info = await GetTalentInfos(character_id, checked_talent, manuelModifier);

    console.log("loaded Talent infos");

    // extract net modifier and set color
    const netto_mod = -info.character.final_modifier;
    const color = netto_mod > 0 ? "var(--my-red)" : "var(--my-green)";

    document.getElementById("status_effect_modifier").textContent = info.character.status_effect_mods;
    document.getElementById("number_of_status_effects").textContent = `(${Object.keys(info.character.status_effects).length})`;

    console.log("lets collect status effects");
    
    const status_effect_info_column = document.getElementById("status_effect_info_column");
    status_effect_info_column.replaceChildren();
    const status_effect_modifier_column = document.getElementById("status_effect_modifier_column");
    status_effect_modifier_column.replaceChildren();
    //const status_effect_modifier_list = document.getElementById("status_effect_modifier_list");
    for (const [key, value] of Object.entries(info.character.status_effects)) {

        const effect_info_icon = document.createElement("span");
        effect_info_icon.title = key;
        effect_info_icon.ariaLabel = key;
        effect_info_icon.style.setProperty("width", "24px");
        effect_info_icon.style.setProperty("height", "24px");
        if (key == "Schmerz") {
            effect_info_icon.classList = "custom-icon icon-pain my-red" 
        }

        if (key == "Paralyse") {
            effect_info_icon.classList = "custom-icon icon-snow my-teal" 
        }
        
        if (key == "Verwirrung") {
            effect_info_icon.classList = "custom-icon icon-stars my-yellow" 
        }
 
        status_effect_info_column.appendChild(effect_info_icon);

        const effect_info_text = document.createElement("span");
        effect_info_text.classList = "text-body-secondary my-1 ms-1 fs-7";
        effect_info_text.textContent = `${key} ${value.level}`;
        status_effect_info_column.appendChild(effect_info_text);

        const effect_info_modifier = document.createElement("span");
        effect_info_modifier.classList = "my-text my-red my-1 fs-7";
        effect_info_modifier.textContent = value.additive;

        status_effect_modifier_column.appendChild(effect_info_modifier);
    }

    console.log("lets update attributes");

    // create roll window
    for (let i=0; i<3; i++ ) {
        // set attribute icon
        const icon = document.getElementById(`icon_attribute${i+1}`);
        icon.classList = `custom-icon icon-${info.talent.attributes[i]} color-${info.talent.attributes[i]}`.toLocaleLowerCase();
        // set attribute name
        document.getElementById(`attribute${i+1}_name`).textContent = info.talent.attributes[i];
        // set attribute value
        const attribute_value = document.getElementById(`attribute${i+1}_value`);
        //attribute_value.classList = `my-text fs-2 fw-bold color-${info.talent.attributes[i]}`.toLocaleLowerCase();
        attribute_value.classList = "my-text fs-2 fw-bold";
        attribute_value.textContent = info.character.attributes[i];

        // set roll modifier
        const modifierDisplay = document.getElementById(`mod${i+1}`);
        modifierDisplay.textContent = netto_mod > 0 ? `+${netto_mod}` : `${netto_mod}`;
        modifierDisplay.style.setProperty("color", `${color}`);
        
    }

    document.getElementById("talent_FW").textContent = info.character.FW;

};

modifierInput.addEventListener("input", UpdateTalentCheckInfo)


// PICK A TALENT TO PROBE
talent_list.addEventListener("click", async (event) => {
    const chosen_talent = event.target.closest(".talent_name")

    // abbort if no button was clicked
    if (!chosen_talent || !talent_list.contains(chosen_talent)) {
        return;
    } 

    talent_selection.classList.add("d-none");
    talent_check.classList.remove("d-none");

    const checked_talent = document.getElementById("checked_talent");
    checked_talent.textContent = chosen_talent.textContent;

    UpdateTalentCheckInfo();

    return;
});


// GET TALENT INFO AND MODIFICATIONS
async function GetTalentInfos(character_id, talent_name, manuel_modification) {
    // load character data
    const response = await fetch(`/api/characters/${character_id}/talents/${encodeURIComponent(talent_name)}/check-info?manuel_mod=${encodeURIComponent(manuel_modification)}`);
    
    const result = await response.json();

    if (!response.ok) {
        console.error("Talente konnten nicht geladen werden:", response.status);
        return;
    }
    return result;
};

// roll button action
const roll_talent_btn = document.getElementById("roll_talent_btn");
roll_talent_btn.addEventListener("click", async () => {
    const character_id = document.getElementById("characterSheet").dataset.characterId;
    const talent_name = document.getElementById("checked_talent").textContent;

    const manuelModifier = Number(modifierInput.value) || 0;

    const result = await TalentCheck(character_id, talent_name, manuelModifier);

    for (let i=0; i<3; i++) {
        // roll
        const number = document.getElementById(`attribute${i+1}_roll`);
        number.textContent = result.rolls[i];
        number.classList.remove("d-none");
        //const attribute_value = Number(document.getElementById(`attribute${i+1}_value`).textContent);

        // check if roll + mod < attribut
        const failed = result.rolls[i] - result.final_mod > result.attributes[i];
        const color = failed ? "var(--my-red)" : "var(--my-green)";
        const background = document.getElementById(`roll${i+1}_background`);

        background.style.setProperty(
            "background-color",
            `color-mix(in srgb, ${color} 30%, var(--bs-tertiary-bg))`
        );
        number.style.setProperty("color", `${color}`);
    };  

    document.getElementById("talent_check_result_section").classList.remove("d-none");

    const roll_diff = document.getElementById("roll_diff");
    const reduce = result.diff < 0;
    const color = reduce ? "var(--my-red)" : "var(--my-green)";
    roll_diff.textContent = result.diff;
    roll_diff.style.setProperty("color", `${color}`);
    roll_diff.classList.remove("d-none");

    const failed = result.fp_left < 0;
    const result_color = failed ? "var(--my-red)" : "var(--my-green)";
    document.getElementById("fp_left").textContent = `${result.fp_left}`;
    document.getElementById("fp_left").style.setProperty("color", `${result_color}`);
    document.getElementById("QS_reached").textContent = failed ? "Probe nicht bestanden!" : `${result.QS}`;
    document.getElementById("QS_reached").style.setProperty("color", `${result_color}`);
    document.getElementById("QS_reached").style.setProperty("font-size", failed ? "16px" : "64px");
    document.getElementById("QS_reached").style.setProperty("bottom", failed ? "40%" : "25%");

    const result_icon = document.getElementById("roll_result_icon");
    const icon_spec = failed ? "icon-alert" : "icon-medal";
    result_icon.classList = `custom-icon ${icon_spec}`;
    result_icon.style.setProperty("background-color", `color-mix(in srgb, ${result_color} 20%,var(--bs-tertiary-bg))`);
});

// reset talent check window
function resetTalentCheck() {
    document.getElementById("roll_diff").classList.add("d-none");
    document.getElementById("talent_check_result_section").classList.add("d-none");
    for (let i=0; i<3; i++) {
        document.getElementById(`attribute${i+1}_roll`).classList.add("d-none");
    }
}

// PERFOM TALENT CHECK
async function TalentCheck(character_id, talent_name, manuel_modification) {
    // load character data
    const response = await fetch(`/api/characters/${encodeURIComponent(character_id)}/talents/${encodeURIComponent(talent_name)}/perform_check?manuel_mod=${encodeURIComponent(manuel_modification)}`);

    const result = await response.json();

    if (!response.ok) {
        console.error("Talente konnten nicht geprobt werden:", response.status);
        return;
    }

    return result;

}


// resetn Talent check modal when closing
TalentCheckModal.addEventListener("hidden.bs.modal", () => {
    TalentCategorySelection.classList.remove("d-none");
    talent_selection.classList.add("d-none");
    talent_check.classList.add("d-none");
    resetTalentCheck();
});

// go back to talent category selection
const backToTalentCategorySelection = document.getElementById("backToTalentCategorySelection");
backToTalentCategorySelection.addEventListener("click", () => {
    TalentCategorySelection.classList.remove("d-none");
    talent_selection.classList.add("d-none");
    talent_check.classList.add("d-none");
});

// go back to talent selection
const backToTalentSelection = document.getElementById("backToTalentSelection");
backToTalentSelection.addEventListener("click", () => {
    talent_selection.classList.remove("d-none");
    talent_check.classList.add("d-none");
    resetTalentCheck();
});


// GET TALENT LIST
async function GetTalentList(talent_category) {
    // load character data
    const response = await fetch(`/api/talents?category=${encodeURIComponent(talent_category)}`);
    const talent_names = await response.json();

    
    if (!response.ok) {
        console.error("Talente konnten nicht geladen werden:", response.status);
        return;
    }

    const chosen_talent_category = document.getElementById("chosen_talent_category");
    chosen_talent_category.textContent = talent_category+"e";

    TalentCategorySelection.classList.add("d-none");
    talent_selection.classList.remove("d-none");

    talent_list.querySelectorAll(".talent_name").forEach(item => item.remove());

    // add items
    talent_names.forEach(talent => {
        const button = document.createElement("button");
        button.classList.add(
            "btn",
            "btn-sm",
            "px-1", 
            "flex-grow-1", 
            "text-center",
            "d-flex",
            //"justify-content-center",
            "talent_name" 
        );
        button.style.setProperty("--bs-btn-bg","color-mix(in srgb,var(--my-teal) 10%,var(--bs-tertiary-bg))")
        button.style.setProperty("--bs-btn-color", "var(--my-teal)");
        button.style.setProperty("--bs-btn-border-color", "var(--my-teal)");
        button.style.setProperty("--bs-btn-hover-bg", "color-mix(in srgb,var(--my-teal) 20%,var(--bs-tertiary-bg))");
        button.style.setProperty("--bs-btn-hover-color", "white");
        button.style.setProperty("--bs-btn-hover-border-color", "var(--my-teal)");

        button.id = talent;
        button.textContent = talent;
        talent_list.appendChild(button);
    })

    return;

}

    


