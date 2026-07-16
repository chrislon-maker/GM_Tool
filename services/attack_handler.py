from models.status_effect import ModifierContribution, ValueModifier, DependentCondition, Blind
from models.properties import AttackValue, Damage
from models.equipment import Weapon, MeeleWeapon, RangedWeapon, Armor
from models.creature import Creature
from models.enums import SizeCategory

from services.checks import CheckResult, check_on_crit

from dataclasses import dataclass, field
import numpy as np
import random



@dataclass(frozen=True)
class AttackContext:
    attacker: Creature
    weapon: Weapon
    attacker_movement: int = 0
    abilities: tuple[str, ...] = ()

    target: Creature | None = None
    target_weapon: Weapon | None = None
    target_movement: int = 0
    targer_swerving: bool = False
    targer_in_crowd: bool = False
    target_obscured: int = 0

    distance: float | None = None
    narrow_space: bool = False
    
    modifier: ValueModifier | None = None
    


class CombatValueCalculator:

    def attack_value_modifications(self, context: AttackContext) -> list[ModifierContribution]:
        attacker = context.attacker
        weapon = context.weapon
        # create dummy bool for status effect conditions that are only active during the attack action. Change to False when vision is irrelevant again
        attack_lasting: bool = True 

        attack_value = AttackValue(attacker, weapon)

        # vision 
        if context.target_obscured != 0:
            if not Blind in attacker.status_effects:
                attacker.status_effects[Blind] = Blind()
            
            # add #level references to the same removal_condition
            # Consider changing this to adding multiple identical removal_conditions instead
            for i in range(context.target_obscured):
                attacker.status_effects[Blind].removal_conditions.append(DependentCondition(lambda dummy_bool=attack_lasting: dummy_bool))
        
        # creature specific modifications including status effects
        modifications = attack_value.modifications()

        # meele weapon mods
        if isinstance(weapon, MeeleWeapon):
            modifications.append(self.meele_modifier(context))

        # ranged weapon mods
        if isinstance(weapon, RangedWeapon):
            modifications.append(self.range_modifier(context))

        # flat (external) bonus
        if context.modifier is not None:
            modifications.append(
                ModifierContribution(
                    modifier = context.modifier,
                    source_name = "user",
                    description = "Manueller Modifikator"
                    )
            )

        # disable Conditions that where able only during the attack calculation
        attack_lasting = False
      
        return modifications
    
    
    def meele_modifier(self,  context: AttackContext) -> list[ModifierContribution]:
        weapon = context.weapon
        contributions: list[ModifierContribution] = []

        # weapon range difference 
        if context.target is not None and context.target_weapon is not None:
            modifier = ValueModifier(additive = -2*max(0, context.target_weapon.range - weapon.range))
            if not modifier.is_neutral:
                contributions.append(
                    ModifierContribution( 
                        modifier = modifier,
                        source_name = "weapon range difference",
                        description = "Reichweite: {0:} vs. {1:}".format(weapon.range, context.target_weapon.range)
                    )
                )  

        return contributions



    def range_modifier(self, context: AttackContext) -> list[ModifierContribution]:
        contributions: list[ModifierContribution] = []

        # consider distance
        distance = context.distance 
        if distance is None:
            raise ValueError("Für einen Fernkampfangriff fehlt die Distanz.")
        
        short, medium, long = context.weapon.range
        if distance <= short:
            contributions.append(
                ModifierContribution( 
                    modifier =  ValueModifier(additive = 2),
                    source_name = "distance",
                    description = "Reichweite nah"
                )
            )  
        elif distance > medium and distance <= long:
            contributions.append(
                ModifierContribution( 
                    modifier =  ValueModifier(additive = -2),
                    source_name = "distance",
                    description = "Reichweite weit"
                )
            )  
        elif distance > long:
            raise TargetOutOfRange
        
        # attacker movement
        movement = context.attacker_movement
        if 0 < movement <= 4:
            contributions.append(
                ModifierContribution( 
                    modifier =  ValueModifier(additive = -2),
                    source_name = "attacker movement",
                    description = "{:} bewegt sich langsam".format(context.attacker.name)
                )
            )  
        elif 4 < movement:
            contributions.append(
                ModifierContribution( 
                    modifier =  ValueModifier(additive = -4),
                    source_name = "attacker movement",
                    description = "{:} bewegt sich schnell".format(context.attacker.name)
                )
            )


        # target modifiers 
        if context.target is not None:
            target = context.target

            # target size
            modifier = ValueModifier(additive = 4 * (target.size_category - SizeCategory.MEDIUM))
            if not modifier.is_neutral:
                contributions.append(
                    ModifierContribution( 
                        modifier =  modifier,
                        source_name = "target size",
                        description = "Ziel ist {:}".format(target.size_category.label)
                    )
                )

        # target movement
        movement = context.target_movement
        if movement == 0:
            contributions.append(
                ModifierContribution( 
                    modifier =  ValueModifier(additive = 2),
                    source_name = "target movement",
                    description = "{:} steht still".format(context.target.name or "Ziel")
                )
            ) 
        elif movement > 0:
            additive = 0
            description = "Ziel bewegt sich"
            if context.targer_swerving:
                additive += -4
                movement /= 2  
                targer_swerving_string = "und schlägt Haken"

            if movement >= 5:
                additive += -2
                description += " schnell"

            contributions.append(
                ModifierContribution( 
                    modifier =  ValueModifier(additive = additive),
                    source_name = "target movement",
                    description = "{0:} {1:}".format(description, targer_swerving_string or "")
                )
            )

        # in crowd
        if context.targer_in_crowd:
            contributions.append(
                ModifierContribution( 
                    modifier =  ValueModifier(additive = -2),
                    source_name = "target in crowd",
                    description = "Schuss ins Kampfgetümmel"
                )
            )

        return contributions

    #TBD
    def defense_modifier(self,  context: AttackContext) -> list[ModifierContribution]:
        weapon = context.weapon
        contributions: list[ModifierContribution] = []

        # weapon range difference 
        if context.target is not None and context.target_weapon is not None:
            modifier = ValueModifier(additive = -2*max(0, context.target_weapon.range - weapon.range))
            if not modifier.is_neutral:
                contributions.append(
                    ModifierContribution( 
                        modifier = modifier,
                        source_name = "weapon range difference",
                        description = "Reichweite: {0:} vs. {1:}".format(weapon.range, context.target_weapon.range)
                    )
                )  

        return contributions

    # TBD
    def roll_damage(self, context: AttackContext) -> Damage:
        # roll damage
        formula = self.damage_formula.replace(" ", "")

        if "+" in formula:
            dice, flat = formula.split("+")
            flat = int(flat)
        else:
            dice = formula
            flat = 0

        number, sides = dice.split("W")
        amount = sum(random.randint(1, int(sides)) for _ in range(int(number)))
        amount += flat

        # attribute bonus
        attribute_bonus = max(self.creature.attributes[attribute] - threshold for attribute, threshold in self.damage_attribute.items())
        amount += attribute_bonus

        return Damage(type=self.damage_type, amount=amount)

#TBD: maybe move resolve() to CombatValueCalculator, not two distinct classes PROCEED HERE
class AttackHandler:
    def __init__(self, context: AttackContext):
        self.context = context

    def resolve(self) -> CheckResult:
        """
        Führt einen Angriffswurf von <attacker> gegen <target> aus und nutzt dafür übergebene Waffen <weapon> und Sonderfertigkeiten <abilities>.
        Wenn <target> = None wird nur ein Boolean fürs Gelingen der Probe zurückgegeben.
        Sonst wird ein Verteidigungswurf von <target> ausgeführt und schaden zugefügt, sollte dieser misslingen.
        """

        # attack roll
        attack_value_modifications = CombatValueCalculator.attack_value_modifications(self.context)

        modifier = ValueModifier()
        for contribution in attack_value_modifications:
            modifier = modifier.combine(contribution.modifier)

        attack_value = modifier.apply(AttackValue(self.context.attacker, self.context.weapon).base)
        result = self.check_result(attack_value)



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