from dataclasses import dataclass, field
from typing import Callable


#__CONDITIONS AND COUNTERS_____________________________________________________________________

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


#__STATUS EFFECTS_____________________________________________________________________

@dataclass
class ValueModifier:
    additive: int = 0
    multiplicative: float = 0.0


@dataclass
class Encumbrance:
    name: str = "Belastung"

    affected_talents: list[str] = [
        "Fliegen",
        "Gaukeleien",
        "Klettern",
        "Körperbeherrschung",
        "Kraftakt",
        "Reiten",
        "Schwimmen",
        "Tanzen",
        "Taschendiebstahl",
        "Verbergen",
        "Fährtensuchen",
        "Tierkunde",
        "Wildnisleben",
        "Alchemie",
        "Boote & Schiffe",
        "Fahrzeuge",
        "Heilkunde Gift",
        "Heilkunde Krankheiten",
        "Heilkunde Wunden",
        "Holzbearbeitung",
        "Lebensmittelverarbeitung",
        "Lederverarbeitung",
        "Malen & Zeichnen",
        "Metallbearbeitung",
        "Musizieren",
        "Schlösserknacken",
        "Steinbearbeitung",
        "Stoffbearbeitung"
        ]
    
    removal_condition: ConditionCheck | None = None

    def is_valid(self):
        if self.removal_condition is None:
            return True
        return self.removal_condition.is_valid()

    # modifies a current value of some derived property
    def get_modifier(self, property) -> ValueModifier:
        if isinstance(property, MovementSpeed):
            return ValueModifier(additive=-1)

        if isinstance(property, Initiative):
            return ValueModifier(additive=-1)
        
        if isinstance(property, Evasion):
            return ValueModifier(additive=-1)
        
        if isinstance(property, AttackValue):
            return ValueModifier(additive=-1)
        
        if isinstance(property, Parry):
            return ValueModifier(additive=-1)
        
        if isinstance(property, TalentDefinition) and property.name in self.affected_talents:
            return ValueModifier(additive=-1)

        return ValueModifier()
         

@dataclass
class Pain:
    name = "Schmerz"
    affected_talents: str = "all"
    removal_condition: ConditionCheck | None = None

    def is_valid(self):
        if self.removal_condition is None:
            return True
        return self.removal_condition.is_valid()

    # modifies a current value of some derived property
    def get_modifier(self, property) -> ValueModifier:
        if isinstance(property, MovementSpeed):
            return ValueModifier(additive=-1)

        if isinstance(property, TalentDefinition):
            return ValueModifier(additive=-1)

        return ValueModifier()
    

@dataclass
class Fear:
    name = "Furcht"
    affected_talents: str = "all"
    removal_condition: ConditionCheck | None = None

    def is_valid(self):
        if self.removal_condition is None:
            return True
        return self.removal_condition.is_valid()

    # modifies a current value of some derived property
    def get_modifier(self, property) -> ValueModifier:
        if isinstance(property, TalentDefinition):
            return ValueModifier(additive=-1)

        return ValueModifier()


@dataclass
class Confusion:
    name = "Verwirrung"
    affected_talents: str = "all"
    removal_condition: ConditionCheck | None = None

    def is_valid(self):
        if self.removal_condition is None:
            return True
        return self.removal_condition.is_valid()

    # modifies a current value of some derived property
    def get_modifier(self, property) -> ValueModifier:
        if isinstance(property, TalentDefinition):
            return ValueModifier(additive=-1)

        return ValueModifier()
    

@dataclass
class Stun:
    name = "Betäubung"
    affected_talents: str = "all"
    removal_condition: ConditionCheck | None = None

    def is_valid(self):
        if self.removal_condition is None:
            return True
        return self.removal_condition.is_valid()

    # modifies a current value of some derived property
    def get_modifier(self, property) -> ValueModifier:
        if isinstance(property, TalentDefinition):
            return ValueModifier(additive=-1)

        return ValueModifier()


@dataclass
class Paralysis:
    name = "Paralyse"
    affected_talents: list[str] = ["movement", "speech"]
    removal_condition: ConditionCheck | None = None

    def is_valid(self):
        if self.removal_condition is None:
            return True
        return self.removal_condition.is_valid()

    # modifies a current value of some derived property
    def get_modifier(self, property) -> ValueModifier:
        if isinstance(property, MovementSpeed):
            return ValueModifier(multiplicative=-0.25)

        if isinstance(property, TalentDefinition) and not set(self.affected_talents).isdisjoint(property.tags):
            return ValueModifier(additive=-1)
        
        return ValueModifier()

