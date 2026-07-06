

def quality_level(fp_left: int) -> int:
    """
    Berechnet die QS aus dem FW; max QS 6, min QS 1

    Args:
        FW (int): Fähigkeitswert/Fähigkeitspunkte die nach einer Probe noch übrig sind.

    Returns:
        QS 
    """
    return max(1, min(6, (fp_left + 2) // 3))


class RoundHandler:
    def __init__(self):
        self.current_round = RoundCounter()
        self.actors = []
        self.update_order_of_action()


    def get_INIS(self):
        for actor in self.actors:
            if isinstance(actor, Character):
                actor.INI = input('{0:}s Initiative: '.format(actor.name))
            elif isinstance(actor, Kreatur):
                actor.roll_INI()

    def update_order_of_action(self):
        INIs = []
        for actor in self.actors:
            if actor.initiative.current is None:
                actor.roll_initiative()
            INIs.append(float(actor.INI)+float(actor.base_INI)/100.+random.uniform(0, 1e-3))

        self.actors = [actor for _, actor in sorted(zip(INIs, self.actors))]
        self.actors.reverse()

    def update