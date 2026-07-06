from dataclasses import dataclass, field
from models.status_effect import StatusEffect, Pain, Confusion, Encumbrance, Paralysis, Fear, Stun
import json


class ActionBlockedError(Exception):
    pass


@dataclass(frozen=True)
class TalentDefinition: 
    # Klasse hat die form eines einzelnen Talents
    name: str
    attributes: tuple[str, str, str]
    category: str
    tags: frozenset[str]

    # teilt sich aber mit allen anderen TalentDefinition Klassen die daten aller Talente
    _definitions: dict[str, "TalentDefinition"] | None = None


    @classmethod
    def load_all(cls):
        if cls._definitions is not None:
            return

        with open("data/talents.json", encoding="utf-8") as f:
            raw_data = json.load(f)

        # falls cls._definitions leer ist wird es mit TalentDefinition objekten für jedes Talent gefüllt
        cls._definitions = {
            name: cls(
                name=name,
                attributes=tuple(data["attributes"]),
                category=data["category"],
                tags=frozenset(data.get("tags", [])),
            )
            for name, data in raw_data.items()
        }

    @classmethod
    def get(cls, name: str) -> "TalentDefinition":
        cls.load_all()

        if name not in cls._definitions:
            raise KeyError(f"Unbekanntes Talent: {name}")

        return cls._definitions[name]




def quality_level(fp_left: int) -> int:
    """
    Berechnet die QS aus dem FW; max QS 6, min QS 1

    Args:
        FW (int): Fähigkeitswert/Fähigkeitspunkte die nach einer Probe noch übrig sind.

    Returns:
        QS 
    """
    return max(1, min(6, (fp_left + 2) // 3))


def get_current_derived_value(creature, name: str) -> int:
    base = creature.derived_values[name]

    if name == "GS":
        base -= creature.status_level(Pain)
        base -= creature.status_level(Encumbrance)

        paralysis = creature.status_level(Paralysis)
        if paralysis == 1:
            base *= 0.75
        elif paralysis == 2:
            base *= 0.5
        elif paralysis == 3:
            base *= 0.25
        elif paralysis >= 4:
            base = 0

    if name == "INI":
        base -= creature.status_level(Encumbrance)

    return max(0, int(base))



def get_talent_modifiers(creature, talent: TalentDefinition):
    modifiers = {}

    confusion_level = creature.status_level(Confusion)
    modifiers[Confusion] = confusion_level

    if talent.category in ["knowledge", "spell", "liturgy"] and confusion_level >= 3:
        raise ActionBlockedError(
            "Bei 3 oder mehr Stufen Verwirrung können keine Proben auf Zauber, Liturgien oder Wissenstalente mehr abgelegt werden."
            )
    
    if "encumbrance" in talent.tags:
        modifiers[Encumbrance] = creature.status_level(Encumbrance)

    if "movement" in talent.tags | "speech" in talent.tags:  
        modifiers[Paralysis] = creature.status_level(Paralysis)
    
    modifiers[Pain] = creature.status_level(Pain)
    modifiers[Fear] = creature.status_level(Fear)
    modifiers[Stun] = creature.status_level(Stun)

    return modifiers


def skill_check(creature: Creature, talent_name: str) -> int:
    """
    Führt eine Probe auf das angegebene Talent aus.
    Gibt sowohl die Attribute auf die gewürfelt wird als auch die Attributswerte den FW des Charakters aus.
    Gibt anschließend die QS der Probe und informiert über krittische Erfolge und Fehlschläge.

    Args:
        probe (str): Talent auf das gewürfelt werden soll.
        mod (int): Modifikation der Probe. Negative Werte entsprechen einer Erschwerniss.
    """

    talent = TalentDefinition.get(talent_name)

    # MALI DURCH STATUSEFFEKTE
    try:
        # information about which status effect contributed how much
        modifiers = get_talent_modifiers(creature, talent)
    except ActionBlockedError as e:
        print(e)

    netto_mod = sum( modifiers[key] for key in modifiers.keys() )

    # CHARAKTERWERTE
    if talent_name in creature.talents.keys():
        # Fähigkeitswert
        talent_value = creature.talents[talent_name]
    else:
        talent_value = 0

    # Würfelwurf
    roll = np.array([random.randint(1, 20) for _ in range(3)])

    # Attribute
    attributes = np.array([ creature.attributes[attribute] for attribute in talent["attributes"] ])
    #attributes = np.array([getattr(self, attribute) for attribute in talents.get(talent)])

    diff = (roll - netto_mod) - attributes
    remaining = talent_value - sum(diff[diff > 0])

    print('{0:} würfelt eine Probe auf {1:} mit einer Erschwerniss von {2:}.'.format(creature.name, talent.name, netto_mod))
    print("{0:}'s FW ist {1:}.".format(creature.name, talent_value))
    print('Die relevanten Atribute sind {0:}/{1:}/{2:} = {3:}/{4:}/{5:}'.format(talent["attributes"][0], talent["attributes"][1], talent["attributes"][2], attributes[0], attributes[1], attributes[2]))
    print('Die Würfel zeigen: {0:} - {1:} - {2:}'.format(roll[0], roll[1], roll[2]))
    

    if remaining >= 0:
        #print(spec_text('ERFOLG! mit QS = {:}'.format(QS(remaining)), bcolors.cyan))
        return quality_level(remaining)
    else:
        #print(spec_text('FEHLSCHLAG!', bcolors.red))
        return 0


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
