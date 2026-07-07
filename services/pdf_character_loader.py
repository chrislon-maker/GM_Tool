from PyPDF2 import PdfReader
from models.creature import CreatureBase, Creature
from models.resource import Attribute, Resource, SoulPower, MovementSpeed, Toughness, Evasion, Initiative
from urllib.request import urlopen
from tqdm import tqdm
import re, json, os


'''
# metadata, author, creation date etc.
info = reader.metadata

# list of page objects
reader.pages

# text of page n
reader.pages[n].extract_text()
'''

def load_character_from_pdf(pdf_path: str) -> Creature:
    creature = Creature()

    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        if not reader.get_fields():
            return
        
        form_fields = reader.get_fields()
        data = {}
        for field_name, field_data in form_fields.items():
            data[field_name] = field_data.get('/V', None)

    '''

        source: str | None = None
        source_url: str | None = None

        talents: dict[str, int] = field(default_factory=dict)

        LeP: Resource
        KaP: Resource
        AsP: Resource
        chips: Resource

        GS: DerivedValue
        INI: DerivedValue
        SK: DerivedValue
        ZK: DerivedValue
        AW: DerivedValue

        status_effects = []

        weapons: list[Weapon] = field(default_factory=list)
        armor: list[dict] = field(default_factory=list)

        advantages: list[str] = field(default_factory=list)
        disadvantages: list[str] = field(default_factory=list)
        special_abilities: list[str] = field(default_factory=list)

        spells: dict[str, int] = field(default_factory=dict)
        liturgies: dict[str, int] = field(default_factory=dict)

        notes: str = ""

        disabled: bool = False
        dying: bool = False'''
    
    # characteristics
    creature.name = data['Held_Name']
    creature.family = data['Held_Familie']
    creature.home = data['Held_Geburtsort']
    creature.birthday = data['Held_Geburtsdatum']
    creature.species = data['Held_Spezies_Anzeige']

    creature.size = data['Held_Groesse']
    creature.hair_color = data['Held_Haare']
    creature.eye_color = data['Held_Augen']
    creature.culture = data['Held_Kultur_Anzeige']
    creature.profession = data['Held_Profession_Anzeige']

    creature.social_status = data['Held_Sozialstatus']
    creature.gender = data['Held_Geschlecht']

    # attributes
    creature.attributes[Attribute.MU] = int(data["MU_1"])
    creature.attributes[Attribute.KL] = int(data["KL_1"])
    creature.attributes[Attribute.IN] = int(data["IN_1"])
    creature.attributes[Attribute.CH] = int(data["CH_1"])
    creature.attributes[Attribute.FF] = int(data["FF_1"])
    creature.attributes[Attribute.GE] = int(data["GE_1"])
    creature.attributes[Attribute.KO] = int(data["KO_1"])
    creature.attributes[Attribute.KK] = int(data["KK_1"])

    # resources
    creature.LeP = Resource(int(data['LE_Wert_1']),  maximum=int(data['LE_Max_1']))
    creature.AsP = Resource(int(data['AE_Wert_1']),  maximum=int(data['AE_Max_1']), minimum=0)
    creature.KaP = Resource(int(data['KE_Wert_1']),  maximum=int(data['KE_Max_1']), minimum=0)
    creature.chips = Resource(int(data['SchiP_Aktuell_1']), maximum=int(data['SchiP_Max_1']), minimum=0)

    # derived values
    creature.SK = SoulPower(creature, int(data['SK_Max_1']))
    creature.ZK = Toughness(creature, int(data['ZK_Max_1']))
    creature.AW = Evasion(creature, int( re.sub(r"\(\d+\)" , "", data['AW_Max_1']) ))
    creature.INI = Initiative(creature, int(data['INI_Max_1']))
    creature.GS = MovementSpeed(creature, data['GS_Max_1'])


    # Talente
    for index, talent in enumerate(TalentDefinition._definitions.keys()):
        creature.talents[talent] = int(data['Talent_FW_{:}'.format(index+1)])
    
    # Inventory
    creature.inventory = []
    for field, value in data.items():
        if "Besitz_Name_Anzeige_" in field and value is not None:
            creature.inventory.append(value)

    # magic abilities
    creature.magic_special_abilities = data["Held_SF_Mag"]
    creature.magic_tricks = data["Held_Tricks"]
    creature.spells = []
    for i in range(30):
        try:
            if data["Zauber_{:}".format(i)] is not None: 
                creature.spells.append(data["Zauber_{:}".format(i)])
        except:
            continue

    # profane abilities
    creature.combat_special_abilities = []
    for i in range(30):
        try:
            if data["SF_Kampf_{:}".format(i)] is not None: 
                creature.combat_special_abilities.append(data["SF_Kampf_{:}".format(i)][:-5])
        except:
            continue

    creature.general_special_abilities = []
    for i in range(30):
        try:
            if data["SF_allg_{:}".format(i)] is not None: 
                try:
                    creature.general_special_abilities.append(re.sub(r"\[\d+\]", "", data["SF_allg_Er_{:}".format(i)]))
                except:
                    creature.general_special_abilities.append(re.sub(r"\[\d+\]", "", data["SF_allg_{:}".format(i)]))
        except:
            continue

    creature.advantages = re.split(r"\s*/\s*", data["Held_Vorteile"])
    creature.disadvantages = re.split(r"\s*/\s*", data["Held_Nachteile"])
    creature.money = [data["Geld_D"], data["Geld_S"], data["Geld_H"], data["Geld_K"]]
    
    return creature



       
