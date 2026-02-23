# app/modules/game/time_limits.py
def get_time_limit_ms(level: int) -> int:
    if level <= 1:
        return 35_000
    if level <= 3:
        return 45_000
    if level <= 5:
        return 55_000
    if level <= 8:
        return 60_000
    if level <= 10:
        return 75_000
    if level == 11:
        return 90_000
    if level == 12:
        return 105_000
    return 60_000
