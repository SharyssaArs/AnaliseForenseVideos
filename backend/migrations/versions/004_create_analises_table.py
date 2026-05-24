"""create logs_processamento table

Revision ID: 004
Revises: 003
Create Date: 2026-05-23
"""
from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'logs_processamento',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('video_id', sa.Integer, nullable=False),
        sa.Column('resultado', sa.String(255), nullable=False),
        sa.Column('data_analise', sa.DateTime, nullable=False)
    )
