from dataclasses import dataclass, field
from enum import Enum, auto
import random
from dataclasses import dataclass
from typing import ClassVar
import json



#__ATTRIBUTES________________________________________________________________________________

class Attribute(Enum):
    MU = "MU"
    KL = "KL"
    IN = "IN"
    CH = "CH"
    FF = "FF"
    GE = "GE"
    KO = "KO"
    KK = "KK"



#__TALENTS________________________________________________________________________________

@dataclass(frozen=True)
class TalentDefinition:
    name: str
    attributes: tuple[Attribute, Attribute, Attribute]
    category: str
    tags: frozenset[str]

    _definitions: ClassVar[dict[str, "TalentDefinition"] | None] = None

    @classmethod
    def load_all(cls) -> None:
        if cls._definitions is not None:
            return

        with open("data/talents.json", encoding="utf-8") as f:
            raw_data = json.load(f)

        cls._definitions = {
            name: cls(
                name=name,
                attributes=tuple(Attribute[a] for a in data["attributes"]),
                category=data["category"],
                tags=frozenset(data.get("tags", [])),
            )
            for name, data in raw_data.items()
        }

    @classmethod
    def get(cls, name: str) -> "TalentDefinition":
        cls.load_all()

        if cls._definitions is None:
            raise RuntimeError("Talent definitions were not loaded")

        if name not in cls._definitions:
            raise KeyError(f"Unbekanntes Talent: {name}")

        return cls._definitions[name]

    @classmethod
    def all(cls) -> dict[str, "TalentDefinition"]:
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

class DerivedValue:
    name: str = ""
    maximum: int | float = float("inf")
    minimum: int | float = -float("inf")

    def __init__(self, creature, base: int | None = None):
        self.creature = creature
        if base is None:
            self.base = self.calculate
        else:
            self.base = base

    @property
    def calculate(self):
        return 0

    @property
    def current(self):
        additive = 0
        multiplier = 1.

        for effect in self.creature.status_effects.values():
            modifier = effect.get_modifier(self)
            additive += modifier.additive
            multiplier += modifier.multiplicative

        current_value = (self.base + additive) * multiplier    
        return min(self.maximum, max(self.minimum, current_value))
    

    
class MovementSpeed(DerivedValue):
    name = "GS"
    minimum = 0

    @property
    def calculate(self):
        return self.creature.culture.movement_speed


class SoulPower(DerivedValue):
    name = "SK"

    @property
    def calculate(self):
        return int( self.creature.culture.soul_power + (self.creature.MU + self.creature.KL + self.creature.IN)/6. )
    
class Toughness(DerivedValue):
    name = "ZK"

    @property
    def calculate(self):
        return int( self.creature.culture.toughness + (self.creature.KO + self.creature.KO + self.creature.KK)/6. )


class Initiative(DerivedValue):
    name = "INI"
    minimum = 0
    bonus: int = 0

    def __init__(self, creature, base: int | None = None):
        self.creature = creature
        if base is None:
            self.base_flat = self.calculate
        else:
            self.base_flat = base
    
    @property
    def base(self):
        return self.base_flat + self.bonus

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
    amount: int
    type: DamageType

@dataclass
class DamageBonus: #TBD
    attributes: list[str] = field(default_factory=list)
    threshold: int | None = None

@dataclass #TBD
class AttackValue:
    attributes: list[str] = field(default_factory=list)
    threshold: int | None = None

@dataclass #TBD
class Parry:
    attributes: list[str] = field(default_factory=list)
    threshold: int | None = None
