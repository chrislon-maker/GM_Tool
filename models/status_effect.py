from __future__ import annotations  # treat type hints as strings
from typing import TYPE_CHECKING

# import classes for type checking
#if TYPE_CHECKING:
#    from models.properties import Parry

from models.properties import TalentDefinition, TalentTag, MovementSpeed, Initiative, Evasion, Parry, AttackValue
from models.enums import *

from dataclasses import dataclass, field
from typing import ClassVar, Callable


#__CONDITIONS AND COUNTERS_____________________________________________________________________

class Counter:
    '''
    Holds an integer which can be increased and decreases
    '''
    def __init__(self, value: int = 0):
        self.value = value

    def set_to(self, value: int = 0):
        self.value = value

    def increase(self, amount: int = 1):
        self.value += amount

    def decrease(self, amount: int = 1):
        self.value -= amount


class RoundCounter(Counter):
    def tick_round(self):
        self.increase()



@dataclass
class ConditionCheck:
    '''
    Checks whether a value defined by check_value() is within minimum and maximum
    '''
    minimum: int | None = None
    maximum: int | None = None 

    @property
    def check_value(self):
        raise NotImplementedError
    
    def is_valid(self) -> bool:
        value = self.check_value

        if self.minimum is not None and value < self.minimum:
            return False

        if self.maximum is not None and value >= self.maximum:
            return False

        return True


class RoundCondition(ConditionCheck):
    '''
    Like a ConditionCheck but with a tick-function to incrementally increase the stored value. 
    Standard case: value is increased every round until maximum number or rounds (maximum) is exceeded
    '''
    def __init__(self, initial_count: int = 0, expiration: int | None = None, initialization: int | None = None):
        super().__init__(minimum=initialization, maximum=expiration)
        self.counter = RoundCounter(initial_count)

    @property
    def check_value(self):
        return self.counter.value

    def tick_round(self):
        self.counter.tick_round()


class ValueCondition(ConditionCheck):
    '''
    Like a ConditionCheck but wich the stored value being linked to some dynamic resource.
    Standard case: the resource is the life-points of a creature and the condition is valid as long as that value is within a certian range 
    '''
    def __init__(self, resource, minimum: int | None = None, maximum: int | None = None):
        super().__init__(minimum=minimum, maximum=maximum)
        self.resource = resource

    @property
    def check_value(self):
        return self.resource.current
    

@dataclass
class DependentCondition(ConditionCheck):
    '''
    Validity depents on validity of an other object
    Call:   DependentCondition(myarmor.is_worn)    for normal method
    Call:   DependentCondition(lambda: myarmor.is_worn)    for @property
    Call:   DependentCondition(lambda: creature.LeP.current < 0.75*creature.LeP.maximum)   
    '''

    def __init__(self, dependence: Callable[[], bool]):
        self.dependence = dependence
    
    def is_valid(self) -> bool:
        return self.dependence()


#__VALUE MODIFICATIONS_________________________________________________________________________

@dataclass(frozen=True)
class ValueModifier:
    '''
    Handels a modifier that can be applied to a value
    '''
    additive: int = 0
    multiplicative: float = 1.0

    @property
    def is_neutral(self) -> bool:
        return (self.additive == 0 and self.multiplicative == 1.)

    def apply(self, value: int) -> int:
        return int((value + self.additive) * self.multiplicative)
    
    def combine(self, modifier: ValueModifier) -> ValueModifier:
        return ValueModifier(
            additive = self.additive + modifier.additive,
            multiplicative = self.multiplicative * modifier.multiplicative
            )
    

@dataclass(frozen=True)
class ModifierContribution:
    '''
    Holds a ValueModifier and additional information about it like its source and a description for GUI
    '''
    modifier: ValueModifier
    source_name: str
    source: object | None = None
    description: str | None = None


@dataclass(frozen=True)
class ModifierQuery:
    '''
    Holds all information about the value which is to be modified.
    Used e.g. by the StatusEffect classes which require these information to calculate the correct ValueModifier 
    '''
    value_type: ValueType   # value to be modified
    actor: Creature         # creature that value belongs to
    tags: frozenset[ModifierTag] = frozenset()  # general tags and categories
    subject: object | None = None       # Talent, Weapon usw. 
    context: object | None = None       # context



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
            ValueType.MEELE_ATTACK
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
                ValueType.MEELE_ATTACK,
                ValueType.MEELE_ATTACK,
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
                ValueType.MEELE_ATTACK,
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
            if query.value_type is ValueType.MEELE_ATTACK:
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

        if query.value_type in [ValueType.MEELE_ATTACK, ValueType.PARRY]:
            weapon = query.subject
            if weapon.type is WeaponType.SHIELD:
                return ValueModifier(additive= -2 * (weapon.size + 1))
            
            return ValueModifier(additive= -4 * weapon.range )
        
        return ValueModifier()

