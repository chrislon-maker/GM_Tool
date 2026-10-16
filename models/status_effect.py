from __future__ import annotations  # treat type hints as strings
from typing import TYPE_CHECKING

# import classes for type checking
#if TYPE_CHECKING:
#    from models.properties import Parry

from models.properties import TalentTag
from models.modifiers import ConditionCheck, ValueModifier, ModifierQuery, ModifierContribution
from models.enums import *

from dataclasses import dataclass, field
from typing import ClassVar, Callable


class StatusModifierResolver:
    '''
    Collects the ModifierContributions of all StatusEffect instances into a list 
    '''
    @staticmethod
    def resolve(query: ModifierQuery) -> list[ModifierContribution]:

        contributions: list[ModifierContribution] = []

        for effect in query.creature.status_effects:
            modifier = effect.get_modifier(query)

            if not modifier.is_neutral:
                contributions.append(
                    ModifierContribution(
                    modifier=modifier,
                    source_name = effect.name,
                    source = effect,
                    description = "{0:} {1:}".format(effect.name, effect.level)
                    )
                )

        return contributions
    

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
        TalentTag.FLYING,
        TalentTag.JUGGLING,
        TalentTag.CLIMBING,
        TalentTag.BODY_CONTROL,
        TalentTag.FEAT_OF_STRENGTH,
        TalentTag.RIDING,
        TalentTag.SWIMMING,
        TalentTag.DANCING,
        TalentTag.PICKPOCKETING,
        TalentTag.STEALTH,
        TalentTag.TRACKING,
        TalentTag.ZOOLOGY,
        TalentTag.SURVIVAL,
        TalentTag.ALCHEMY,
        TalentTag.SEEFARING,
        TalentTag.VEHICLES,
        TalentTag.MEDICINE_POISSON,
        TalentTag.MEDICINE_DISEASE,
        TalentTag.MEDICINE_WOUNDS,
        TalentTag.WOOD_CRAFTING,
        TalentTag.COOKING,
        TalentTag.FURRIER,
        TalentTag.PAINTING,
        TalentTag.BLACKSMITHING,
        TalentTag.MUSIC,
        TalentTag.PICKPOCKETING,
        TalentTag.STONE_MASONRY,
        TalentTag.TAYLORING
        ]

    # modifies a current value of some derived property
    def get_modifier(self, query: ModifierQuery) -> ValueModifier:
        affected_values = {
            ValueType.MOVEMENT_SPEED,
            ValueType.INITIATIVE,
            ValueType.EVASION,
            ValueType.PARRY,
            ValueType.MELEE_ATTACK
        }

        if query.value_type in affected_values:
            return ValueModifier(additive=-self.level)
        
        if query.value_type is ValueType.TALENT_CHECK and query.subject.name in self.affected_talents:
            return ValueModifier(additive=-self.level)

        return ValueModifier()
         

@dataclass
class Pain(StatusEffect):
    name: str = "Schmerz"
    affected_talents: str = "all"

    # modifies a current value of some derived property
    def get_modifier(self, query: ModifierQuery) -> ValueModifier:
        if query.value_type in [
                ValueType.TALENT_CHECK,
                ValueType.MELEE_ATTACK,
                ValueType.MELEE_ATTACK,
                ValueType.MOVEMENT_SPEED,
                ValueType.PARRY,
                ValueType.DODGE
            ]:
            return ValueModifier(additive=-self.level)

        return ValueModifier()
    

@dataclass
class Blind(StatusEffect):
    name: str = "Blind"
    affected_talents: str = "all"

    # modifies a current value of some derived property
    def get_modifier(self, query: ModifierQuery) -> ValueModifier:
        if self.level < 4:
            if query.value_type in [
                ValueType.TALENT_CHECK,
                ValueType.MELEE_ATTACK,
                ValueType.DEFENSE,
                ValueType.PARRY,
                ValueType.DODGE
            ]:
                return ValueModifier(additive=-self.level)
            
            if query.value_type in [
                ValueType.RANGED_ATTACK
            ]:
                return ValueModifier(additive=-2*self.level)
        else:
            if query.value_type is ValueType.MELEE_ATTACK:
                return ValueModifier(additive=0, multiplicative=0.5)
            
            if query.value_type in [
                ValueType.RANGED_ATTACK,
                ValueType.DEFENSE,
                ValueType.PARRY,
                ValueType.DODGE
            ]:
                return ValueModifier(additive=0, multiplicative=0.)

        return ValueModifier()
    

@dataclass
class Fear(StatusEffect):
    name: str = "Furcht"
    affected_talents: str = "all"

    # modifies a current value of some derived property
    def get_modifier(self, query: ModifierQuery) -> ValueModifier:
        if query.value_type is ValueType.TALENT_CHECK:
            return ValueModifier(additive=-self.level)

        return ValueModifier()


@dataclass
class Confusion(StatusEffect):
    name: str = "Verwirrung"
    affected_talents: str = "all"

    # modifies a current value of some derived property
    def get_modifier(self, query: ModifierQuery) -> ValueModifier:
        if query.value_type is ValueType.TALENT_CHECK:
            return ValueModifier(additive=-self.level)

        return ValueModifier()
    

@dataclass
class Stun(StatusEffect):
    name: str = "Betäubung"
    affected_talents: str = "all"

    # modifies a current value of some derived property
    def get_modifier(self, query: ModifierQuery) -> ValueModifier:
        if query.value_type is ValueType.TALENT_CHECK:
            return ValueModifier(additive=-self.level)

        return ValueModifier()


@dataclass
class Paralysis(StatusEffect):
    name: str = "Paralyse"

    # modifies a current value of some derived property
    def get_modifier(self, query: ModifierQuery) -> ValueModifier:
        if query.value_type is ValueType.MOVEMENT_SPEED:
            return ValueModifier(multiplicative=-0.25*self.level)

        if query.value_type is ValueType.TALENT_CHECK and not set([ModifierTag.MOVEMENT, ModifierTag.SPEECH]).isdisjoint(query.subject.tags):
            return ValueModifier(additive=-self.level)
        
        return ValueModifier()
    

@dataclass
class Confined(StatusEffect):
    name: str = "Eingeengt"

    # modifies a current value of some derived property
    def get_modifier(self, query: ModifierQuery) -> ValueModifier:

        if query.value_type in [ValueType.MELEE_ATTACK, ValueType.PARRY]:
            weapon = query.subject
            if weapon.type is WeaponType.SHIELD:
                return ValueModifier(additive= -2 * (weapon.size + 1))
            
            return ValueModifier(additive= -4 * weapon.range )
        
        return ValueModifier()

