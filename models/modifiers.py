from __future__ import annotations  # treat type hints as strings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.creature import Creature

from models.enums import *

from dataclasses import dataclass, field
from typing import ClassVar, Callable


#__CONDITIONS AND COUNTERS_____________________________________________________________________

class Counter:
    '''
    Holds an integer which can be increased and decreases
    '''
    def __init__(self, value: int = 0):
        self.initial = value
        self.value = value

    def set_to(self, value: int = 0):
        self.value = value

    def increase(self, amount: int = 1):
        self.value += amount

    def decrease(self, amount: int = 1):
        self.value -= amount

    def reset(self):
        self.value = self.initial


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
    Call:   DependentCondition(lambda: myarmor.is_worn)    for bool variable
    Call:   DependentCondition(lambda: myarmor.is_worn)    for @property
    Call:   DependentCondition(lambda value=given_value: creature.LeP.current < value)   
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
    For derived values <additive> is added to it
    For talent checks <additive> is added to the attribute
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
    level: int | None = None


@dataclass(frozen=True)
class ModifierQuery:
    '''
    Holds all information about the value which is to be modified.
    Used e.g. by the StatusEffect classes which require these information to calculate the correct ValueModifier 
    '''
    value_type: ValueId   # value to be modified
    actor: Creature         # creature that value belongs to
    tags: frozenset[ModifierTag] = frozenset()  # general tags and categories
    subject: object | None = None       # Talent, Weapon usw. 
    context: object | None = None       # context


# values that are derived from stats and affected by status effects
class DerivedValue:
    name: ValueId | None = None
    maximum: int | float = float("inf")
    minimum: int | float = -float("inf")

    def __init__(self, creature, base: int | float | None = None):
        self.creature = creature
        self._base_override = base

    @property
    def base(self) -> int | float:
        if self._base_override is not None:
            return self._base_override

        return self.calculate

    @property
    def calculate(self):
        return 0
    

    def modifications(self) -> list[ModifierContribution]:
        return StatusModifierResolver.resolve(self.creature, self)
    
    @property
    def current(self):
        modifier = ValueModifier()
        for contribution in self.modifications():
            modifier = modifier.combine(contribution.modifier)
        return modifier.apply(self.base)


class StatusModifierResolver:
    '''
    Collects the ModifierContributions of all StatusEffect instances into a list 
    '''
    @staticmethod
    def resolve(creature, target) -> list[ModifierContribution]:

        contributions: list[ModifierContribution] = []

        for effect in creature.status_effects.values():
            modifier = effect.get_modifier(target)

            if not modifier.is_neutral:
                contributions.append(
                    ModifierContribution(
                    modifier = modifier,
                    source_name = effect.name,
                    source = effect,
                    level = effect.level
                    )
                )

        return contributions