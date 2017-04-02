"""empty message

Revision ID: 3b63b713160f
Revises: 
Create Date: 2017-01-28 16:46:26.029484

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b63b713160f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Contacts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('phone', sa.String(length=16), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('Role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('default', sa.Boolean(), nullable=True),
    sa.Column('permissions', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_Role_default'), 'Role', ['default'], unique=False)
    op.create_table('Account',
    sa.Column('uid', sa.String(length=36), nullable=False),
    sa.Column('passwd', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['Role.id'], ),
    sa.PrimaryKeyConstraint('uid')
    )
    op.create_table('UserInfo',
    sa.Column('uid', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('phone', sa.String(length=16), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('grade', sa.String(length=64), nullable=True),
    sa.Column('department', sa.String(length=128), nullable=True),
    sa.Column('school', sa.String(length=128), nullable=True),
    sa.Column('major', sa.String(length=128), nullable=True),
    sa.Column('qq', sa.String(length=64), nullable=True),
    sa.Column('introduction', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['uid'], ['Account.uid'], ),
    sa.PrimaryKeyConstraint('uid'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('phone'),
    sa.UniqueConstraint('qq'),
    sa.UniqueConstraint('student_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('UserInfo')
    op.drop_table('Account')
    op.drop_index(op.f('ix_Role_default'), table_name='Role')
    op.drop_table('Role')
    op.drop_table('Contacts')
    # ### end Alembic commands ###