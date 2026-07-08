from services.pdf_character_loader import load_character_from_pdf
from services.checks import skill_check
from models.status_effect import Pain, ValueCondition


Klatu_link = 'data/characters/Klatu3.pdf'
eisgeist_link = 'https://dsa.ulisses-regelwiki.de/Best_Eisgeist.html'

Klatu = load_character_from_pdf(Klatu_link)

print("QS = {:}".format(skill_check(Klatu, "Klettern")))

print("Klatus maximale LeP betragen {:}".format(Klatu.LeP.maximum))
print("Klatus aktuelle LeP betragen {:}".format(Klatu.LeP.current))

Klatu.LeP.decrease(15)

print("Klatus aktuelle LeP betragen {:}".format(Klatu.LeP.current))

Klatu.add_status(Pain, ValueCondition(Klatu.LeP, maximum=int(0.75*Klatu.LeP.maximum)))

print("Klatu leidet an {0:} Stufen {1:}".format(Klatu.status_effects[Pain].level, Klatu.status_effects[Pain].name))
print("Der Zustand verschwindet wenn seine LeP über {:} steigen".format(int(0.75*Klatu.LeP.maximum)))

print("QS = {:}".format(skill_check(Klatu, "Klettern")))

while len(Klatu.status_effects) != 0:
    input()
    Klatu.LeP.increase(1)
    print("Klatu heilt sich um 1 LeP und besitzt nun {:} LeP".format(Klatu.LeP.current))
    Klatu.status_effects[Pain].check_validity()
    print("Klatu leidet an {0:} Stufen {1:}".format(Klatu.status_effects[Pain].level, Klatu.status_effects[Pain].name))


'''
# create characters
Klatu = Character(Klatu_link, name='Klatu')
Adriana = Character(Klatu_link, name='Adriana')
Azir = Character(Klatu_link, name='Azir')

# create a Session
Session = EventTracker(Klatu, Azir, Adriana)

# add effects and events
Session.add_effect('Adriana heult rum', 2)
Session.add_event('Das Tor bricht', 5)

# start an encounter
Session.encounter()
'''
