# app/modules/game/time_limits.py
def get_time_limit_ms(level: int) -> int:
    if level <= 1:
        return 40_000
    if level == 2:
        return 50_000
    if level == 3:
        return 60_000
    if level == 4:
        return 70_000
    if level == 5:
        return 80_000
    if level == 6:
        return 90_000
    if level == 7:
        return 100_000
    if level == 8:
        return 110_000
    if level == 9:
        return 125_000
    if level == 10:
        return 140_000
    if level == 11:
        return 160_000
    if level == 12:
        return 180_000
    return 60_000
