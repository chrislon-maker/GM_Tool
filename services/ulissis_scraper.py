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

def scrape_creature(url: str) -> Creature:
    creature = Creature(source="regelwiki", source_url=url)
    ...
    return creature


def find_creature_url(name: str) -> str | None:
    ...

def scrape_all_creatures() -> list[dict]:
    ...

def scrape_creatures(url: str) -> dict:
    directory = 'data/creatures/'
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

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
    for link in tqdm(creature_links):
        abstract_page = urlopen("https://dsa.ulisses-regelwiki.de/"+link)
        html = abstract_page.read().decode("utf-8")


        data = {}
        data['name'] = re.findall(r'"title":\s*"(\w+)"', html)[0]

        if skip_existing and os.path.exists(directory+"{:}.json".format(data['name'])):
            continue
 
        # get attributes
        print(link)
        
        data['MU'] = int(re.findall(r'<strong>\s*MU\s*</strong>\s*(\w*)\s*', html)[0])
        data['KL'] = int(re.findall(r'<strong>\s*KL\s*</strong>\s*(\w*)\s*', html)[0])
        data['IN'] = int(re.findall(r'<strong>\s*IN\s*</strong>\s*(\w*)\s*', html)[0])
        data['CH'] = int(re.findall(r'<strong>\s*CH\s*</strong>\s*(\w*)\s*', html)[0])
        data['FF'] = int(re.findall(r'<strong>\s*FF\s*</strong>\s*(\w*)\s*', html)[0])
        data['GE'] = int(re.findall(r'<strong>\s*GE\s*</strong>\s*(\w*)\s*', html)[0])
        data['KO'] = int(re.findall(r'<strong>\s*KO\s*</strong>\s*(\w*)\s*', html)[0])
        data['KK'] = int(re.findall(r'<strong>\s*KK\s*</strong>\s*(\w*)\s*', html)[0])

        # get LeP, AsP and KaP
        data['LeP'] = int(re.findall(r'<strong>\s*LeP\s*</strong>[:]*\s*(\w+)\s*', html)[0])
        data['maxLeP'] = data['LeP']
        INI_str = re.findall(r'<strong>\s*INI\s*</strong>\s*(\w*\D*\w*)\s*', html)[0]
        for value in re.split('\D',INI_str):
            if "W" in value:
                data['INI_bonus'] = value
            else:
                data['base_INI'] = int(value)

        RS_BE = re.findall(r'<p><strong>\s*RS[BE/]*[:]*\s*</strong>[:]*\s*([\d/]*)\s*', html)[0]
        data['RS'], data['BE'] = re.split('/', RS_BE)
        data['actions'] = int(re.findall(r'<p><strong>Aktionen[:]*\s*</strong>[:]*\s*(\w+)\s*', html)[0])
        data['size'] = re.findall(r'<strong>Größenkategorie[:]*\s*</strong>[:]*\s*(.*?)\s*', html)[0]
        data['species'] = re.findall(r'<strong>Typus[:]*\s*</strong>[:]*\s*(\w+)\s*', html)[0]
        data['loot'] = re.findall(r'<strong>Beute[:]*</strong>[:]*\s*([\w\s,\(\)]+)\s*', html)[0]
        try:
            data['kampfverhalten'] = re.findall(r'<strong>Kampfverhalten[:]*\s*</strong>[:]*\s*(\w+)\s*', html)[0]
        except:
            data['kampfverhalten'] = ''


        try:
            data['AsP'] = int(re.findall(r'<strong>AsP</strong>\s*(\w+.*)\s*</td>', html)[0])
        except:
            data['AsP'] = 0
        try:
            data['KaP'] = int(re.findall(r'<strong>KaP</strong>\s*(\w+.*)\s*</td>', html)[0])
        except:
            data['KaP'] = 0
        data['maxAsP'] = data['AsP'] 
        data['maxKaP'] = data['KaP'] 

        # get talents
        data['talents'] = {}
        for talent in re.split('\s*, \s*',re.findall('<p><strong>Talente[:]*</strong>[:]*\s*([\w\(\)/\s,]+)\s*', html)[0]):
            #print(talent)
            if re.split(' ', talent)[0] in talents.keys():
                #print(talent)
                name, value = re.split(' ', re.sub(r'\s*\(.*\)','',talent))
                #name, value = re.split(' ', talent)
                data['talents'][name] = int(value)

        with open(directory+"{:}.json".format(data['name']), "w") as file:
            json.dump(data, file, indent=4)
        

'''
cases = [case1, case2, case3]

data = [c.to_dict() for c in cases]

with open("cases.json", "w") as f:
    json.dump(data, f, indent=4)


with open("cases.json", "r") as f:
    raw = json.load(f)

cases = [Case.from_dict(d) for d in raw]

'''
