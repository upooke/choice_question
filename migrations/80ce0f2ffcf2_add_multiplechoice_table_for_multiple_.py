"""Add MultipleChoice table for multiple_choice plugin

Revision ID: 80ce0f2ffcf2
Revises: 1093835a1051
Create Date: 2020-05-08 14:26:51.946967

"""
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "80ce0f2ffcf2"
down_revision = None
branch_labels = None
depends_on = None


def upgrade(op=None):
    try:
        op.create_table(
            "multiple_choice",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["id"], ["challenges.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    except sa.exc.InternalError as e:
        print(str(e))


def downgrade(op=None):
    op.drop_table("multiple_choice")
