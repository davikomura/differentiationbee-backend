"""unique season time window

Revision ID: 0003_unique_season_time_window
Revises: 0002_active_session_user
Create Date: 2026-03-10
"""

from alembic import op


revision = "0003_unique_season_time_window"
down_revision = "0002_active_session_user"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_seasons_time_window",
        "seasons",
        ["starts_at", "ends_at"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_seasons_time_window", "seasons", type_="unique")
