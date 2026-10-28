from __future__ import annotations  # treat type hints as strings
from typing import TYPE_CHECKING

# import classes for type checking
#if TYPE_CHECKING:
#    from models.properties import Parry

from models.properties import TalentId, TalentDefinition
from models.modifiers import ConditionCheck, ValueModifier, DerivedValue, ModifierQuery, ModifierContribution
from models.enums import *

from dataclasses import dataclass, field
from typing import ClassVar, Callable
    

#__STATUS EFFECTS__________________________________________________________________________________

@dataclass
class StatusEffect:
    name: str = ""
    removal_conditions: list[ConditionCheck] = field(default_factory=list)

    @property
    def level(self) -> int:
        self.update()
        return len(self.removal_conditions)
    
    def update(self) -> int:
        self.removal_conditions = [
            condition
            for condition in self.removal_conditions
            if condition.is_valid()
        ]

    @property
    def is_valid(self):
        return self.level > 0


@dataclass
class Encumbrance(StatusEffect):
    name: str = "Belastung"

    affected_talents: ClassVar[list[str]] = [
        TalentId.FLYING,
        TalentId.JUGGLING,
        TalentId.CLIMBING,
        TalentId.BODY_CONTROL,
        TalentId.FEAT_OF_STRENGTH,
        TalentId.RIDING,
        TalentId.SWIMMING,
        TalentId.DANCING,
        TalentId.PICKPOCKETING,
        TalentId.STEALTH,
        TalentId.TRACKING,
        TalentId.ZOOLOGY,
        TalentId.SURVIVAL,
        TalentId.ALCHEMY,
        TalentId.SEEFARING,
        TalentId.VEHICLES,
        TalentId.MEDICINE_POISSON,
        TalentId.MEDICINE_DISEASE,
        TalentId.MEDICINE_WOUNDS,
        TalentId.WOOD_CRAFTING,
        TalentId.COOKING,
        TalentId.FURRIER,
        TalentId.PAINTING,
        TalentId.BLACKSMITHING,
        TalentId.MUSIC,
        TalentId.PICKPOCKETING,
        TalentId.STONE_MASONRY,
        TalentId.TAYLORING
        ]

    affected_values = {
                ValueId.MOVEMENT_SPEED,
                ValueId.INITIATIVE,
                ValueId.DODGE,
                ValueId.PARRY,
                ValueId.MELEE_ATTACK
            }

    # modifies a current value of some derived property
    def get_modifier(self, target) -> ValueModifier:

        if isinstance(target, DerivedValue): 
            if target.ValueId in self.affected_values:
                return ValueModifier(additive=-self.level)
        
        elif isinstance(target, TalentDefinition):
            if target.name in self.affected_talents:
                return ValueModifier(additive=-self.level)

        return ValueModifier()
         

@dataclass
class Pain(StatusEffect):
    name: str = "Schmerz"
    affected_talents: str = "all"
    affected_values = {
                ValueId.MELEE_ATTACK,
                ValueId.MOVEMENT_SPEED,
                ValueId.PARRY,
                ValueId.DODGE
            }

    # modifies a current value of some derived property
    def get_modifier(self, target) -> ValueModifier:
        if isinstance(target, DerivedValue):
            if target.name in self.affected_values:
                return ValueModifier(additive=-self.level)
            
        elif isinstance(target, TalentDefinition):
            return ValueModifier(additive=-self.level)

        return ValueModifier()
    

@dataclass
class Blind(StatusEffect):
    name: str = "Blind"
    affected_talents: str = "all"

    # modifies a current value of some derived property
    def get_modifier(self, target) -> ValueModifier:

        if isinstance(target, TalentDefinition):
            return ValueModifier(additive=-self.level)
        
        elif isinstance(target, TalentDefinition):
            if self.level < 4:
                if target.name in [
                    ValueId.MELEE_ATTACK,
                    ValueId.DEFENSE,
                    ValueId.PARRY,
                    ValueId.DODGE
                ]:
                    return ValueModifier(additive=-self.level)
                elif target.name in [
                    ValueId.RANGED_ATTACK
                ]:
                    return ValueModifier(additive=-2*self.level)
            else: # level >= 4
                if target.name is ValueId.MELEE_ATTACK:
                    return ValueModifier(additive=0, multiplicative=0.5)
                
                if target.name in [
                    ValueId.RANGED_ATTACK,
                    ValueId.DEFENSE,
                    ValueId.PARRY,
                    ValueId.DODGE
                ]:
                    return ValueModifier(additive=0, multiplicative=0.)

        return ValueModifier()
    

@dataclass
class Fear(StatusEffect):
    name: str = "Furcht"
    affected_talents: str = "all"

    # modifies a current value of some derived property
    def get_modifier(self, target) -> ValueModifier:
        if isinstance(target, TalentDefinition):
            return ValueModifier(additive=-self.level)
        elif isinstance(target, DerivedValue):
            if target.name in [ValueId.RANGED_ATTACK,
                                ValueId.DEFENSE,
                                ValueId.PARRY,
                                ValueId.DODGE]:
                return ValueModifier(additive=-self.level)

        return ValueModifier()


@dataclass
class Confusion(StatusEffect):
    name: str = "Verwirrung"
    affected_talents: str = "all"

    # modifies a current value of some derived property
    def get_modifier(self, target) -> ValueModifier:
        if self.level < 4:
            return ValueModifier(additive=-self.level)
        else:
            if isinstance(target, TalentDefinition):
                if target.category == TalentTypes.KNOWLEDGE_TALENT:
                    return ValueModifier(additive=0., multiplicative=0.)

        return ValueModifier()
    

@dataclass
class Stun(StatusEffect):
    name: str = "Betäubung"
    affected_talents: str = "all"

    # modifies a current value of some derived property
    def get_modifier(self, target) -> ValueModifier:
        if isinstance(target, TalentDefinition):
            return ValueModifier(additive=-self.level)
        elif isinstance(target, DerivedValue):
            if target.name in [ValueId.RANGED_ATTACK,
                                ValueId.DEFENSE,
                                ValueId.PARRY,
                                ValueId.DODGE]:
                return ValueModifier(additive=-self.level)

        return ValueModifier()


@dataclass
class Paralysis(StatusEffect):
    name: str = "Paralyse"

    # modifies a current value of some derived property
    def get_modifier(self, target) -> ValueModifier:
        if isinstance(target, DerivedValue):
            if target.name is ValueId.MOVEMENT_SPEED:
                return ValueModifier(multiplicative = 1. - 0.25*self.level)

        if not set([ModifierTag.MOVEMENT, ModifierTag.SPEECH]).isdisjoint(target.tags):
            return ValueModifier(additive=-self.level)
        
        return ValueModifier()
    

@dataclass
class Confined(StatusEffect):
    name: str = "Eingeengt"

    # modifies a current value of some derived property
    def get_modifier(self, query: ModifierQuery) -> ValueModifier:

        if query.value_type in [ValueId.MELEE_ATTACK, ValueId.PARRY]:
            weapon = query.subject
            if weapon.type is WeaponType.SHIELD:
                return ValueModifier(additive= -2 * (weapon.size + 1))
            
            return ValueModifier(additive= -4 * weapon.range )
        
        return ValueModifier()

