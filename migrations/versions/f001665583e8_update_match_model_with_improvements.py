"""Update Match model with improvements

Revision ID: f001665583e8
Revises: a59a95bc3c05
Create Date: 2025-04-04 06:48:13.135428

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f001665583e8'
down_revision = 'a59a95bc3c05'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('match', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
        batch_op.alter_column('phone_number',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('target_phone',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('status',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.create_index('idx_match_phone', ['phone_number'], unique=False)
        batch_op.create_index('idx_match_status', ['status'], unique=False)
        batch_op.create_index('idx_match_target', ['target_phone'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('match', schema=None) as batch_op:
        batch_op.drop_index('idx_match_target')
        batch_op.drop_index('idx_match_status')
        batch_op.drop_index('idx_match_phone')
        batch_op.alter_column('status',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('target_phone',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('phone_number',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###
