from models.properties import TalentDefinition
from models.creature import Creature
import numpy as np
import random




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

    talent = TalentDefinition.get(talent_name)

    # modification due to status effects
    netto_mod = 0
    for status_effect in creature.status_effects.values():
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
    print('Die relevanten Atribute sind {0:}/{1:}/{2:} = {3:}/{4:}/{5:}'.format( talent.attributes[0].value, talent.attributes[1].value, talent.attributes[2].value, attributes[0], attributes[1], attributes[2]))
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


class Report:
    message: str = ''

    def add_message(self, message: str) -> None:
        self.message += '\n'+message

def attack(attacker: Creature, weapon: Weapon, target: Creature | None = None, abilities: None = None) -> Report:
    """
    Führt einen Angriffswurf von <attacker> gegen <target> aus und nutzt dafür übergebene Waffen <weapon> und Sonderfertigkeiten <abilities>.
    Wenn <target> = None wird nur ein Boolean fürs Gelingen der Probe zurückgegeben.
    Sonst wird ein Verteidigungswurf von <target> ausgeführt und schaden zugefügt, sollte dieser misslingen.
    """

    if target is None:
        report = Report(message = "{0:} greift mit {1:} an.".format(attacker.name, weapon.name))
    else:
        report = Report(message = "{0:} greift {1:} mit {2:} an.".format(attacker.name, target.name, weapon.name))

    attack_value = weapon.attack_value.current

    if isinstance(weapon, RangedWeapon):
        distance = input("Wie groß ist die Ditanz? ")
        report.add_message("Die Distanz beträgt {:} Schritt".format(distance))
        if distance <= weapon.range[0]:
            attack_value += 2
            report.add_message("Schuss auf kurze Distanz!")
        elif distance > weapon.range[1] and distance <= weapon.range[2]:
            attack_value += -2
            report.add_message("Schuss auf große Distanz!")
        elif distance > 1.5*weapon.range[2]:
            return report.add_message("Das Ziel ist außer Reichweite!")
        else:
            report.add_message("Schuss auf mittlere Distanz!")

    # roll the dice
    roll = random.randint(1, 20)
    crit = True
    if roll == 1:
        confirmation_roll = random.randint(1, 20)
        if confirmation_roll == 1:
            report.add_message("{:} würfelt einen epischen Erfolg!".format(attacker.name))
        elif confirmation_roll <= attack_value:
            report.add_message("{:} würfelt einen krittischen Erfolg!".format(attacker.name))
    elif roll <= attack_value:
        crit = False
        report.add_message("{:} trifft!".format(attacker.name))
    else:
        return report


    # defense of target
    if weapon.is_parryable and target is not None:
        defence = target.AW

        if isinstance(weapon, RangedWeapon):
            for target_weapon in target.weapons:
                if target_weapon.type is WeaponType.SHIELD and target_weapon.is_equipped: 
                    defense = max(defense, target_weapon.parry.current)
            if weapon.type is WeaponType.THROW:
                defense -= 2
            else:
                defense -= 4
        else: # if weapon is meele weapon
            parry = max(target_weapon.parry.current for target_weapon in target.weapons if target_weapon.is_equipped)
            defense = max(defense, parry)

        defense -= 3 * target.defenses_in_this_round.value
        target.defenses_in_this_round.increase()

        if crit:
            defense = defense // 2   

        defense_roll = random.randint(1, 20)
        defense_crit = True
        if defense_roll <= defense:
            report.add_message("Angriff wurde verteidigt")
            return report

    damage = attacker.weapon.roll_damage()

    if target is not None:
        target.get_damage(damage)
        
    return report