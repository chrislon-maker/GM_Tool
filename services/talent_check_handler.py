from models.properties import TalentDefinition
from models.enums import ValueId, Attribute, TalentId, SpellTag
from models.status_effect import ModifierQuery, ValueModifier, ModifierContribution
from models.modifiers import StatusModifierResolver

from models.creature import Creature

from dataclasses import dataclass, field
import numpy as np
import random

@dataclass
class CheckResult:
    check_type: ValueId | None = None
    check_name: str = ""
    target: int = 0
    roll: int = 0
    remaining: int = 0
    crit: bool = False
    modifier: list[ModifierContribution] = field(default_factory=list)
    success: bool = False


@dataclass
class TalentCheckConditions:
    name: TalentId | None = None
    target_value: int = 0
    attributes: dict[Attribute, int] = field(default_factory=dict)
    status_effect_mods: list[ModifierContribution] = field(default_factory=list)
    external_mod: int = 0
    final_mod: ValueModifier | None = None


@dataclass
class TalentCheckResult:
    conditions: TalentCheckConditions | None = None
    roll: dict[Attribute, int] = field(default_factory=list)
    remaining: int = 0
    crit: bool = False
    success: bool = False
    quality_level: int = 0



def quality_level(fp_left: int) -> int:
    """
    Berechnet die QS aus dem FW; max QS 6, min QS 1

    Args:
        FW (int): Fähigkeitswert/Fähigkeitspunkte die nach einer Probe noch übrig sind.

    Returns:
        QS 
    """
    return max(1, min(6, (fp_left + 2) // 3))


def check_on_crit(roll):
    result = max( 
        sum( 1 for number in roll if number == 1),
        sum( 1 for number in roll if number == 20)
        )
    return result > 1



class TalentCheckHandler:
    @staticmethod
    def conditions(creature, target, external_modifier) -> TalentCheckConditions:
        # get target value (FW)
        talent_value = creature.talents[target.name]
        # get relevant attributes
        relevant_attributes = creature.get_relevant_attributes(target)
        # modifiers from status effects
        status_effect_modifier_contributions = StatusModifierResolver.resolve(creature, target)
        # overall modifier
        modifier = ValueModifier()
        for contribution in status_effect_modifier_contributions:
            modifier = modifier.combine(contribution.modifier)

        modifier = modifier.combine(ValueModifier(additive=external_modifier))
        return TalentCheckConditions(
                name = target.name,
                target_value = talent_value,
                attributes = relevant_attributes,
                status_effect_mods = status_effect_modifier_contributions,
                external_mod = external_modifier,
                final_mod = modifier
            )

    @staticmethod
    def resolve(creature, target, external_modifier) -> TalentCheckResult:
        conditions = TalentCheckHandler.conditions(creature, target, external_modifier)

        # get target value (FW)
        target_value = conditions.target_value

        # modifier
        modifier = conditions.final_mod

        # get relevant attributes
        relevant_attributes = conditions.attributes

        # roll the dice
        roll = [random.randint(1, 20) for _ in range(3)]

        exceeded = sum( 
            max(0, roll[i] - modifier.apply(attribute[1]) )  
            for i, attribute in enumerate(relevant_attributes)  
            )
        
        remaining = target_value - exceeded

        return TalentCheckResult(
            conditions = conditions,
            roll = roll,
            remaining = remaining,
            crit = check_on_crit(roll),
            success = remaining >= 0,
            quality_level = quality_level(remaining),
        )

    




