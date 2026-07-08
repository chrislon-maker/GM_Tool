from dataclasses import dataclass, field

@dataclass
class Armor:
    name: str
    encumbrance: int = 0
    protection: int = 0
    worn: bool = True

    @property
    def is_worn(self) -> bool:
        return self.worn