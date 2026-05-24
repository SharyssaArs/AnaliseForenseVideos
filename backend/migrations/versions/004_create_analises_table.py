"""create analises table

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
        'analises',
        sa.Column('id', sa.CHAR(length=36), primary_key=True),
        sa.Column('user_id', sa.CHAR(length=36), sa.ForeignKey('usuarios.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('task_id', sa.String(length=100), nullable=False),
        sa.Column('video_hash', sa.String(length=64), nullable=False),
        sa.Column('nome_arquivo', sa.String(length=255), nullable=False),
        # ENUM em inglês conforme os critérios da Issue #4:
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='status_analise'), nullable=False),
        sa.Column('progresso', sa.Integer(), server_default='0'),
        sa.Column('criado_em', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('atualizado_em', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    )
    
    op.create_index('IDX_analises_video_hash', 'analises', ['video_hash'], unique=True)
    op.create_index('IDX_analises_status', 'analises', ['status'])
    op.create_index('IDX_analises_task_id', 'analises', ['task_id'])

def downgrade():
    op.drop_index('IDX_analises_task_id', table_name='analises')
    op.drop_index('IDX_analises_status', table_name='analises')
    op.drop_index('IDX_analises_video_hash', table_name='analises')
    op.drop_table('analises')
    sa.Enum(name='status_analise').drop(op.get_bind(), checkfirst=False)