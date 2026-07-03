

def quality_level(fp_left: int) -> int:
    """
    Berechnet die QS aus dem FW; max QS 6, min QS 1

    Args:
        FW (int): Fähigkeitswert/Fähigkeitspunkte die nach einer Probe noch übrig sind.

    Returns:
        QS 
    """
    return max(1, min(6, (fp_left + 2) // 3))