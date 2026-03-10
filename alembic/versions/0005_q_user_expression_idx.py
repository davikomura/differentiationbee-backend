"""issued question user expression index

Revision ID: 0005_q_user_expression_idx
Revises: 0004_q_user_derivative_idx
Create Date: 2026-03-10
"""

from alembic import op


revision = "0005_q_user_expression_idx"
down_revision = "0004_q_user_derivative_idx"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_issued_questions_user_expression",
        "issued_questions",
        ["user_id", "expression_str"],
    )


def downgrade() -> None:
    op.drop_index("ix_issued_questions_user_expression", table_name="issued_questions")
