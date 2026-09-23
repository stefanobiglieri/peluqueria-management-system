"""Enable unaccent extension

Revision ID: d2e74c60a7cc
Revises: 63bcfea78849
Create Date: 2026-09-22 23:42:47.511147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2e74c60a7cc'
down_revision: Union[str, Sequence[str], None] = '63bcfea78849'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # unaccent: función de PostgreSQL que remueve acentos de un texto
    # (ej. "Gómez" -> "Gomez"), necesaria para que la búsqueda de
    # clientes por nombre/apellido no dependa de que el usuario tipee
    # los acentos exactos.
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS unaccent;")
