from dataclasses import dataclass, field
from typing import ClassVar
from models.status_effect import StatusEffect, Pain, Confusion, Encumbrance, Paralysis, Fear, Stun
from models.properties import TalentDefinition, Attribute
from models.creature import Creature
import numpy as np
import random
import json


class ActionBlockedError(Exception):
    pass


def quality_level(fp_left: int) -> int:
    """
    Berechnet die QS aus dem FW; max QS 6, min QS 1

    Args:
        FW (int): Fähigkeitswert/Fähigkeitspunkte die nach einer Probe noch übrig sind.

    Returns:
        QS 
    """
    return max(0, min(6, (fp_left + 2) // 3))



def skill_check(creature: Creature, talent_name: str) -> int:
    """
    Führt eine Probe auf das angegebene Talent aus.
    Gibt sowohl die Attribute auf die gewürfelt wird als auch die Attributswerte den FW des Charakters aus.
    Gibt anschließend die QS der Probe und informiert über krittische Erfolge und Fehlschläge.

    Args:
        probe (str): Talent auf das gewürfelt werden soll.
        mod (int): Modifikation der Probe. Negative Werte entsprechen einer Erschwerniss.
    """

    talent = TalentDefinition.get[talent_name]

    # modification due to status effects
    netto_mod = 0
    for status_effect in creature.status_effects:
        netto_mod += status_effect.get_modifier(talent).additive
    
    # character talent value
    if talent.name in creature.talents.keys():
        talent_value = creature.talents[talent.name]
    else:
        talent_value = 0

    # roll the dice
    roll = np.array([random.randint(1, 20) for _ in range(3)])

    # Attribute
    attributes = np.array([creature.attributes[attribute] for attribute in talent.attributes])
    #attributes = np.array([ creature.attributes[attribute] for attribute in talent.attributes ])
    #attributes = np.array([getattr(self, attribute) for attribute in talents.get(talent)])

    diff = (roll - netto_mod) - attributes
    remaining = talent_value - sum(diff[diff > 0])

    print('{0:} würfelt eine Probe auf {1:} mit einer Erschwerniss von {2:}.'.format(creature.name, talent.name, netto_mod))
    print("{0:}'s FW ist {1:}.".format(creature.name, talent_value))
    print('Die relevanten Atribute sind {0:}/{1:}/{2:} = {3:}/{4:}/{5:}'.format(talent["attributes"][0], talent["attributes"][1], talent["attributes"][2], attributes[0], attributes[1], attributes[2]))
    print('Die Würfel zeigen: {0:} - {1:} - {2:}'.format(roll[0], roll[1], roll[2]))
    
    return quality_level(remaining)



def check_on_crit(roll):
    if isinstance(roll, list):
        if np.sum(roll == 1) == 2:
            return 1

        if np.sum(roll == 1) == 3:
            return 2

        if np.sum(roll == 20) == 2:
            return -1

        if np.sum(roll == 20) == 3:
            return -2
    elif roll == 1:
        return 1
