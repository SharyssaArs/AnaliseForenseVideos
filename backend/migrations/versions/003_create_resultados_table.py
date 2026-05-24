"""create results table

Revision ID: 003
Revises: 002
Create Date: 2026-05-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "resultados_ia",
        sa.Column("id", sa.CHAR(length=36), primary_key=True, nullable=False),
        sa.Column("analise_id", sa.CHAR(length=36), nullable=False),
        sa.Column("score_confianca", sa.DECIMAL(precision=5, scale=4), nullable=False),
        sa.Column(
            "classificacao",
            sa.Enum("REAL", "MANIPULADO", name="classificacao_resultado_ia"), 
            nullable=False,
            ),
        sa.Column("detalhes_json", sa.JSON(), nullable=False),
        sa.Column("finalizado_em",sa.TIMESTAMP(), nullable=True),
        sa.Column(
            "criado_em",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False
        ),
        sa.Column(
            "atualizado_em",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "score_confianca >= 0.0000 AND score_confianca <= 1.0000",
            name="CK_resultados_ia_score_confianca_range",
        ),
        sa.ForeignKeyConstraint(
            ["analise_id"],
            ["analises.id"],
            ondelete="CASCADE",
            name="FK_resultados_ia_analise_id"
        ),
        sa.UniqueConstraint("analise_id", name="UQ_resultados_ia_analise_id"),
    )

    op.create_index(
        "IDX_resultados_ia_analise_id",
        "resultados_ia",
        ["analise_id"],
    )

def downgrade() -> None:
    op.drop_index("IDX_resultados_ia_analise_id", table_name="resultados_ia")
    op.drop_table("resultados_ia")