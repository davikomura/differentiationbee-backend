"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-02-20
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "seasons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_seasons_id", "seasons", ["id"])
    op.create_index("ix_seasons_window", "seasons", ["starts_at", "ends_at"])

    op.create_table(
        "tiers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("min_points", sa.Integer(), nullable=False),
        sa.Column("max_points", sa.Integer(), nullable=True),
        sa.Column("rank_order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index("ix_tiers_id", "tiers", ["id"])
    op.create_index("ix_tiers_range", "tiers", ["min_points", "max_points"])

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "season_translations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["season_id"], ["seasons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("season_id", "locale", name="uq_season_locale"),
    )
    op.create_index("ix_season_translations_id", "season_translations", ["id"])
    op.create_index("ix_season_translations_locale", "season_translations", ["locale"])

    op.create_table(
        "tier_translations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tier_id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["tier_id"], ["tiers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tier_id", "locale", name="uq_tier_locale"),
    )
    op.create_index("ix_tier_translations_id", "tier_translations", ["id"])
    op.create_index("ix_tier_translations_locale", "tier_translations", ["locale"])

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_refresh_tokens_id", "refresh_tokens", ["id"])
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)
    op.create_index("ix_refresh_tokens_user", "refresh_tokens", ["user_id"])

    op.create_table(
        "game_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.Column("seed", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("correct_answers", sa.Integer(), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["season_id"], ["seasons.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_game_sessions_id", "game_sessions", ["id"])
    op.create_index("ix_game_sessions_active", "game_sessions", ["user_id", "is_active"])
    op.create_index("ix_game_sessions_user_started", "game_sessions", ["user_id", "started_at"])
    op.create_index("ix_game_sessions_season_id", "game_sessions", ["season_id"])

    op.create_table(
        "issued_questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("expression_str", sa.Text(), nullable=False),
        sa.Column("expression_latex", sa.Text(), nullable=True),
        sa.Column("derivative_str", sa.Text(), nullable=False),
        sa.Column("derivative_latex", sa.Text(), nullable=True),
        sa.Column("time_limit_ms", sa.Integer(), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("answered", sa.Boolean(), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["game_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_issued_questions_id", "issued_questions", ["id"])
    op.create_index("ix_issued_questions_session_issued", "issued_questions", ["session_id", "issued_at"])
    op.create_index("ix_issued_questions_user_session", "issued_questions", ["user_id", "session_id"])

    op.create_table(
        "attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("issued_question_id", sa.Integer(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("expression_str", sa.Text(), nullable=False),
        sa.Column("expression_latex", sa.Text(), nullable=True),
        sa.Column("derivative_latex", sa.Text(), nullable=True),
        sa.Column("user_answer", sa.Text(), nullable=False),
        sa.Column("use_latex", sa.Boolean(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("time_taken_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["issued_question_id"], ["issued_questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["game_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attempts_id", "attempts", ["id"])
    op.create_index("ix_attempts_session_created", "attempts", ["session_id", "created_at"])
    op.create_index("ix_attempts_user_created", "attempts", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_attempts_user_created", table_name="attempts")
    op.drop_index("ix_attempts_session_created", table_name="attempts")
    op.drop_index("ix_attempts_id", table_name="attempts")
    op.drop_table("attempts")

    op.drop_index("ix_issued_questions_user_session", table_name="issued_questions")
    op.drop_index("ix_issued_questions_session_issued", table_name="issued_questions")
    op.drop_index("ix_issued_questions_id", table_name="issued_questions")
    op.drop_table("issued_questions")

    op.drop_index("ix_game_sessions_season_id", table_name="game_sessions")
    op.drop_index("ix_game_sessions_user_started", table_name="game_sessions")
    op.drop_index("ix_game_sessions_active", table_name="game_sessions")
    op.drop_index("ix_game_sessions_id", table_name="game_sessions")
    op.drop_table("game_sessions")

    op.drop_index("ix_refresh_tokens_user", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_token_hash", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.drop_index("ix_tier_translations_locale", table_name="tier_translations")
    op.drop_index("ix_tier_translations_id", table_name="tier_translations")
    op.drop_table("tier_translations")

    op.drop_index("ix_season_translations_locale", table_name="season_translations")
    op.drop_index("ix_season_translations_id", table_name="season_translations")
    op.drop_table("season_translations")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_tiers_range", table_name="tiers")
    op.drop_index("ix_tiers_id", table_name="tiers")
    op.drop_table("tiers")

    op.drop_index("ix_seasons_window", table_name="seasons")
    op.drop_index("ix_seasons_id", table_name="seasons")
    op.drop_table("seasons")
