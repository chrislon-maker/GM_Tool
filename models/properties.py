from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from models.modifiers import ValueModifier, ModifierQuery, DerivedValue
import random
from dataclasses import dataclass
from typing import ClassVar
import json

from .enums import *

#__TALENTS________________________________________________________________________________

@dataclass(frozen=True)
class TalentDefinition:
    name: TalentId
    attributes: tuple[Attribute, Attribute, Attribute]
    category: TalentTypes
    tags: frozenset[ModifierTag]

    _definitions: ClassVar[dict[TalentId, "TalentDefinition"] | None] = None

    @classmethod
    def load_all(cls) -> None:
        if cls._definitions is not None:
            return

        with open("data/talents.json", encoding="utf-8") as f:
            raw_data = json.load(f)

        cls._definitions = {}
        for category in raw_data.keys():
            for name, data in raw_data[category].items():
                cls._definitions[TalentId(name)] = cls(
                    name=TalentId(name),
                    attributes=tuple(Attribute[a] for a in data["attributes"]),
                    category=TalentTypes(category),
                    tags=frozenset(ModifierTag(tag) for tag in data.get("tags", [])),
                )

    @classmethod
    def get(cls, name: str) -> "TalentDefinition":
        cls.load_all()

        if cls._definitions is None:
            raise RuntimeError("Talent definitions were not loaded")

        if name not in cls._definitions:
            raise KeyError(f"Unbekanntes Talent: {name}")

        return cls._definitions[name]

    @classmethod
    def all(cls) -> dict[TalentId, "TalentDefinition"]:
        cls.load_all()

        if cls._definitions is None:
            raise RuntimeError("Talent definitions were not loaded")

        return cls._definitions
    



#__RESOURCES________________________________________________________________________________

class Resource:
    def __init__(self, initial: int, maximum: int | None = None, minimum: int | None = None):
        self.initial = initial
        self.current = initial
        self.maximum = maximum
        self.minimum = minimum

    def set_to(self, value: int):
        self.current = value

    def reset(self):
        self.current = self.initial

    def decrease(self, amount: int) -> None:
        if self.minimum is None:
            self.current = self.current - amount
        else:
            self.current = max(self.minimum, self.current - amount)

    def increase(self, amount: int) -> None:
        if self.maximum is None:
            self.current = self.current + amount
        else:
            self.current = min(self.maximum, self.current + amount)


#__DERIVED VALUES__________________________________________________________________________    

class MovementSpeed(DerivedValue):
    name = "GS"
    value_type = ValueId.MOVEMENT_SPEED
    minimum = 0

    @property
    def calculate(self):
        return self.creature.culture.movement_speed


class SoulPower(DerivedValue):
    name = "SK"
    value_type = ValueId.SOUL_POWER

    @property
    def calculate(self):
        return int( self.creature.culture.soul_power + (self.creature.MU + self.creature.KL + self.creature.IN)/6. )
    


class Toughness(DerivedValue):
    name = "ZK"
    value_type = ValueId.TOUGHNESS

    @property
    def calculate(self):
        return int( self.creature.culture.toughness + (self.creature.KO + self.creature.KO + self.creature.KK)/6. )


class Initiative(DerivedValue):
    name = "INI"
    value_type = ValueId.INITIATIVE
    minimum = 0
    bonus: int = 0
    
    @property
    def base(self):
        if self._base_override is not None:
            return self._base_override + self.bonus

        return self.calculate + self.bonus

    def roll(self, die_sides: int = 6):
        self.bonus = random.randint(1, die_sides)

    @property
    def calculate(self):
        return int( (self.creature.MU + self.creature.GE)/2. )
    

class Evasion(DerivedValue):
    name = "AW"
    minimum = 0

    @property
    def calculate(self):
        return int( self.creature.GE/2. )

    
#_COMBAT_____________________________________________________________

class DamageType(Enum):
    PHYSICAL = auto()
    MAGICAL = auto()

@dataclass
class Damage:
    value_type = ValueId.DAMAGE
    amount: int
    type: DamageType


class AttackValue(DerivedValue):
    minimum = 0

    def __init__(
        self,
        creature: "Creature",
        weapon: "Weapon",
    ):
        super().__init__(creature)
        self.weapon = weapon

    @property
    def value_type(self) -> ValueId:
        if isinstance(self.weapon, RangedWeapon):
            return ValueId.RANGED_ATTACK

        return ValueId.MELEE_ATTACK
    
    @property
    def name(self) -> str:
        if isinstance(self.weapon, RangedWeapon):
            return "FK"

        return "AT"

    @property
    def calculate(self) -> int:
        return self.creature.weapon_skills[self.weapon.type]

    def standard_query(self) -> ModifierQuery:
        return ModifierQuery(
            value_type=self.value_type,
            actor=self.creature,
            subject=self.weapon,
        )
    
    def modifications(self, query: ModifierQuery | None = None) -> list[ModifierContribution]:
        query = query or self.standard_query
        weapon = query.weapon
        creature = query.creature

        # status effects
        contributions = StatusModifierResolver.resolve(query)

        # weapon it self
        if isinstance(weapon, MeleeWeapon):
            modifier = ValueModifier(additive = weapon.attack_modifier)
            if not modifier.is_neutral:
                contributions.append(
                    ModifierContribution(
                    modifier = modifier,   
                    source_name = "Angriffsbonus",
                    source = weapon,
                    description = "Waffen AT-Bonus"             
                    )
                )

        # attribute bonus
        modifier = ValueModifier(additive = (creature.attribute.get(weapon.attack_attribute)-8)//3 )
        if not modifier.is_neutral:
            contributions.append(
                ModifierContribution(
                modifier = modifier,   
                source_name = "Attributsbonus",
                source = creature,
                description = "{:}-Bonus".format(weapon.attack_attribute)             
                )
            )
        return contributions


class ParryValue(DerivedValue):
    name = "PA"
    value_type = ValueId.PARRY
    minimum = 0

    def __init__(
        self,
        creature: "Creature",
        weapon: "MeleeWeapon",
    ):
        super().__init__(creature)
        self.weapon = weapon



    @property
    def calculate(self) -> int:
        return self.creature.weapon_skills[self.weapon.type]//2

    def standard_query(self) -> ModifierQuery:
        return ModifierQuery(
            value_type=self.value_type,
            actor=self.creature,
            subject=self.weapon,
        )
    
    def modifications(self, query: ModifierQuery | None = None) -> list[ModifierContribution]:
        query = query or self.standard_query
        weapon = query.weapon
        creature = query.creature

        # status effects
        contributions = StatusModifierResolver.resolve(query)

        # weapon it self
        if isinstance(weapon, MeleeWeapon):
            modifier = ValueModifier(additive = weapon.parry_modifier)
            if not modifier.is_neutral:
                contributions.append(
                    ModifierContribution(
                    modifier = modifier,   
                    source_name = "Paradebonus",
                    source = weapon,
                    description = "Waffen PA-Bonus"             
                    )
                )

        # attribute bonus
        attribute_name = max(weapon.damage_attributes, key=weapon.damage_attributes.get)
        modifier = ValueModifier(additive = (creature.attribute.get(attribute_name, 8) - 8) // 3 )
        if not modifier.is_neutral:
            contributions.append(
                ModifierContribution(
                modifier = modifier,   
                source_name = "Attributsbonus",
                source = creature,
                description = "{:}-Bonus".format(attribute_name)             
                )
            )
        return contributions

@dataclass
class DamageBonus: #TBD
    attributes: list[str] = field(default_factory=list)
    threshold: int | None = None

