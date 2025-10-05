"""
Generic single-database configuration.
This template is provided for completeness; not strictly required if you
only use pre-authored migration files.
"""
from __future__ import annotations
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_create_initial_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("verse_reference", sa.String(length=100), nullable=False),
        sa.Column("verse_text", sa.Text(), nullable=False),
        sa.Column("bible_version", sa.String(length=50), nullable=False),
        sa.Column("bible_id", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "favorite_verses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("verse_reference", sa.String(length=100), nullable=False),
        sa.Column("verse_text", sa.Text(), nullable=False),
        sa.Column("bible_version", sa.String(length=50), nullable=False),
        sa.Column("bible_id", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("favorite_verses")
    op.drop_table("journal_entries")
