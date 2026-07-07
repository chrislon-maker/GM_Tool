from dataclasses import dataclass, field
from models.talents import TalentDefinition
from typing import ClassVar, Callable

#__CONDITIONS AND COUNTERS_____________________________________________________________________

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


class Counter:
    '''
    Holds an integer which can be increased and decreases
    '''
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


#__STATUS EFFECTS_____________________________________________________________________

@dataclass
class ValueModifier:
    additive: int = 0
    multiplicative: float = 0.0


@dataclass
class StatusEffect:
    name: str = ""
    removal_conditions: list[ConditionCheck] = field(default_factory=list)

    @property
    def level(self) -> int:
        return len(self.removal_conditions)
    
    def check_validity(self):
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

    # modifies a current value of some derived property
    def get_modifier(self, property) -> ValueModifier:
        if isinstance(property, MovementSpeed):
            return ValueModifier(additive=-self.level)

        if isinstance(property, Initiative):
            return ValueModifier(additive=-self.level)
        
        if isinstance(property, Evasion):
            return ValueModifier(additive=-self.level)
        
        if isinstance(property, AttackValue):
            return ValueModifier(additive=-self.level)
        
        if isinstance(property, Parry):
            return ValueModifier(additive=-self.level)
        
        if isinstance(property, TalentDefinition) and property.name in self.affected_talents:
            return ValueModifier(additive=-self.level)

        return ValueModifier()
         

@dataclass
class Pain(StatusEffect):
    name = "Schmerz"
    affected_talents: str = "all"

    # modifies a current value of some derived property
    def get_modifier(self, property) -> ValueModifier:
        if isinstance(property, MovementSpeed):
            return ValueModifier(additive=-self.level)

        if isinstance(property, TalentDefinition):
            return ValueModifier(additive=-self.level)

        return ValueModifier()
    

@dataclass
class Fear(StatusEffect):
    name = "Furcht"
    affected_talents: str = "all"

    # modifies a current value of some derived property
    def get_modifier(self, property) -> ValueModifier:
        if isinstance(property, TalentDefinition):
            return ValueModifier(additive=-self.level)

        return ValueModifier()


@dataclass
class Confusion(StatusEffect):
    name = "Verwirrung"
    affected_talents: str = "all"

    # modifies a current value of some derived property
    def get_modifier(self, property) -> ValueModifier:
        if isinstance(property, TalentDefinition):
            return ValueModifier(additive=-self.level)

        return ValueModifier()
    

@dataclass
class Stun(StatusEffect):
    name = "Betäubung"
    affected_talents: str = "all"
    removal_condition: ConditionCheck | None = None

    # modifies a current value of some derived property
    def get_modifier(self, property) -> ValueModifier:
        if isinstance(property, TalentDefinition):
            return ValueModifier(additive=-self.level)

        return ValueModifier()


@dataclass
class Paralysis(StatusEffect):
    name = "Paralyse"
    affected_talents: ClassVar[list[str]] = ["movement", "speech"]

    # modifies a current value of some derived property
    def get_modifier(self, property) -> ValueModifier:
        if isinstance(property, MovementSpeed):
            return ValueModifier(multiplicative=-0.25*self.level)

        if isinstance(property, TalentDefinition) and not set(self.affected_talents).isdisjoint(property.tags):
            return ValueModifier(additive=-self.level)
        
        return ValueModifier()

