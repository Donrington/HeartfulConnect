"""empty message

Revision ID: 4b50bfd8abf7
Revises: 8b0d6d725ca8
Create Date: 2023-10-16 10:58:46.587700

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4b50bfd8abf7'
down_revision = '8b0d6d725ca8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin',
    sa.Column('idAdmin', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('idAdmin'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.drop_table('payment')
    with op.batch_alter_table('plan', schema=None) as batch_op:
        batch_op.drop_index('plan_name')

    op.drop_table('plan')
    op.drop_table('subscription')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subscription',
    sa.Column('subscription_id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('subscription_name', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('description', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('benefits', mysql.VARCHAR(length=500), nullable=False),
    sa.Column('plan_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('payment_method', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('plan_start_date', mysql.DATETIME(), nullable=True),
    sa.Column('plan_end_date', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('subscription_id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('plan',
    sa.Column('plan_id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('plan_name', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('plan_sub_month', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('plan_sub_month_price', mysql.VARCHAR(length=120), nullable=True),
    sa.Column('plan_sub_year', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('plan_sub_year_price', mysql.VARCHAR(length=120), nullable=True),
    sa.Column('subscription_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('plan_id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('plan', schema=None) as batch_op:
        batch_op.create_index('plan_name', ['plan_name'], unique=False)

    op.create_table('payment',
    sa.Column('payment_id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('subscription_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('amount', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('payment_date', mysql.DATETIME(), nullable=True),
    sa.Column('payment_method', mysql.VARCHAR(length=80), nullable=False),
    sa.PrimaryKeyConstraint('payment_id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('admin')
    # ### end Alembic commands ###