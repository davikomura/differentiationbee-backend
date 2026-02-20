from alembic import command
from alembic.config import Config


def migrate_to_head() -> None:
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")


if __name__ == "__main__":
    migrate_to_head()
    print("Schema atualizado para a ultima migration.")
