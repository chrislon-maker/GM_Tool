from PyPDF2 import PdfReader
from urllib.request import urlopen
from IPython import embed, get_ipython
import numpy as np
import random, re, inspect, json, os

pdf_path = "Klatu3.pdf"

'''
# metadata, author, creation date etc.
info = reader.metadata

# list of page objects
reader.pages

# text of page n
reader.pages[n].extract_text()
'''


class bcolors:
    HEADER = '\033[95m'
    blue = '\033[94m'
    cyan = '\033[96m'
    orange = '\033[93m'
    purple = '\033[95m'
    yellow = '\033[93m'
    red = '\033[91m'
    dark_red = '\033[31m'
    grey = '\033[90m'
    grey2 = '\033[38;5;240m'
    gold = '\033[38;5;220m'
    silver = '\033[38;5;7m'
    bronze = '\033[38;5;94m'
    green = '\033[92m'
    reset = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

talents = {'Fliegen': ['MU', 'IN', 'GE'], 
            'Gaukeleien': ['MU', 'CH', 'FF'], 
            'Klettern': ['MU', 'GE', 'KK'], 
            'Körperbeherrschung': ['GE', 'GE', 'KO'], 
            'Kraftakt': ['KO', 'KK', 'KK'], 
            'Reiten': ['CH', 'GE', 'KK'], 
            'Schwimmen': ['GE', 'KO', 'KK'], 
            'Selbstbeherrschung': ['MU', 'MU', 'KO'], 
            'Singen': ['KL', 'CH', 'KO'], 
            'Sinnesschärfe': ['KL', 'IN', 'IN'], 
            'Tanzen': ['KL', 'CH', 'GE'], 
            'Taschendiebstahl': ['MU', 'FF', 'GE'], 
            'Verbergen': ['MU', 'IN', 'GE'], 
            'Zechen': ['KL', 'KO', 'KK'], 
            'Bekehren & Überzeugen': ['MU', 'KL', 'CH'], 
            'Betören': ['MU', 'CH', 'CH'], 
            'Einschüchtern': ['MU', 'IN', 'CH'], 
            'Etikette': ['KL', 'IN', 'CH'], 
            'Gassenwissen': ['KL', 'IN', 'CH'], 
            'Menschenkenntnis': ['KL', 'IN', 'CH'], 
            'Überreden': ['MU', 'IN', 'CH'], 
            'Verkleiden': ['IN', 'CH', 'GE'], 
            'Willenskraft': ['MU', 'IN', 'CH'], 
            'Fährtensuchen': ['MU', 'IN', 'GE'], 
            'Fesseln': ['KL', 'FF', 'KK'], 
            'Fischen & Angeln': ['FF', 'GE', 'KO'], 
            'Orientierung': ['KL', 'IN', 'IN'],
            'Pflanzenkunde': ['KL', 'FF', 'KO'],
            'Tierkunde': ['MU', 'MU', 'CH'],
            'Wildnisleben': ['MU', 'GE', 'KO'],
            'Brett- & Glücksspiel': ['KL', 'KL', 'IN'],
            'Geographie': ['KL', 'KL', 'IN'],
            'Geschichtswissen': ['KL', 'KL', 'IN'],
            'Götter & Kulte': ['KL', 'KL', 'IN'],
            'Kriegskunst': ['MU', 'KL', 'IN'],
            'Magiekunde': ['KL', 'KL', 'IN'],
            'Mechanik': ['KL', 'KL', 'FF'],
            'Rechnen': ['KL', 'KL', 'IN'],
            'Rechtskunde': ['KL', 'KL', 'IN'],
            'Sagen & Legenden': ['KL', 'KL', 'IN'],
            'Sphärenkunde': ['KL', 'KL', 'IN'],
            'Sternkunde': ['KL', 'KL', 'IN'],
            'Alchimie': ['MU', 'KL', 'FF'],
            'Boote & Schiffe': ['FF', 'GE', 'KK'],
            'Fahrzeuge': ['CH', 'FF', 'KO'],
            'Handel': ['KL', 'IN', 'CH'],
            'Heilkunde Gift': ['MU', 'KL', 'IN'],
            'Heilkunde Krankheiten': ['MU', 'IN', 'KO'],
            'Heilkunde Seele': ['IN', 'CH', 'KO'],
            'Heilkunde Wunden': ['KL', 'FF', 'FF'],
            'Holzbearbeitung': ['FF', 'GE', 'KK'],
            'Lebensmittelbearbeitung': ['IN', 'FF', 'FF'],
            'Lederbearbeitung': ['FF', 'GE', 'KO'],
            'Malen & Zeichnen': ['IN', 'FF', 'FF'], 
            'Metallbearbeitung': ['FF', 'KO', 'KK'], 
            'Musizieren': ['CH', 'FF', 'KO'], 
            'Schlösserknacken': ['IN', 'FF', 'FF'], 
            'Steinbearbeitung': ['FF', 'FF', 'KK'], 
            'Stoffbearbeitung': ['KL', 'FF', 'FF']}

def QS(FW):
        """
        Berechnet die QS aus dem FW.

        Args:
            FW (int): Fähigkeitswert/Fähigkeitspunkte die nach einer Probe noch übrig sind.

        Returns:
            QS (int): Die Qualitätsstufe der der verbleibende FW/FP entspricht. 
        """
        return (FW+2)//3


def spec_text(text, color, style=bcolors.reset):
    return style+color+text+bcolors.reset

def scrape_creatures_from_ulisses():
    if not os.path.exists(path):
        os.mkdir(path)
    #test = '<a class="ulSubMenu" href="Best_Chim%C3%A4ren.html" title="Chimären">'
    #<a style="border-bottom: 1px solid gray; padding-left: 2px; padding-right: 2px;" href="regeln.html" title="Regeln" class="ulsubmenu sibling first" role="menuitem"> Regeln<i class="sub pro-angle-down"></i></a>
    # access parent web page
    main_page = "https://dsa.ulisses-regelwiki.de/bestiarium.html"
    abstract_page = urlopen(main_page)
    #html = abstract_page.read().decode("utf-8")
    html = abstract_page.read().decode("iso-8859-1")
    re_link_pattern = r'<a\s+[^>]*class="ulSubMenu"[^>]*href="([^"]+)"|<a\s+[^>]*href="([^"]+)"[^>]*class="ulSubMenu"'
    sub_links = re.findall(re_link_pattern , html)
    sub_links = [m[0] or  m[1] for m in sub_links]
    creature_links = []
    for link in sub_links:
        abstract_page = urlopen("https://dsa.ulisses-regelwiki.de/"+link)
        html = abstract_page.read().decode("iso-8859-1")
        sub_sub_links = re.findall(re_link_pattern , html)
        sub_sub_links = [m[0] or  m[1] for m in sub_sub_links]
        creature_links += sub_sub_links

    print(creature_links)
    for link in creature_links:
        abstract_page = urlopen("https://dsa.ulisses-regelwiki.de/"+link)
        html = abstract_page.read().decode("iso-8859-1")

        data = {}
        # get attributes
        data['MU'] = int(re.findall(r'<strong>MU</strong>\s*(\w+)\s*', html)[0])
        data['KL'] = int(re.findall(r'<strong>KL</strong>\s*(\w+)\s*', html)[0])
        data['IN'] = int(re.findall(r'<strong>IN</strong>\s*(\w+)\s*', html)[0])
        data['CH'] = int(re.findall(r'<strong>CH</strong>\s*(\w+)\s*', html)[0])
        data['FF'] = int(re.findall(r'<strong>FF</strong>\s*(\w+)\s*', html)[0])
        data['GE'] = int(re.findall(r'<strong>GE</strong>\s*(\w+)\s*', html)[0])
        data['KO'] = int(re.findall(r'<strong>KO</strong>\s*(\w+)\s*', html)[0])
        data['KK'] = int(re.findall(r'<strong>KK</strong>\s*(\w+)\s*', html)[0])

        # get LeP, AsP and KaP
        data['LeP'] = int(re.findall(r'<strong>\s*LeP\s*</strong>[:]*\s*(\w+)\s*', html)[0])
        data['maxLeP'] = data['LeP']
        INI_str = re.findall(r'<strong>INI</strong>\s*([\w\+]+)\s*', html)[0]
        data['base_INI'], data['INI_bonus'] = re.split('\+',INI_str)
        data['base_INI'] = int(data['base_INI'])
        

        data['RS'] = int(re.findall(r'<p><strong>RS[/\w:]*</strong>[:]*\s*(\w+)[/\w]*', html)[0])
        data['actions'] = int(re.findall(r'<p><strong>Aktionen[:]*\s*</strong>[:]*\s*(\w+)\s*', html)[0])
        data['size'] = re.findall(r'<strong>Größenkategorie[:]*\s*</strong>[:]*\s*(\w+)\s*', html)[0]
        data['species'] = re.findall(r'<strong>Typus[:]*\s*</strong>[:]*\s*(\w+)\s*', html)[0]
        data['loot'] = re.findall(r'<strong>Beute[:]*</strong>[:]*\s*([\w\s,\(\)]+)\s*', html)[0]
        data['kampfverhalten'] = re.findall(r'<strong>Kampfverhalten[:]*\s*</strong>[:]*\s*(\w+)\s*', html)[0]

        data['name'] = re.findall(r'"title":\s*"(\w+)"', html)[0]

        try:
            data['AsP'] = int(re.findall(r'<strong>AsP</strong>\s*(\w+.*)\s*</td>', html)[0])
        except:
            data['AsP'] = 0
        try:
            data['KaP'] = int(re.findall(r'<strong>KaP</strong>\s*(\w+.*)\s*</td>', html)[0])
        except:
            data['KaP'] = 0
        data['maxAsP'] = AsP
        data['maxKaP'] = KaP

        # get talents
        data['talents'] = {}
        #for talent in re.split('\s*,\s*', re.findall('<p><strong>Talente[:]*</strong>[:]*\s*(\w+.*)\s*</p>', html)[0]):
        for talent in re.split('\s*, \s*',re.findall('<p><strong>Talente[:]*</strong>[:]*\s*([\w\(\)/\s,]+)\s*', html)[0]):
            #print(talent)
            if re.split(' ', talent)[0] in talents.keys():
                #print(talent)
                name, value = re.split(' ', re.sub(r'\s*\(.*\)','',talent))
                #name, value = re.split(' ', talent)
                talents[name] = int(value)

        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)

        #print(self.talents)
'''
cases = [case1, case2, case3]

data = [c.to_dict() for c in cases]

with open("cases.json", "w") as f:
    json.dump(data, f, indent=4)


with open("cases.json", "r") as f:
    raw = json.load(f)

cases = [Case.from_dict(d) for d in raw]

'''


class Kreatur:
    def __init__(self, link=None, lookfor="", **kwargs):
        #super().__init__()
        """
        Character class: represents a character with its all stats.
    
        VARIABLES:
            # CHARACTERISTICS
            name (str) = full name
            family (str) = family name
            home (str) = location of birth
            birthday (str) = date of birth
            species (str) = species
            size (str) = body height
            hair (str) = hair color
            eyes (str) = eye color
            culture (str) = culture / origin
            profession (str) = profession
            social_status (str) = social status
            gender (str) = gender

            # ATTRIBUTES
            MU (int) = Mut 
            KL (int) = Klugheit
            IN (int) = Intuition
            CH (int) = Charisma
            FF (int) = Fingerfertigkeit 
            GE (int) = Geschicklichkeit
            KO (int) = Konstitution
            KK (int) = Körperkraft

            # STATUS VALUES
            LeP (int) = current hit points
            maxLeP (int) = maximum hit points
            AsP (int) = current astral points
            maxAsP (int) = maximum astral points
            KaP (int) = current karmal points 
            maxKaP (int) = maximum karmal points 
            SK (int) = Seelenkraft 
            ZK (int) = Zähigkeit 
            AW (int) = Ausweichen
            INI (int) = Initiative 
            schip (int) = aktuelle Schicksalspunkte
            maxschip (int) = maximale Schicksalspunkte 
            GS (int) = Geschwindigkeit 
            statuus (dict{str:int})= aktive Statuseffecte und deren Stufe
            disabled (bool) = gibt an ob der Charakter handlungsunfähig ist
            dying (int) = gibt an wie viele KR der Charakter schon im sterben liegt
        """
        self.statuus = {}
        self.disabled = False
        self.dying = False
    
        if link is not None:
            self.scrape_from_ulissis(link)
        elif lookfor != '':
            alt_name = re.sub(r'ü', r'ue', lookfor.lower())
            alt_name = re.sub(r'ä', r'ae', alt_name)
            alt_name = re.sub(r'ö', r'oe', alt_name)
            alt_name = re.sub(r'\s+', '_', alt_name)
            print('Durchsuche Bestiarium auf Ulisses nach möglichen Einträgen...')
            try: 
                link = 'https://dsa.ulisses-regelwiki.de/Best_{:}.html'.format(alt_name)
                print(link)
                urlopen(link)
                self.scrape_from_ulissis(link)
            except:
                pass

            
            alt_name = re.sub("(^|_|-)\w{1}", lambda p: p.group(0).upper(), alt_name)
            link = 'https://dsa.ulisses-regelwiki.de/Best_{:}.html'.format(alt_name)
            print(link)
            urlopen(link)
            self.scrape_from_ulissis(link)
        
            print('No URL found! Standard values will be used.')
        else: # setstandard values
            # characteristics
            self.name = ''
            self.species = ''
            self.size = ''

            # attributes
            self.MU = 8
            self.KL = 8
            self.IN = 8
            self.CH = 8
            self.FF = 8
            self.GE = 8
            self.KO = 8
            self.KK = 8

            # status values
            self.LeP = 20
            self.maxLeP = 20
            self.AsP = 0
            self.maxAsP = 0
            self.KaP = 0
            self.maxKaP = 0
            self.SK = 2
            self.ZK = 2
            self.AW = 8
            self.INI = 14
            self.base_INI = 14
            self.INI_bonus = '1W6'
            self.GS = 8

            for k, v in kwargs.items():
                setattr(self, k, v)

    def roll_INI(self):
        INI_bonus_num, INI_bonus_dice = re.split('W', self.INI_bonus)
        self.INI = self.base_INI + sum([random.randint(1, int(INI_bonus_dice)) for _ in range(int(INI_bonus_num))])


    def scrape_from_ulissis(self, link):
        # access web page
        abstract_page = urlopen(link)
        html = abstract_page.read().decode("utf-8")
        #print(html)
        # get attributes
        self.MU = int(re.findall(r'<strong>MU</strong>\s*(\w+)\s*', html)[0])
        self.KL = int(re.findall(r'<strong>KL</strong>\s*(\w+)\s*', html)[0])
        self.IN = int(re.findall(r'<strong>IN</strong>\s*(\w+)\s*', html)[0])
        self.CH = int(re.findall(r'<strong>CH</strong>\s*(\w+)\s*', html)[0])
        self.FF = int(re.findall(r'<strong>FF</strong>\s*(\w+)\s*', html)[0])
        self.GE = int(re.findall(r'<strong>GE</strong>\s*(\w+)\s*', html)[0])
        self.KO = int(re.findall(r'<strong>KO</strong>\s*(\w+)\s*', html)[0])
        self.KK = int(re.findall(r'<strong>KK</strong>\s*(\w+)\s*', html)[0])

        self.LeP = int(re.findall(r'<strong>\s*LeP\s*</strong>[:]*\s*(\w+)\s*', html)[0])
        self.maxLeP = self.LeP
        INI_str = re.findall(r'<strong>INI</strong>\s*([\w\+]+)\s*', html)[0]
        self.base_INI, self.INI_bonus = re.split('\+',INI_str)
        self.base_INI = int(self.base_INI)
        

        self.RS = int(re.findall(r'<p><strong>RS[/\w:]*</strong>[:]*\s*(\w+)[/\w]*', html)[0])
        self.actions = int(re.findall(r'<p><strong>Aktionen[:]*\s*</strong>[:]*\s*(\w+)\s*', html)[0])
        self.size = re.findall(r'<strong>Größenkategorie[:]*\s*</strong>[:]*\s*(\w+)\s*', html)[0]
        self.species = re.findall(r'<strong>Typus[:]*\s*</strong>[:]*\s*(\w+)\s*', html)[0]
        self.loot = re.findall(r'<strong>Beute[:]*</strong>[:]*\s*([\w\s,\(\)]+)\s*', html)[0]
        self.kampfverhalten = re.findall(r'<strong>Kampfverhalten[:]*\s*</strong>[:]*\s*(\w+)\s*', html)[0]

        self.name = re.findall(r'"title":\s*"(\w+)"', html)[0]

        try:
            self.AsP = int(re.findall(r'<strong>AsP</strong>\s*(\w+.*)\s*</td>', html)[0])
        except:
            self.AsP = 0
        try:
            self.KaP = int(re.findall(r'<strong>KaP</strong>\s*(\w+.*)\s*</td>', html)[0])
        except:
            self.KaP = 0
        self.maxAsP = self.AsP
        self.maxKaP = self.KaP

        # get talents
        self.talents = {}
        #for talent in re.split('\s*,\s*', re.findall('<p><strong>Talente[:]*</strong>[:]*\s*(\w+.*)\s*</p>', html)[0]):
        for talent in re.split('\s*, \s*',re.findall('<p><strong>Talente[:]*</strong>[:]*\s*([\w\(\)/\s,]+)\s*', html)[0]):
            #print(talent)
            if re.split(' ', talent)[0] in talents.keys():
                #print(talent)
                name, value = re.split(' ', re.sub(r'\s*\(.*\)','',talent))
                #name, value = re.split(' ', talent)
                self.talents[name] = int(value)

        #print(self.talents)

    @classmethod
    def __info__(cls):
        info = []
        for name, func in inspect.getmembers(cls, inspect.isfunction):
            sig = inspect.signature(func)   # e.g. (a: int, b: int) -> int
            doc = inspect.getdoc(func) or "No description available."
            info.append(spec_text(f"{name}{sig}", bcolors.cyan, bcolors.BOLD) + f"\n{doc}\n")
        print(f"\n".join(info))

    def heal(self, amount:int):
        """
        Heilt den Charakter um <amount> LeP bis zum LeP maximum.
        Aktuallisiert die LeP des Characters und gibt sie aus.

        Args:
            amount (int): Menge der geheilten LeP.
        """
        pain_index = int(4*(self.maxLeP - self.LeP)/self.maxLeP)
        self.LeP += amount
        if self.LeP > self.maxLeP:
            self.LeP = self.maxLeP
        else:
            if int(4*(self.maxLeP - self.LeP)/self.maxLeP) != pain_index:
                self.statuus['Schmerz'] -= pain_index - int(4*(self.maxLeP - self.LeP)/self.maxLeP) 
                if self.statuus['Schmerz'] == 0:
                    self.statuus.pop('Schmerz')

        print("{0:}'s aktuelle Lebenspunkte betragen {1:}.".format(self.name, self.LeP))

    def get_status(self, status:str):
        """
        Fügt dem Charakter ein Statusleiden hinzu.
        Falls das Statusleiden bereits vorhanden ist wird die Stufe um 1 erhöht.
        Statusleiden und Stufe sind im dict self.statuus = {status(str):stufe(int)} gespeichert.

        Args:
            status (str): Statusleiden das hinzugefügt oder erhöht werden soll.
        """
        if status in self.statuus.keys():
            self.statuus[status] += 1
            if self.statuus[status] == 4:
                print(spec_text('{0:} erleidet die 4. Stufe {0:} und ist handlungsunfähig!'.format(self.name, status), bcolors.red) )
        else:
            self.statuus[status] = 1

    def cure_status(self, status:str, reduce=1, cure=False):
        """
        Heilt Statusleiden des Charakters falls vorhanden.
        Gibt eine Meldung aus falls der Status nicht besteht.

        Args:
            status (str): Statusleiden das geheilt oder reduziert werden soll.
            reduce (int): Anzahl der Stufen die geheilt werden sollen. Status wird entfernt wenn Stufe 0 erreicht.
            cure (bool): Wenn True, wirden der Status vollständig geheilt unabhängig von der Stufe.   
        """
        if status in self.statuus.keys():
            if cure:
                self.statuus.pop(status)
                print(spec_text('Status {0:} wurde vollständig geheilt.'.format(status), bcolors.green))
            else:
                self.statuus[status] -= reduce
                if self.statuus[status] <= 0:
                    self.statuus.pop(status)
                    print(spec_text('Status {0:} wurde vollständig geheilt.'.format(status), bcolors.green))
                else:
                    print(spec_text('Die Stufe des Status {0:} wurde um {1:} reduziert.'.format(status, reduce), bcolors.green))
                    print('Es verbleiben {0:} Stufen {1:}.'.format(self.statuus(status), status))
        else:
            print('{0:} leidet nicht unter Stufen des Status {1:}'.format(self.name, status))

    def status(self):
        """
        Liste von Statusleiden.
        """
        print(spec_text('Status:', bcolors.cyan))
        if self.statuus == {}:
            print('{:} leidet an keinen Zuständen'.format(self.name))
        else:
            print('{:} leidet an folgenden Zuständen:'.format(self.name))
            for status, stufe in self.statuus.items():
                if stufe > 1:
                    print('{0:} Stufen {1:}'.format(stufe, status))
                else:
                    print('{0:} Stufe {1:}'.format(stufe, status))
        if self.dying:
            print(spec_text('{:} liegt im sterben.'.format(self.name), bcolors.red))
        elif self.disabled:
            print(spec_text('{:} ist handlungsunfähig.'.format(self.name), bcolors.yellow))

    def schaden(self, amount:int):
        """
        Fügt dem Charakter <amount> Schaden zu und aktualisiert die Lebenspunkte.
        Gibt anschließend die aktuellen Lebenspunkte aus und eine Warnung falls der Charakter
        handlungsunfähig wird oder im sterben liegt. 

        Args:
            amount (int): Menge des erlittenen Schadens.
        """
        pain_index = int(4*(self.maxLeP - self.LeP)/self.maxLeP)
        self.LeP -= amount
        print("{0:}'s aktuelle Lebenspunkte betragen {1:}.".format(self.name, self.LeP))

        if self.LeP > 0:
            if self.LeP <= 5:
                self.statuus['Schmerz'] = 4
                print("{0:} hat {1:} Stufen Schmerz.".format(self.name, self.statuus['Schmerz']))
                print("{0:} versucht durch eine Probe auf Selbstbeherrschung die Handlungsfähigkeit zu bewahren...".format(self.name))
                if self.talent_check('Selbstbeherrschung') > 0:
                    print("{0:} ist vorerst handlungsfähig".format(self.name))
                else:
                    print(spec_text("{0:} wird handlungsunfähig!".format(self.name), bcolors.red))
                    self.disabled = True
            elif int(4*(self.maxLeP - self.LeP)/self.maxLeP) > 0:
                if not 'Schmerz' in self.statuus.keys():
                    self.statuus['Schmerz'] = int(4*(self.maxLeP - self.LeP)/self.maxLeP)
                else:
                    if int(4*(self.maxLeP - self.LeP)/self.maxLeP) > pain_index:
                        self.statuus['Schmerz'] += int(4*(self.maxLeP - self.LeP)/self.maxLeP) - pain_index
                print("{0:} hat {1:} Stufen Schmerz.".format(self.name, self.statuus['Schmerz']))
        else:
            print(spec_text("{0:} liegt im sterben!".format(self.name), bcolors.red))
            self.dying = True

    def attribute(self):
        """
        Listet alle Attribute des Charakters auf. 
        """
        print(spec_text("Attributes", bcolors.cyan, bcolors.BOLD))
        print(spec_text("MU ", bcolors.cyan, bcolors.reset), self.MU)
        print(spec_text("KL ", bcolors.cyan, bcolors.reset), self.KL)
        print(spec_text("IN ", bcolors.cyan, bcolors.reset), self.IN)
        print(spec_text("CH ", bcolors.cyan, bcolors.reset), self.CH)
        print(spec_text("FF ", bcolors.cyan, bcolors.reset), self.FF)
        print(spec_text("GE ", bcolors.cyan, bcolors.reset), self.GE)
        print(spec_text("KO ", bcolors.cyan, bcolors.reset), self.KO)
        print(spec_text("KK ", bcolors.cyan, bcolors.reset), self.KK)

    def talent_check(self, probe, mod=0):
        """
        Führt eine Probe auf das angegebene Talent aus.
        Gibt sowohl die Attribute auf die gewürfelt wird als auch die Attributswerte den FW des Charakters aus.
        Gibt anschließend die QS der Probe und informiert über krittische Erfolge und Fehlschläge.

        Args:
            probe (str): Talent auf das gewürfelt werden soll.
            mod (int): Modifikation der Probe. Negative Werte entsprechen einer Erschwerniss.
        """
        for index, talent in enumerate(talents):
            if probe.lower() in talent.lower():

                if talent in self.talents.keys():
                    # Fähigkeitswert
                    FW = self.talents[talent]
                else:
                    FW = 0

                # Würfelwurf
                roll = np.array([random.randint(1, 20) for _ in range(3)])

                # Attribute
                attributes = np.array([getattr(self, attribute) for attribute in talents[talent] ])
                #attributes = np.array([getattr(self, attribute) for attribute in talents.get(talent)])

                try:
                    mod -= self.statuus['Schmerz']
                except:
                    pass
                
                print('{0:} würfelt eine Probe auf {1:} mit einer Erschwerniss von {2:}.'.format(self.name, probe, mod))
                print("{0:}'s FW ist {1:}.".format(self.name, FW))
                print('Die relevanten Atribute sind {0:}/{1:}/{2:} = {3:}/{4:}/{5:}'.format(talents[talent][0], talents[talent][1], talents[talent][2], attributes[0], attributes[1], attributes[2]))
                print('Die Würfel zeigen: {0:} - {1:} - {2:}'.format(roll[0], roll[1], roll[2]))

                if np.sum(roll == 1) == 2:
                    print(spec_text('__________________KRITISCHER_ERFOLG__________________\nQS = {:}'.format(QS(FW)), bcolors.purple, bcolors.BOLD))
                    break

                if np.sum(roll == 1) == 3:
                    print(spec_text('__________________EPISCHER_ERFOLG__________________\nQS = {:}'.format(QS(FW)), bcolors.orange, bcolors.BOLD))
                    break

                if np.sum(roll == 20) == 2:
                    print(spec_text('__________________KRITISCHER_FEHLSCHLAG__________________', bcolors.red, bcolors.BOLD))
                    break

                if np.sum(roll == 20) == 3:
                    print(spec_text('__________________EPISCHER_FEHLSCHLAG__________________', bcolors.red, bcolors.BOLD))
                    break

                diff = (roll-mod) - attributes
                FP = FW - sum(diff[diff > 0])
                if FP >= 0:
                    print(spec_text('ERFOLG! mit QS = {:}'.format(QS(FP)), bcolors.cyan))
                    return QS(FP)
                else:
                    print(spec_text('FEHLSCHLAG!', bcolors.red))
                    return 0

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


class EventTracker:
    def __init__(self, *args, **kwargs):
        self.turn = 0
        self.elapsed_time = [0,0,0,0] # [KR, Minuten, Stunden, Tage]
        self.lasting_effects = {}
        self.incoming_events = {}
        self.actors = []
        for actor in args:
            self.actors.append(actor)
        #self.update_order_of_action()

    def add_actors(self, actors):
        for actor in actors:
            self.actors.append(actor)
        #self.update_order_of_action()

    def delete_actors(self, name):
        for actor in self.actors:
            if actor.name == name:
                self.actors.remove(actor)
                del actor

        #self.update_order_of_action()

    def get_INIS(self):
        print(spec_text('Welche Initiativen haben die Charaktere?', bcolors.cyan))
        for actor in self.actors:
            if isinstance(actor, Character):
                actor.INI = input('{0:}s Initiative: '.format(actor.name))
            elif isinstance(actor, Kreatur):
                actor.roll_INI()

    def update_order_of_action(self):
        INIs = []
        for actor in self.actors:
            INIs.append(float(actor.INI)+float(actor.base_INI)/100.+random.uniform(0, 1e-3))

        self.actors = [actor for _, actor in sorted(zip(INIs, self.actors))]
        self.actors.reverse()

    def transform_time(self, time):
        days = time//(24*60*5)
        time -= days*24*60*5
        hours = time//(60*5)
        time -= hours*(60*5)
        minutes = time//5
        time -= minutes*5
        return [time, minutes, hours, days] 
    
    def inv_transform_time(self, time):
        return time[0]+time[1]*5+time[2]*60*5+time[3]*24*60*5

    def update_times(self, duration, unit = 'KR'):
        if isinstance(duration, int):
            amount = duration
        elif isinstance(duration, str):
            amount, unit = re.split('\s+', duration)
            amount = int(amount)

        if 'k' in unit.lower() and 'r' in unit.lower():
            duration = amount
        elif 'min' in unit.lower():
            duration = amount*5 
        elif 'h' in unit.lower() or 'st' in unit.lower():
            duration = amount*5*60
        elif 'day' in unit.lower() or 'tag' in unit.lower():
            duration = amount*5*60

        self.elapsed_time = self.transform_time(self.inv_transform_time(self.elapsed_time)+duration)

        for effect in list(self.lasting_effects.keys()):
            if self.inv_transform_time(self.lasting_effects[effect])-duration <= 0:
                print(spec_text('Der Effekt {0:} ist abgelaufen!'.format(effect), bcolors.yellow))
                self.lasting_effects.pop(effect)
            else:
                self.lasting_effects[effect] = self.transform_time(self.inv_transform_time(self.lasting_effects[effect])-duration)

        for effect in list(self.incoming_events.keys()):
            if self.inv_transform_time(self.incoming_events[effect])-duration <= 0:
                print(spec_text('{0:}!!'.format(effect), bcolors.yellow))
                self.incoming_events.pop(effect)
            else:
                self.incoming_events[effect] = self.transform_time(self.inv_transform_time(self.incoming_events[effect])-duration)

    def show_lasting_effects(self):
        print(spec_text('Anhaltende Effekte:', bcolors.cyan))
        for effect in self.lasting_effects.keys():
            duration_str = ''
            if self.lasting_effects[effect][3] != 0:
                duration_str += '{:} Tage '.format(self.lasting_effects[effect][3])
            if self.lasting_effects[effect][2] != 0:
                duration_str += '{:} Stunden '.format(self.lasting_effects[effect][2])
            if self.lasting_effects[effect][1] != 0:
                duration_str += '{:} Minuten '.format(self.lasting_effects[effect][1])
            if self.lasting_effects[effect][0] != 0:
                duration_str += '{:} KR '.format(self.lasting_effects[effect][0])
            print('{0:} hält noch {1:} an'.format(effect, duration_str))

    def show_incoming_events(self):
        print(spec_text('Bevorstehende Events:', bcolors.cyan))
        for effect in self.incoming_events.keys():
            duration_str = ''
            if self.incoming_events[effect][3] != 0:
                duration_str += '{:} Tage '.format(self.incoming_events[effect][3])
            if self.incoming_events[effect][2] != 0:
                duration_str += '{:} Stunden '.format(self.incoming_events[effect][2])
            if self.incoming_events[effect][1] != 0:
                duration_str += '{:} Minuten '.format(self.incoming_events[effect][1])
            if self.incoming_events[effect][0] != 0:
                duration_str += '{:} KR '.format(self.incoming_events[effect][0])
            print('{0:} in {1:}'.format(effect, duration_str))

    def order_of_action(self):
        self.update_order_of_action()
        print(spec_text('Aktionsreihenfolge:', bcolors.cyan))
        for i, actor in enumerate(self.actors):
            print('{0:}. {1:} INI={2:}, LeP={3:}'.format(i+1, actor.name, actor.INI, actor.LeP))

    def add_effect(self, name, duration, unit='KR'):
        while name in self.lasting_effects.keys():
            if name == 'break':
                return
            else:
                print('Es gibt bereits einen Effekt mit diesem Namen!')
                name = input('Wähle einen anderen:')
        
        if isinstance(duration, int):
            amount = duration
        elif isinstance(duration, str):
            amount, unit = re.split('\s+', duration)
            amount = int(amount)

        if 'k' in unit.lower() and 'r' in unit.lower():
            duration = amount
        elif 'min' in unit.lower():
            duration = amount*5 
        elif 'h' in unit.lower() or 'st' in unit.lower():
            duration = amount*5*60
        elif 'day' in unit.lower() or 'tag' in unit.lower():
            duration = amount*5*60

        self.lasting_effects[name] = self.transform_time(duration)


    def add_event(self, name, duration, unit='KR'):
        while name in self.incoming_events.keys():
            if name == 'break':
                return
            else:
                print('Es gibt bereits ein Event mit diesem Namen!')
                name = input('Wähle einen anderen:')
        
        if isinstance(duration, int):
            amount = duration
        elif isinstance(duration, str):
            amount, unit = re.split('\s+', duration)
            amount = int(amount)

        if 'k' in unit.lower() and 'r' in unit.lower():
            duration = amount
        elif 'min' in unit.lower():
            duration = amount*5 
        elif 'h' in unit.lower() or 'st' in unit.lower():
            duration = amount*5*60
        elif 'day' in unit.lower() or 'tag' in unit.lower():
            duration = amount*5*60

        self.incoming_events[name] = self.transform_time(duration)

    def end(self):
        self.endit = True
        ip = get_ipython()
        if ip is not None:
            ip.ask_exit()

    def encounter(self):
        self.endit = False
        ns = {"self": self}
        # Give names to actors
        for i, actor in enumerate(self.actors, 1):
            ns[actor.name] = actor
        print(spec_text('_________EINE_BEGEGNUNG_BEGINNT_________', bcolors.cyan, bcolors.BOLD))
        self.get_INIS()
        while not self.endit:
            print(spec_text('KR {:} beginnt!'.format(self.elapsed_time[0]+1), bcolors.cyan, bcolors.BOLD))
            self.order_of_action()
            self.show_lasting_effects()
            self.show_incoming_events()
            embed(user_ns=ns,banner1="", banner2="",confirm_exit=False)
            for actor in self.actors:
                if self.endit:
                    break
                print(spec_text('{0:} ist am Zug!'.format(actor.name), bcolors.cyan))
                # what shall happen next ?
                embed(user_ns=ns,banner1="", banner2="",confirm_exit=False)
            self.update_times(1)
            self.update_order_of_action()

#print(sys.getsizeof(Klatu))

#Klatu.money
#Klatu.spells
#Klatu.benefits
#Klatu.talent_check('Verbergen', -2)


#i=0
#n=74
#print(len(Klatu.data.items()))
#print(n*50)
#for field, value in Klatu.data.items():
#    if value is not None and i >= n*50 and i < (n+1)*50:
#        print(field, value)
#    i+=1