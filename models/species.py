from dataclasses import dataclass, field

@dataclass
class Species:
    name: str = ""
    base_health: int | None = None
    soul_power: int | None = None
    toughness: int | None = None
    movement_speed: int | None = None

human = Species(name="Mensch", base_health=5, soul_power=-5, toughness=-5, movement_speed=8)
achaz = Species(name="Achaz", base_health=5, soul_power=-4, toughness=-5, movement_speed=8)
elf = Species(name="Elf", base_health=2, soul_power=-4, toughness=-6, movement_speed=8)
halfelf = Species(name="Helbelf", base_health=5, soul_power=-4, toughness=-6, movement_speed=8)
dwarf = Species(name="Zwerg", base_health=8, soul_power=-4, toughness=-4, movement_speed=6)