from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
from app.modules.users.models import User
from app.modules.auth.models import RefreshToken
from app.modules.seasons.models import Season
from app.modules.tiers.models import Tier, TierTranslation

def reset_schema(schema: str = "public"):
    with engine.connect() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        conn.execute(text(f"CREATE SCHEMA {schema}"))
        conn.commit()

if __name__ == "__main__":
    reset_schema("public")
    Base.metadata.create_all(bind=engine)
    print("✅ Banco resetado e tabelas recriadas.")

# python -m app.scripts.create_tables