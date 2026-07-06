from dataclasses import dataclass, field
import re, random

@dataclass
class DamageBonus:
    attributes: list[str] = field(default_factory=list)
    threshold: int | None = None

@dataclass
class Weapon:
    name: str = ""
    damage_formula: str = ""    # 2W6 + 4
    weight: float | None = None
    price: str | None = None
    complexity: str | None = None
    weapon_advantage: str = ""
    weapon_disadvantage: str = ""
    length: str = ""

    def roll_damage(self) -> int:
        formula = self.damage_formula.replace(" ", "")

        if "+" in formula:
            dice, flat = formula.split("+")
            flat = int(flat)
        else:
            dice = formula
            flat = 0

        number, sides = dice.split("W")
        return sum(random.randint(1, int(sides)) for _ in range(int(number))) + int(flat)


@dataclass
class Meele_Weapon(Weapon):
    attack_modifier: int | None = None
    parry_modifier: int | None = None
    attribute_bonus: DamageBonus = field(default_factory=DamageBonus)
    reach: str = ""

@dataclass
class Ranged_Weapon(Weapon):
    loading_period: int | None = None
    distance: list[int]
    munition: str | None = None

