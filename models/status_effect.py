from dataclasses import dataclass, field
from typing import Callable

@dataclass
class ConditionCheck:
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

class Counter:
    def __init__(self, value: int = 0):
        self.value = value

    def increase(self, amount: int = 1):
        self.value += amount

    def decrease(self, amount: int = 1):
        self.value -= amount

class RoundCounter(Counter):
    def tick_round(self):
        self.increase()


class RoundCondition(ConditionCheck):
    def __init__(self, initial_count: int = 0, expiration: int | None = None, initialization: int | None = None):
        super().__init__(minimum=initialization, maximum=expiration)
        self.counter = RoundCounter(initial_count)

    @property
    def check_value(self):
        return self.counter.value

    def tick_round(self):
        self.counter.tick_round()


class ValueCondition(ConditionCheck):
    def __init__(self, resource, minimum: int | None = None, maximum: int | None = None):
        super().__init__(minimum=minimum, maximum=maximum)
        self.resource = resource

    @property
    def check_value(self):
        return self.resource.current



@dataclass
class StatusEffect:
    name: str = ""

    source: str = ""

    affected_check_types: set[str] = set()
    affected_attributes: set[str] = set()
    affected_talents: set[str] = set()

    removal_condition: ConditionCheck | None = None

    def is_valid(self):
        if self.removal_condition is not None:
            return self.removal_condition.is_valid()
        return False

    def get_modifier(self, check_context) -> int:
        return 0

    


class Pain(StatusEffect):
    name = "Schemerz"

    def modify_check(self, ctx, modifier):
        return modifier - self.level

    def modify_derived_value(self, name, value):
        if name == "GS":
            return value - self.level
        return value
    
class Fear(StatusEffect):
    name = "Furcht"

    def modify_check(self, ctx, modifier):
        return modifier - self.level

    def modify_derived_value(self, name, value):
        if name == "GS":
            return value - self.level
        return value
    
class Stun(StatusEffect):
    name = "Betäubung"

    def modify_check(self, ctx, modifier):
        return modifier - self.level

    def modify_derived_value(self, name, value):
        if name == "GS":
            return value - self.level
        return value
    
class Confusion(StatusEffect):
    name = "Verwirrung"

    def modify_check(self, ctx, modifier):
        return modifier - self.level

    def modify_derived_value(self, name, value):
        if name == "GS":
            return value - self.level
        return value
    
class Encumbrance(StatusEffect):
    name = "Belastung"

    def modify_check(self, ctx, modifier):
        return modifier - self.level

    def modify_derived_value(self, name, value):
        if name == "GS":
            return value - self.level
        return value


class Paralysis(StatusEffect):
    name = "Paralyse"

    def modify_check(self, ctx, modifier):
        if ctx.requires_movement or ctx.requires_speech:
            return modifier - self.level
        return modifier

    def modify_derived_value(self, name, value):
        if name == "GS":
            return int(value * [1, 0.75, 0.5, 0.25][self.level])
        return value