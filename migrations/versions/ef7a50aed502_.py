"""empty message

Revision ID: ef7a50aed502
Revises: 79c22cf79633
Create Date: 2023-01-26 14:00:10.914978

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef7a50aed502'
down_revision = '79c22cf79633'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vehicle', schema=None) as batch_op:
        batch_op.drop_constraint('vehicle_planet_id_fkey', type_='foreignkey')
        batch_op.drop_column('planet_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vehicle', schema=None) as batch_op:
        batch_op.add_column(sa.Column('planet_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('vehicle_planet_id_fkey', 'planet', ['planet_id'], ['id'])

    # ### end Alembic commands ###
