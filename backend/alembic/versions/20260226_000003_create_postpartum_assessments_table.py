"""create postpartum assessments table

Revision ID: 20260226_000003
Revises: 20260224_000002
Create Date: 2026-02-26 12:20:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260226_000003"
down_revision: Union[str, None] = "20260224_000002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "postpartum_assessments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("age_group", sa.String(length=40), nullable=True),
        sa.Column("baby_age_months", sa.Float(), nullable=True),
        sa.Column("kgs_gained_during_pregnancy", sa.Float(), nullable=True),
        sa.Column("postnatal_problems", sa.Integer(), nullable=True),
        sa.Column("baby_feeding_difficulties", sa.Integer(), nullable=True),
        sa.Column("financial_problems", sa.Integer(), nullable=True),
        sa.Column("predicted_class", sa.String(length=64), nullable=False),
        sa.Column("probability_high_risk", sa.Float(), nullable=False),
        sa.Column("probability_low_risk", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=32), nullable=False),
        sa.Column("decision_threshold", sa.Float(), nullable=False),
        sa.Column("emergency_threshold", sa.Float(), nullable=False),
        sa.Column("advise_hospital_visit", sa.Boolean(), nullable=False),
        sa.Column("advise_emergency_care", sa.Boolean(), nullable=False),
        sa.Column("hospital_advice", sa.Text(), nullable=False),
        sa.Column("emergency_advice", sa.Text(), nullable=False),
        sa.Column("top_risk_factors", sa.JSON(), nullable=False),
        sa.Column("imputed_fields", sa.JSON(), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_postpartum_assessments_user_id",
        "postpartum_assessments",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_postpartum_assessments_created_at",
        "postpartum_assessments",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_postpartum_assessments_created_at", table_name="postpartum_assessments")
    op.drop_index("ix_postpartum_assessments_user_id", table_name="postpartum_assessments")
    op.drop_table("postpartum_assessments")
