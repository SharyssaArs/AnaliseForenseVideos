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
        sa.Column('id', sa.CHAR(length=36), primary_key=True),
        sa.Column('analise_id', sa.CHAR(length=36), sa.ForeignKey('analises.id', ondelete='CASCADE'), nullable=False),
        sa.Column('etapa', sa.String(length=100), nullable=False),
        sa.Column('status', sa.Enum('iniciado', 'sucesso', 'erro', name='status_log'), nullable=False),
        sa.Column('mensagem', sa.Text(), nullable=True),
        sa.Column('criado_em', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    
    op.create_index('IDX_logs_analise_id', 'logs_processamento', ['analise_id'])

def downgrade():
    #op.drop_index('IDX_logs_analise_id', table_name='logs_processamento')
    op.drop_table('logs_processamento')
    #sa.Enum(name='status_log').drop(op.get_bind(), checkfirst=False)