from dataclasses import dataclass, field
from .resource import Resource
from .weapon import Weapon
from .status_effect import StatusEffect
import numpy as np
import random, re, inspect


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
class Creature:
    name: str = ""

    source: str | None = None
    source_url: str | None = None

    attributes: dict[str, int] = field(default_factory=dict)
    resources: dict[str, Resource] = field(default_factory=dict)    # LeP, SaP, KaP, Schips
    derived_values: dict[str, int | str] = field(default_factory=dict)  # SKm ZK, AW, INI, GS
    talents: dict[str, int] = field(default_factory=dict)
    status_effects: list[StatusEffect] = field(default_factory=list)

    weapons: list[Weapon] = field(default_factory=list)
    armor: list[dict] = field(default_factory=list)

    advantages: list[str] = field(default_factory=list)
    disadvantages: list[str] = field(default_factory=list)
    special_abilities: list[str] = field(default_factory=list)

    spells: dict[str, int] = field(default_factory=dict)
    liturgies: dict[str, int] = field(default_factory=dict)

    notes: str = ""

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

    def lose_hp(self, amount: int) -> None:
        self.lose_resource("LeP", amount)

    def heal(self, amount: int) -> None:
        self.restore_resource("LeP", amount)

    def add_weapon(self, weapon: Weapon) -> None:
        self.weapons.append(weapon)

    def get_talent_value(self, name: str, default: int = 0) -> int:
        return self.talents.get(name, default)
    

        self.statuus = {}
        self.disabled = False
        self.dying = False
    
        # characteristics
        self.name = ''
        self.species = ''
        self.size = ''

        # attributes
        self.attributes = {
            "MU": 14,
            "KL": 12,
            "IN": 13,
            "CH": 8,
            "FF": 8,
            "GE": 8,
            "KO": 8,
            "KK": 8
        }

        self.resources = {
            "LeP": 32,
            "AsP": 20,
            "KaP": 0
        }

        self.skills = {
            "Klettern": 8,
            "Sinnesschärfe": 10
        }

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