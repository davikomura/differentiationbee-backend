from app.db.session import SessionLocal
from app.modules.tiers.models import Tier, TierTranslation

TIERS = [
    ("rookie",   0,    199,  1, {"pt-BR": "Novato",     "en": "Rookie",    "es": "Novato"}),
    ("bronze",   200,  399,  2, {"pt-BR": "Bronze",     "en": "Bronze",    "es": "Bronce"}),
    ("silver",   400,  599,  3, {"pt-BR": "Prata",      "en": "Silver",    "es": "Plata"}),
    ("gold",     600,  799,  4, {"pt-BR": "Ouro",       "en": "Gold",      "es": "Oro"}),
    ("platinum", 800,  999,  5, {"pt-BR": "Platina",    "en": "Platinum",  "es": "Platino"}),
    ("diamond",  1000, 1199, 6, {"pt-BR": "Diamante",   "en": "Diamond",   "es": "Diamante"}),
    ("master",   1200, 1399, 7, {"pt-BR": "Mestre",     "en": "Master",    "es": "Maestro"}),
    ("champion", 1400, 1599, 8, {"pt-BR": "Campeão",    "en": "Champion",  "es": "Campeón"}),
    ("titan",    1600, 1799, 9, {"pt-BR": "Titã",       "en": "Titan",     "es": "Titán"}),
    ("legend",   1800, 1999, 10,{"pt-BR": "Lenda",      "en": "Legend",    "es": "Leyenda"}),
    ("mythic",   2000, 2399, 11,{"pt-BR": "Mítico",     "en": "Mythic",    "es": "Mítico"}),
    ("immortal", 2400, None, 12,{"pt-BR": "Imortal",    "en": "Immortal",  "es": "Inmortal"}),
]

def main():
    db = SessionLocal()
    try:
        for key, min_t, max_t, order, titles in TIERS:
            exists = db.query(Tier).filter(Tier.key == key).first()
            if exists:
                continue

            tier = Tier(key=key, min_points=min_t, max_points=max_t, rank_order=order)
            db.add(tier)
            db.flush()

            for locale, title in titles.items():
                db.add(TierTranslation(tier_id=tier.id, locale=locale, title=title, description=None))

        db.commit()
        print("✅ Tiers seeded.")
    finally:
        db.close()

if __name__ == "__main__":
    main()