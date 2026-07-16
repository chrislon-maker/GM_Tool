from PyPDF2 import PdfReader
from models.creature import Creature
from models.properties import Attribute, Resource, SoulPower, MovementSpeed, Toughness, Evasion, Initiative
from models.equipment import WeaponType
from services.checks import TalentDefinition
import re


'''
# metadata, author, creation date etc.
info = reader.metadata

# list of page objects
reader.pages

# text of page n
reader.pages[n].extract_text()
'''


def get_str(data: dict, key: str, default: str = "") -> str:
    value = data.get(key)
    if value is None or value == "-":
        return default
    return str(value).strip()


def get_int(data: dict, key: str, default: int = 0) -> int:
    value = data.get(key)

    if value is None:
        return default

    value = str(value).strip()

    if value in ("", "-", "–"):
        return default

    # entfernt z.B. "(8)" oder andere Nicht-Zahlen
    value = re.sub(r"[^\d-]", "", value)

    if value in ("", "-"):
        return default

    return int(value)


def load_character_from_pdf(pdf_path: str) -> Creature:

    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        if not reader.get_fields():
            return
        
        form_fields = reader.get_fields()
        data = {}
        for field_name, field_data in form_fields.items():
            data[field_name] = field_data.get('/V', None)
    
    creature = Creature()

    # characteristics
    creature.name = get_str(data, 'Held_Name')
    creature.family = get_str(data, 'Held_Familie')
    creature.home = get_str(data, 'Held_Geburtsort')
    creature.birthday = get_str(data, 'Held_Geburtsdatum')
    creature.species = get_str(data, 'Held_Spezies_Anzeige')

    creature.size = get_str(data, 'Held_Groesse')
    creature.size_category = SizeCategory.MEDIUM
    creature.hair_color = get_str(data, 'Held_Haare')
    creature.eye_color = get_str(data, 'Held_Augen')
    creature.culture = get_str(data, 'Held_Kultur_Anzeige')
    creature.profession = get_str(data, 'Held_Profession_Anzeige')

    creature.social_status = get_str(data, 'Held_Sozialstatus')
    creature.gender = get_str(data, 'Held_Geschlecht')

    # attributes
    creature.attributes[Attribute.MU] = get_int(data, "MU_1")
    creature.attributes[Attribute.KL] = get_int(data, "KL_1")
    creature.attributes[Attribute.IN] = get_int(data, "IN_1")
    creature.attributes[Attribute.CH] = get_int(data, "CH_1")
    creature.attributes[Attribute.FF] = get_int(data, "FF_1")
    creature.attributes[Attribute.GE] = get_int(data, "GE_1")
    creature.attributes[Attribute.KO] = get_int(data, "KO_1")
    creature.attributes[Attribute.KK] = get_int(data, "KK_1")

    # resources
    creature.LeP = Resource(get_int(data, 'LE_Wert_1'),  maximum=get_int(data, 'LE_Max_1'))
    creature.AsP = Resource(get_int(data, 'AE_Wert_1'),  maximum=get_int(data, 'AE_Max_1'), minimum=0)
    creature.KaP = Resource(get_int(data, 'KE_Wert_1'),  maximum=get_int(data, 'KE_Max_1'), minimum=0)
    creature.chips = Resource(get_int(data, 'SchiP_Aktuell_1'), maximum=get_int(data, 'SchiP_Max_1'), minimum=0)

    # derived values
    creature.SK = SoulPower(creature, get_int(data, 'SK_Max_1'))
    creature.ZK = Toughness(creature, get_int(data, 'ZK_Max_1'))
    #creature.AW = Evasion(creature, int( re.sub(r"\(\d+\)" , "", data['AW_Max_1']) ))
    creature.AW = Evasion(creature, get_int(data, 'AW_Max_1'))
    creature.INI = Initiative(creature, get_int(data, 'INI_Max_1'))
    creature.GS = MovementSpeed(creature, get_int(data, 'GS_Max_1'))


    # Talente
    for index, talent_name in enumerate(TalentDefinition.all().keys()):
        creature.talents[talent_name] = get_int(data, 'Talent_FW_{:}'.format(index+1))

    # weapon skills
    creature.weapon_skills[WeaponType.CROSSBOW] = get_int(data, "KT_FW_1")
    creature.weapon_skills[WeaponType.BOW] = get_int(data, "KT_FW_2")
    creature.weapon_skills[WeaponType.DAGGERS] = get_int(data, "KT_FW_3")
    creature.weapon_skills[WeaponType.FENCING] = get_int(data, "KT_FW_4")
    creature.weapon_skills[WeaponType.BLUNT] = get_int(data, "KT_FW_5")
    creature.weapon_skills[WeaponType.CHAIN] = get_int(data, "KT_FW_6")
    creature.weapon_skills[WeaponType.LANCE] = get_int(data, "KT_FW_7")
    creature.weapon_skills[WeaponType.BRAWL] = get_int(data, "KT_FW_8")
    creature.weapon_skills[WeaponType.SHIELD] = get_int(data, "KT_FW_9")
    creature.weapon_skills[WeaponType.SWORD] = get_int(data, "KT_FW_10")
    creature.weapon_skills[WeaponType.POLEARMS] = get_int(data, "KT_FW_11")
    creature.weapon_skills[WeaponType.THROW] = get_int(data, "KT_FW_12")
    creature.weapon_skills[WeaponType.BLUNT_2H] = get_int(data, "KT_FW_13")
    creature.weapon_skills[WeaponType.SWORD_2H] = get_int(data, "KT_FW_14")
    creature.weapon_skills[WeaponType.FIREBREATH] = get_int(data, "KT_FW_15")
    creature.weapon_skills[WeaponType.WHIP] = get_int(data, "KT_FW_16")
    creature.weapon_skills[WeaponType.SPIN] = get_int(data, "KT_FW_17")
    creature.weapon_skills[WeaponType.BLOWGUN] = get_int(data, "KT_FW_18")
    creature.weapon_skills[WeaponType.DISCUS] = get_int(data, "KT_FW_19")
    creature.weapon_skills[WeaponType.FAN] = get_int(data, "KT_FW_20")
    creature.weapon_skills[WeaponType.SKEWER] = get_int(data, "KT_FW_21")
    
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



       
