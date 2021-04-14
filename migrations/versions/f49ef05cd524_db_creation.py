"""db creation

Revision ID: f49ef05cd524
Revises: 
Create Date: 2021-04-13 19:25:40.712840

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f49ef05cd524'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('book_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status_name', sa.String(length=60), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('org_full_name', sa.String(length=120), nullable=False),
    sa.Column('org_short_name', sa.String(length=20), nullable=False),
    sa.Column('org_type', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role_name', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('book',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('qr_id', sa.String(length=20), nullable=True),
    sa.Column('real_id', sa.String(length=140), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('status_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['status_id'], ['book_status.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_book_qr_id'), ['qr_id'], unique=True)

    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('telegram_id', sa.Integer(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('user_role_id', sa.Integer(), nullable=True),
    sa.Column('user_company_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['user_role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('action',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('location', sa.String(length=30), nullable=True),
    sa.Column('old_status_id', sa.Integer(), nullable=True),
    sa.Column('new_status_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('book_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.ForeignKeyConstraint(['new_status_id'], ['book_status.id'], ),
    sa.ForeignKeyConstraint(['old_status_id'], ['book_status.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('action', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_action_timestamp'), ['timestamp'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('action', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_action_timestamp'))

    op.drop_table('action')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_book_qr_id'))

    op.drop_table('book')
    op.drop_table('role')
    op.drop_table('company')
    op.drop_table('book_status')
    # ### end Alembic commands ###
