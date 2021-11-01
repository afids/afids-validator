"""empty message

Revision ID: a0928ce2eee6
Revises: 11230bf660dc
Create Date: 2021-10-13 16:19:02.318876

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a0928ce2eee6"
down_revision = "11230bf660dc"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "flask_dance_oauth",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("token", sa.JSON(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("human_fiducial_set", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("afids_user_id", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(None, "user", ["afids_user_id"], ["id"])
        batch_op.drop_column("user_id")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("human_fiducial_set", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "user_id", sa.VARCHAR(), autoincrement=False, nullable=True
            )
        )
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.drop_column("afids_user_id")

    op.drop_table("flask_dance_oauth")
    op.drop_table("user")
    # ### end Alembic commands ###
