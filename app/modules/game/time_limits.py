# app/modules/game/time_limits.py
def get_time_limit_ms(level: int) -> int:
    if level <= 2:
        return 20_000
    if level <= 4:
        return 30_000
    if level <= 6:
        return 45_000
    if level <= 8:
        return 60_000
    if level <= 10:
        return 75_000
    if level == 11:
        return 90_000
    if level == 12:
        return 105_000
    return 60_000