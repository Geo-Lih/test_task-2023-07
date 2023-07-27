"""Database creation

Revision ID: 8057854ee61e
Revises: ecaa46fea308
Create Date: 2023-07-26 01:21:10.318228

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8057854ee61e'
down_revision = 'ecaa46fea308'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'plans', 'dictionary', ['category_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'plans', type_='foreignkey')
    # ### end Alembic commands ###