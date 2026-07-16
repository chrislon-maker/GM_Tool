from models.status_effect import StatusModifierResolver, ModifierQuery, ModifierContribution

from services.talent_check_handler import TalentCheckHandler


class SpellCheckHandler(TalentCheckHandler):

    def get_modifiers(self) -> list[ModifierContribution]:

        # modification due to status effects
        query = ModifierQuery(
            value_type = self.context.value_type,   
            actor = self.context.actor,         
            subject = self.subject
        )

        modifier_contributions = StatusModifierResolver.resolve(query)

        return modifier_contributions
    
    




