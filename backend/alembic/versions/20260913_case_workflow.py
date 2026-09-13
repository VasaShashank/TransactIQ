"""Add case workflow approval and evidence fields.

Revision ID: 20260913_case_workflow
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "20260913_case_workflow"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("cases")}

    additions = {
        "evidence": sa.Column("evidence", sa.JSON(), nullable=False, server_default="[]"),
        "verdict": sa.Column("verdict", sa.String(), nullable=True),
        "approved_by": sa.Column("approved_by", sa.Integer(), nullable=True),
        "approved_at": sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        "closed_by": sa.Column("closed_by", sa.Integer(), nullable=True),
        "closed_at": sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    }

    for name, column in additions.items():
        if name not in columns:
            op.add_column("cases", column)

    op.alter_column("cases", "evidence", server_default=None)

    account_columns = {column["name"] for column in inspector.get_columns("accounts")}
    for name in ("phone", "email", "device_id", "card_id"):
        if name not in account_columns:
            op.add_column("accounts", sa.Column(name, sa.String(), nullable=True))
            op.create_index(f"ix_accounts_{name}", "accounts", [name])


def downgrade() -> None:
    for name in ("closed_at", "closed_by", "approved_at", "approved_by", "verdict", "evidence"):
        op.drop_column("cases", name)
    for name in ("phone", "email", "device_id", "card_id"):
        op.drop_index(f"ix_accounts_{name}", table_name="accounts")
        op.drop_column("accounts", name)
