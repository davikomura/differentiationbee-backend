# create_db.py
from app.db.session import Base, engine
from app.models.session import GameSession
from app.models.user import User

def create_tables():
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")

if __name__ == "__main__":
    create_tables()
