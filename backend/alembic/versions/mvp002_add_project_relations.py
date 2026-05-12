"""add project_id to datasets & analysis_sessions, add title to sessions

Revision ID: mvp002
Revises: mvp001
Create Date: 2026-05-09

"""
from alembic import op
import sqlalchemy as sa


revision = "mvp002"
down_revision = "mvp001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("datasets", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_datasets_project_id",
        "datasets",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("analysis_sessions", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_analysis_sessions_project_id",
        "analysis_sessions",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_analysis_sessions_project_id"),
        "analysis_sessions",
        ["project_id"],
        unique=False,
    )

    op.add_column("analysis_sessions", sa.Column("title", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("analysis_sessions", "title")
    op.drop_index(op.f("ix_analysis_sessions_project_id"), table_name="analysis_sessions")
    op.drop_constraint("fk_analysis_sessions_project_id", "analysis_sessions", type_="foreignkey")
    op.drop_column("analysis_sessions", "project_id")
    op.drop_constraint("fk_datasets_project_id", "datasets", type_="foreignkey")
    op.drop_column("datasets", "project_id")
