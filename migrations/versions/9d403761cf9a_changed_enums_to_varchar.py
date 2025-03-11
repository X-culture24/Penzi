"""Changed ENUMs to VARCHAR

Revision ID: 9d403761cf9a
Revises: 94844424f70f
Create Date: 2025-03-11 11:27:21.503249

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9d403761cf9a'
down_revision = '94844424f70f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('approval_request', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=postgresql.ENUM('Pending', 'Approved', 'Declined', name='approval_status_enum'),
               type_=sa.String(length=20),
               existing_nullable=False)

    with op.batch_alter_table('user_details', schema=None) as batch_op:
        batch_op.alter_column('marital_status',
               existing_type=postgresql.ENUM('Single', 'Married', 'Divorced', name='marital_status_enum'),
               type_=sa.String(length=20),
               existing_nullable=False)
        batch_op.alter_column('religion',
               existing_type=postgresql.ENUM('Christian', 'Muslim', 'Other', name='religion_enum'),
               type_=sa.String(length=50),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_details', schema=None) as batch_op:
        batch_op.alter_column('religion',
               existing_type=sa.String(length=50),
               type_=postgresql.ENUM('Christian', 'Muslim', 'Other', name='religion_enum'),
               existing_nullable=False)
        batch_op.alter_column('marital_status',
               existing_type=sa.String(length=20),
               type_=postgresql.ENUM('Single', 'Married', 'Divorced', name='marital_status_enum'),
               existing_nullable=False)

    with op.batch_alter_table('approval_request', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=sa.String(length=20),
               type_=postgresql.ENUM('Pending', 'Approved', 'Declined', name='approval_status_enum'),
               existing_nullable=False)

    # ### end Alembic commands ###
