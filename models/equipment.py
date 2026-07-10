from __future__ import annotations  # treat type hints as strings
from typing import TYPE_CHECKING

# import classes for type checking
if TYPE_CHECKING:
    from models.creature import Creature

from models.status_effect import DependentCondition, Encumbrance
from models.properties import Attribute

from dataclasses import dataclass, field
import re, random
from enum import Enum, auto



class DamageType(Enum):
    PHYSICAL = auto()
    MAGICAL = auto()

@dataclass
class Damage:
    amount: int
    type: DamageType


@dataclass #TBD
class AttackValue:
    minimum = 0

    def __init__(self, weapon: Weapon, creature: Creature):
        self.weapon = weapon
        self.creature = creature

    @property
    def current(self):
        current_value = self.creature.weapon_skills[self.weapon.weapon_type]

        # attribute bonus
        current_value += (self.creature.attributes[self.weapon.attack_attribute] - 8)//3

        # weapon bonus
        if isinstance(self.weapon, MeeleWeapon):
            current_value += self.weapon_attack_modifier

        # status effect bonus
        additive = 0
        multiplier = 1.

        for effect in self.creature.status_effects.values():
            modifier = effect.get_modifier(self)
            additive += modifier.additive
            multiplier += modifier.multiplicative

        current_value += additive 
        current_value *= multiplier    
        return max(self.minimum, current_value)
    
@dataclass #TBD
class ParryValue:
    minimum = 0

    def __init__(self, weapon: Weapon, creature: Creature):
        self.weapon = weapon
        self.creature = creature

    # needed: relevanter Eigenschaftswert der creature, waffen skill der creature, Zustände der kreatur
    @property
    def current(self):
        current_value = self.creature.weapon_skills[self.weapon.weapon_type]//2

        # attribute bonus
        attribute_bonus = max(self.creature.attributes[attribute] for attribute in self.weapon.damage_attribute.keys())
        current_value += (attribute_bonus - 8)//3

        # weapon bonus
        current_value += self.weapon_parry_modifier

        # status effect bonus
        additive = 0
        multiplier = 1.

        for effect in self.creature.status_effects.values():
            modifier = effect.get_modifier(self)
            additive += modifier.additive
            multiplier += modifier.multiplicative

        current_value += additive 
        current_value *= multiplier    
        return max(self.minimum, current_value)
    



    
#_WEPAONRY_____________________________________________________________________________________

class WeaponType(Enum):
    CROSSBOW = "Armbrust"
    BLOWGUN = "Blasrohr"
    BOW = "Bogen"
    DISCUS = "Diskus"
    FIREBREATH = "Feuerspucken"
    SPIN = "Schleuder"
    THROW = "Wurfwaffe"

    DAGGERS = "Dolche"
    FAN = "Fächer"
    FENCING = "Fechtwaffe"
    BLUNT = "Hiebwaffe"
    CHAIN = "Kettenwaffe"
    LANCE = "Lanze"
    WHIP = "Peitsche"
    BRAWL = "Raufen"
    SHIELD = "Schild"
    SWORD = "Schwert"
    SKEWER = "Spießwaffe"
    POLEARMS = "Stangenwaffen"
    BLUNT_2H = "Zweihandhiebwaffe"
    SWORD_2H = "Zweihandschwert"

@dataclass
class Weapon:
    name: str = ""
    type: WeaponType | None = None
    damage_formula: str = ""    # 2W6 + 4
    attack_attribute: Attribute | None = None

    damage_type: DamageType = DamageType.PHYSICAL
    is_parryable: bool = True
    weight: float | None = None
    price: str | None = None
    complexity: str | None = None
    weapon_advantage: str = ""
    weapon_disadvantage: str = ""
    length: str = ""

    equipped: bool = False

    @property
    def is_equipped(self) -> bool:
        return self.equipped

    def equip(self) -> None:
        self.equipped = True

    def unequip(self) -> None:
        self.equipped = False


@dataclass
class MeeleWeapon(Weapon):
    attack_modifier: int | None = None
    parry_modifier: int | None = None

    attack: AttackValue(self, creature)
    parry: ParryValue(self, creature)
    attack_attribute: Attribute = Attribute.MU
    damage_attribute: dict[Attribute: int] | None = None

    weapon_attack_modifier: int = 0
    weapon_parry_modifier: int = 0

    reach: str = ""

    def roll_damage(self) -> Damage:
        # roll damage
        formula = self.damage_formula.replace(" ", "")

        if "+" in formula:
            dice, flat = formula.split("+")
            flat = int(flat)
        else:
            dice = formula
            flat = 0

        number, sides = dice.split("W")
        amount = sum(random.randint(1, int(sides)) for _ in range(int(number)))
        amount += flat

        # attribute bonus
        attribute_bonus = max(self.creature.attributes[attribute] - threshold for attribute, threshold in self.damage_attribute.items())
        amount += attribute_bonus

        return Damage(type=self.damage_type, amount=amount)




@dataclass
class RangedWeapon(Weapon):
    loading_period: int | None = None
    range: list[int] = field(default_factory=list)
    munition: str | None = None
    



#_ARMOR_____________________________________________________________________________________

@dataclass
class Armor:
    name: str
    encumbrance: int = 0
    physical_protection: int = 0
    magical_protection: int = 0
    equipped: bool = True

    @property
    def is_equipped(self) -> bool:
        return self.equipped
    
    def equip(self, creature: Creature) -> None:
        self.equipped = True
        cond = DependentCondition(lambda armor=self: armor.is_equipped)
        creature.add_status(Encumbrance, cond, level = self.encumbrance)

    def unequip(self) -> None:
        self.equipped = False

    def reduce(self, damage: Damage) -> int:
        if not self.is_equipped:
            return 0
        
        if damage.type is DamageType.PHYSICAL:
            damage.amount -= self.physical_protection
        elif damage.type is DamageType.MAGICAL:
            damage.amount -= self.magical_protection

        damage.amount = max(0, damage.amount)

        return damage

