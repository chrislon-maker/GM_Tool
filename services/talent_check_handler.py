from models.properties import TalentDefinition
from models.enums import ValueType, Attribute, TalentTag, SpellTag
from models.status_effect import StatusModifierResolver, ModifierQuery, ValueModifier, ModifierContribution

from models.creature import Creature

from dataclasses import dataclass, field
import numpy as np
import random

@dataclass
class CheckResult:
    check_type: ValueType | None = None
    check_name: str = ""
    target: int = 0
    roll: int = 0
    remaining: int = 0
    crit: bool = False
    modifier: list[ModifierContribution]
    success: bool = False

@dataclass
class SkillCheckResult(CheckResult):
    check_type: ValueType = ValueType.TALENT_CHECK
    attributes: dict[Attribute, int] = []
    roll: dict[Attribute, int] = []
    quality_level: int = 0


@dataclass
class TalentCheckContext:
    name: TalentTag | SpellTag = None
    value_type: ValueType | None = None
    actor: Creature | None = None
    subject: object | None = None
    modifier: ValueModifier | None = None


class TalentCheckHandler:
    def __init__(self, context: TalentCheckContext):
        self.context = context
        self.subject = context.subject 


    def quality_level(self, fp_left: int) -> int:
        """
        Berechnet die QS aus dem FW; max QS 6, min QS 1

        Args:
            FW (int): Fähigkeitswert/Fähigkeitspunkte die nach einer Probe noch übrig sind.

        Returns:
            QS 
        """
        return max(0, min(6, (fp_left + 2) // 3))


    def get_modifiers(self) -> list[ModifierContribution]:

        # modification due to status effects
        query = ModifierQuery(
            value_type = self.context.value_type,   
            actor = self.context.actor,         
            subject = self.subject
        )

        modifier_contributions = StatusModifierResolver.resolve(query)

        return modifier_contributions
    
    
    def get_target_value(self) -> int:
        # character talent value
        if self.context.value_type is ValueType.TALENT_CHECK:
            if self.subject.name in self.creature.talents.keys():
                return self.creature.talents[self.subject.name]
            return 0
        elif self.context.value_type is ValueType.SPELL_CHECK:
            return self.creature.spells[self.subject.name]
        
    
    def get_relevant_attributes(self) -> dict[Attribute, int]:
        # Attribute
        relevant_attributes = {}
        for attribute in self.subject.attributes:
            relevant_attributes[attribute] = self.creature.attributes[attribute]
        return relevant_attributes


    def resolve(self) -> CheckResult:

        # modifiers
        modifier_contributions = self.get_modifiers()

        modifier = ValueModifier()
        for contribution in modifier_contributions:
            modifier = modifier.combine(contribution.modifier)

        # get target value
        target_value = self.get_target_value()

        # get relevant attributes
        relevant_attributes = self.get_relevant_attributes()

        # roll the dice
        roll = [random.randint(1, 20) for _ in range(3)]

        exceeded = sum( 
            max(0, roll[i] - modifier.apply(attribute) )  
            for i, attribute in enumerate(relevant_attributes.values())  
            )
        

        remaining = target_value - exceeded

        return SkillCheckResult(
            check_name = self.context.name,
            attributes = relevant_attributes,
            target = target_value,
            roll = roll,
            remaining = remaining,
            crit = self.check_on_crit(roll),
            quality_level = self.quality_level(remaining),
            modifier = modifier_contributions,
            success = remaining >= 0
        )


    def check_on_crit(roll):
        result = max( 
            sum( 1 for number in roll if number == 1),
            sum( 1 for number in roll if number == 20)
            )
        return result > 1
    




