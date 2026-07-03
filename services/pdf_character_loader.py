from PyPDF2 import PdfReader
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

def load_character_from_pdf(path: str) -> Creature:
    creature = Creature(source="pdf")
    ...
    return creature


class Character(Kreatur):
    def __init__(self, pdf_path, **kwargs):
        super().__init__(**kwargs)
        self.pdf_path = pdf_path
        self.extract_form_values()

        self.disabled = False
        self.dying = False

        for k, v in kwargs.items():
            setattr(self, k, v)

    def extract_form_values(self):
        with open(self.pdf_path, 'rb') as file:
            reader = PdfReader(file)
            if not reader.get_fields():
                return
            
            form_fields = reader.get_fields()
            data = {}
            for field_name, field_data in form_fields.items():
                data[field_name] = field_data.get('/V', None)
        
        # characteristics
        self.name = data['Held_Name']
        self.family = data['Held_Familie']
        self.home = data['Held_Geburtsort']
        self.birthday = data['Held_Geburtsdatum']
        self.species = data['Held_Spezies_Anzeige']
        self.size = data['Held_Groesse']
        self.hair = data['Held_Haare']
        self.eyes = data['Held_Augen']
        self.culture = data['Held_Kultur_Anzeige']
        self.profession = data['Held_Profession_Anzeige']
        self.social_status = data['Held_Sozialstatus']
        self.gender = data['Held_Geschlecht']

        # attributes
        self.MU = int(data["MU_1"])
        self.KL = int(data["KL_1"])
        self.IN = int(data["IN_1"])
        self.CH = int(data["CH_1"])
        self.FF = int(data["FF_1"])
        self.GE = int(data["GE_1"])
        self.KO = int(data["KO_1"])
        self.KK = int(data["KK_1"])

        # status values
        self.LeP = int(data['LE_Wert_1'])
        self.maxLeP = int(data['LE_Max_1'])
        self.AsP = int(data['AE_Wert_1'])
        self.maxAsP = int(data['AE_Max_1'])
        #self.KaP = int(data['KE_Wert_1'])
        #self.maxKaP = int(data['KE_Max_1'])
        self.SK = int(data['SK_Max_1'])
        self.ZK = int(data['ZK_Max_1'])
        self.AW = int( re.sub(r"\(\d+\)" , "", data['AW_Max_1']) )
        self.base_INI = int(data['INI_Max_1'])
        self.INI_bonus = '1W6'
        self.schip = int(data['SchiP_Aktuell_1'])
        self.maxschip = int(data['SchiP_Max_1'])
        self.GS = int(data['GS_Max_1'])
        self.statuus = {}

        # Talente
        self.talents = {}
        for index, talent in enumerate(talents.keys()):
            self.talents[talent] = int(data['Talent_FW_{:}'.format(index+1)])
        
        # Inventory
        self.inventory = []
        for field, value in data.items():
            if "Besitz_Name_Anzeige_" in field and value is not None:
                self.inventory.append(value)

        # magic abilities
        self.magic_special_abilities = data["Held_SF_Mag"]
        self.magic_tricks = data["Held_Tricks"]
        self.spells = []
        for i in range(30):
            try:
                if data["Zauber_{:}".format(i)] is not None: 
                    self.spells.append(data["Zauber_{:}".format(i)])
            except:
                continue

        # profane abilities
        self.combat_special_abilities = []
        for i in range(30):
            try:
                if data["SF_Kampf_{:}".format(i)] is not None: 
                    self.combat_special_abilities.append(data["SF_Kampf_{:}".format(i)][:-5])
            except:
                continue

        self.general_special_abilities = []
        for i in range(30):
            try:
                if data["SF_allg_{:}".format(i)] is not None: 
                    try:
                        self.general_special_abilities.append(re.sub(r"\[\d+\]", "", data["SF_allg_Er_{:}".format(i)]))
                    except:
                        self.general_special_abilities.append(re.sub(r"\[\d+\]", "", data["SF_allg_{:}".format(i)]))
            except:
                continue

        self.advantages = re.split(r"\s*/\s*", data["Held_Vorteile"])
        self.disadvantages = re.split(r"\s*/\s*", data["Held_Nachteile"])
        self.money = [data["Geld_D"], data["Geld_S"], data["Geld_H"], data["Geld_K"]]
