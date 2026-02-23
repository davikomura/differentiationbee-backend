"""unique active session per user

Revision ID: 0002_unique_active_session_per_user
Revises: 0001_initial_schema
Create Date: 2026-02-23
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_unique_active_session_per_user"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "uq_game_sessions_one_active_per_user",
        "game_sessions",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )


def downgrade() -> None:
    op.drop_index("uq_game_sessions_one_active_per_user", table_name="game_sessions")
