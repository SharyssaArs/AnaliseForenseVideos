"""create usuarios table

Revision ID: 001
Revises:
Create Dare: 2026-05-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None #Union aceita mais um tipo de dado (string ou None)
branch_labels: Union[str, Sequence[str], None] = None #Sequence: podendo ser uma lista ou trupla de strings
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None: #None: n retorna nada
    op.create_table(
        "usuarios", 
        sa.Column("id", sa.CHAR(length=36), primary_key=True, nullable=False),
        sa.Column("nome", sa.VARCHAR(length=100), nullable=False),
        sa.Column("email", sa.VARCHAR(length=150), nullable=False),
        sa.Column("senha_hash", sa.VARCHAR(length=255), nullable=False),
        sa.Column(
            "criado_em",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True
        ),
        sa.Column(
            "atualizado_em",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.UniqueConstraint("email", name="uq_usuarios_email"),
    )

def downgrade() -> None:
    op.drop_table("usuarios")