from __future__ import annotations  # treat type hints as strings
from typing import TYPE_CHECKING

# import classes for type checking
if TYPE_CHECKING:
    from models.creature import Creature

from models.status_effect import DependentCondition, Encumbrance
from models.properties import Attribute
from models.enums import WeaponType, ValueType, MeeleWeaponRange, WhereEquipped, ShieldSize

from dataclasses import dataclass, field
import re, random
from enum import Enum, IntEnum, auto



class DamageType(Enum):
    PHYSICAL = auto()
    MAGICAL = auto()

@dataclass
class Damage:
    amount: int
    type: DamageType





    
#_WEPAONRY_____________________________________________________________________________________

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
    equipped_at: WhereEquipped | None = None


    @property
    def is_equipped(self) -> bool:
        return self.equipped

    def equip(self, where: WhereEquipped) -> None:
        self.equipped = True
        equipped_at = where

    def unequip(self) -> None:
        self.equipped = False


@dataclass
class MeeleWeapon(Weapon):
    attack_modifier: int = 0
    parry_modifier: int = 0

    attack_type: ValueType.MEELE_ATTACK

    attack_attribute: Attribute = Attribute.MU
    damage_attribute: dict[Attribute: int] | None = None

    range: MeeleWeaponRange | None = None
    parry_weapon_bonus: int = 0

@dataclass
class Shield(Weapon):
    type = WeaponType.SHIELD
    size: ShieldSize | None = None
    structure_points: int = 0 


@dataclass
class RangedWeapon(Weapon):
    loading_period: int | None = None
    range: list[int] = field(default_factory=list)
    munition: str | None = None

    attack_type: ValueType.RANGED_ATTACK
    



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

