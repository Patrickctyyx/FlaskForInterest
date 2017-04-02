"""empty message

Revision ID: aac65e83ee37
Revises: cf6c6d1681f3
Create Date: 2017-04-02 16:29:45.552849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aac65e83ee37'
down_revision = 'cf6c6d1681f3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('body_html', sa.Text(), nullable=True),
    sa.Column('cred_at', sa.DateTime(), nullable=True),
    sa.Column('disabled', sa.Boolean(), nullable=True),
    sa.Column('author_id', sa.String(length=36), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['Account.uid'], ),
    sa.ForeignKeyConstraint(['post_id'], ['Post.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Comment_cred_at'), 'Comment', ['cred_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_Comment_cred_at'), table_name='Comment')
    op.drop_table('Comment')
    # ### end Alembic commands ###