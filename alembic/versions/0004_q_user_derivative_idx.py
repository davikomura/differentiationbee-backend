"""issued question user derivative index

Revision ID: 0004_q_user_derivative_idx
Revises: 0003_unique_season_time_window
Create Date: 2026-03-10
"""

from alembic import op


revision = "0004_q_user_derivative_idx"
down_revision = "0003_unique_season_time_window"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_issued_questions_user_derivative",
        "issued_questions",
        ["user_id", "derivative_str"],
    )


def downgrade() -> None:
    op.drop_index("ix_issued_questions_user_derivative", table_name="issued_questions")
