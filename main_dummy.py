from services.pdf_character_loader import load_character_from_pdf
from services.checks import skill_check
from models.status_effect import Pain, Encumbrance, Paralysis, ValueCondition
from models.equipment import Armor, Damage, DamageType


Klatu_link = 'data/characters/Klatu3.pdf'

Klatu = load_character_from_pdf(Klatu_link)

print("QS = {:}".format(skill_check(Klatu, "Klettern")))

print( Klatu.status_update() )

Klatu.armor.append(Armor(name="Lederrüstung", encumbrance=2, physical_protection=3))
Klatu.armor[0].equip(Klatu)

print( Klatu.status_update() )


print("QS = {:}".format(skill_check(Klatu, "Klettern")))

print("Klatus maximale LeP betragen {:}".format(Klatu.LeP.maximum))
print("Klatus aktuelle LeP betragen {:}".format(Klatu.LeP.current))

Klatu.get_damage(Damage(amount = 2, type=DamageType.PHYSICAL))
print("Klatus aktuelle LeP betragen {:}".format(Klatu.LeP.current))
print( Klatu.status_update() )

Klatu.get_damage(Damage(amount = 20, type=DamageType.PHYSICAL))
print("Klatus aktuelle LeP betragen {:}".format(Klatu.LeP.current))
print( Klatu.status_update() )

print("QS = {:}".format(skill_check(Klatu, "Klettern")))

while len(Klatu.status_effects) != 0:
    input()
    Klatu.LeP.increase(1)
    print("Klatu heilt sich um 1 LeP und besitzt nun {:} LeP".format(Klatu.LeP.current))
    Klatu.status_effects[Pain].update()
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
