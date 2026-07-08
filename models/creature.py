from dataclasses import dataclass, field

from models.species import Species
from models.properties import Resource, DerivedValue, Attribute
from models.weapon import Weapon
from models.status_effect import StatusEffect, ConditionCheck

import numpy as np


"""
def lose_hp(self, amount: int):

def heal(self, amount: int):
    ...

def add_status(self, status: str):
    ...

def remove_status(self, status: str):
    ...

def roll_initiative(self):
    ...

def make_skill_check(self, talent: str):
    ...
"""

@dataclass
class CreatureBase:
    name: str = ""
    family: str = ""
    home: str = ""
    birthday: str = ""
    size: str = ""
    hair_color: str = "" 
    eye_color: str = ""
    species: Species = field(default_factory=Species)
    culture: str | None = None
    profession: str | None = None
    social_status: str = "" 
    gender: str = ""

    source: str | None = None
    source_url: str | None = None

    attributes: dict[str, int] = field(default_factory=dict)
    talents: dict[str, int] = field(default_factory=dict)

    LeP: Resource = field(default_factory=lambda: Resource(0))
    KaP: Resource = field(default_factory=lambda: Resource(0))
    AsP: Resource = field(default_factory=lambda: Resource(0))
    chips: Resource = field(default_factory=lambda: Resource(0))

    GS: DerivedValue = field(init=False)
    INI: DerivedValue = field(init=False)
    SK: DerivedValue = field(init=False)
    ZK: DerivedValue = field(init=False)
    AW: DerivedValue = field(init=False)

    #status_effects: list = field(default_factory=list)
    status_effects: dict = field(default_factory=dict)

    weapons: list[Weapon] = field(default_factory=list)
    armor: list[dict] = field(default_factory=list)

    advantages: list[str] = field(default_factory=list)
    disadvantages: list[str] = field(default_factory=list)
    special_abilities: list[str] = field(default_factory=list)

    spells: dict[str, int] = field(default_factory=dict)
    liturgies: dict[str, int] = field(default_factory=dict)

    notes: str = ""

    disabled: bool = False
    dying: bool = False


class Creature(CreatureBase):
    
    def add_status(self, status_type: type[StatusEffect], removal_condition: ConditionCheck) -> None:
        if not status_type in self.status_effects:
            self.status_effects[status_type] = status_type()
        self.status_effects[status_type].removal_conditions.append(removal_condition)
        
    def remove_invalid_status_effects(self) -> None:
        self.status_effects = [
            status for status in self.status_effects
            if status.is_valid()
            ]

    def time_step(self):
        for status in self.status_effects:
            if status.removal_condition is not None and hasattr(status.removal_condition, "tick_round"):
                status.removal_condition.tick_round()

    @property
    def MU(self):
        return self.attributes[Attribute.MU]
    
    @property
    def KL(self):
        return self.attributes[Attribute.KL]
    
    @property
    def IN(self):
        return self.attributes[Attribute.IN]
    
    @property
    def CH(self):
        return self.attributes[Attribute.CH]
    
    @property
    def FF(self):
        return self.attributes[Attribute.FF]
    
    @property
    def GE(self):
        return self.attributes[Attribute.GE]
    
    @property
    def KK(self):
        return self.attributes[Attribute.KK]
    
    @property
    def KO(self):
        return self.attributes[Attribute.KO]
    
    def pain_markers(self) -> tuple[int, int, int, int]:
        return np.array([
            int(0.75 * self.LeP.maximum),
            int(0.50 * self.LeP.maximum),
            int(0.25 * self.LeP.maximum),
            5,
        ])
    
    def get_damage(self, amount: int) -> None:
        pain_markers = self.pain_markers()

        before = {
            marker for marker in pain_markers
            if self.LeP.current < marker
        }

        self.LeP.decrease(amount)

        after = {
            marker for marker in pain_markers
            if self.LeP.current < marker
        }

        newly_crossed = after - before

        for marker in newly_crossed:
            self.add_status(
                Pain,
                DependentCondition(lambda marker=marker: self.LeP.current < marker)
            )


    def heal(self, amount: int) -> None:
        self.LeP.increase(amount)
        if Pain in self.status_effects:
            self.status_effects[Pain].check_validity(self)



    # TBD
    def events_at_turn(self):
        self.time_step()
        self.remove_invalid_status_effects()

    def get_attribute(self, name: str, default: int = 0) -> int:
        return self.attributes.get(name, default)

    def get_resource(self, name: str) -> Resource:
        if name not in self.resources:
            self.resources[name] = Resource()
        return self.resources[name]

    def lose_resource(self, name: str, amount: int) -> None:
        self.get_resource(name).lose(amount)

    def restore_resource(self, name: str, amount: int) -> None:
        self.get_resource(name).restore(amount)


    def add_weapon(self, weapon: Weapon) -> None:
        self.weapons.append(weapon)

    def get_talent_value(self, name: str, default: int = 0) -> int:
        return self.talents.get(name, default)
    

'''


        for k, v in kwargs.items():
            setattr(self, k, v)

    def roll_INI(self):
        INI_bonus_num, INI_bonus_dice = re.split('W', self.INI_bonus)
        self.INI = self.base_INI + sum([random.randint(1, int(INI_bonus_dice)) for _ in range(int(INI_bonus_num))])


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


    def damage(self, amount:int):
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

    def get_attributes(self):
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
'''