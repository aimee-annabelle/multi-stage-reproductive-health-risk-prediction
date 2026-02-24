"""create pregnancy assessments table

Revision ID: 20260224_000002
Revises: 20260223_000001
Create Date: 2026-02-24 11:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260224_000002"
down_revision: Union[str, None] = "20260223_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pregnancy_assessments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("gestational_age_weeks", sa.Integer(), nullable=True),
        sa.Column("visit_label", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("systolic_bp", sa.Float(), nullable=False),
        sa.Column("diastolic", sa.Float(), nullable=False),
        sa.Column("bs", sa.Float(), nullable=True),
        sa.Column("body_temp", sa.Float(), nullable=True),
        sa.Column("bmi", sa.Float(), nullable=True),
        sa.Column("previous_complications", sa.Integer(), nullable=True),
        sa.Column("preexisting_diabetes", sa.Integer(), nullable=True),
        sa.Column("gestational_diabetes", sa.Integer(), nullable=True),
        sa.Column("mental_health", sa.Integer(), nullable=True),
        sa.Column("heart_rate", sa.Float(), nullable=True),
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
        "ix_pregnancy_assessments_user_id",
        "pregnancy_assessments",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_pregnancy_assessments_created_at",
        "pregnancy_assessments",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pregnancy_assessments_created_at", table_name="pregnancy_assessments")
    op.drop_index("ix_pregnancy_assessments_user_id", table_name="pregnancy_assessments")
    op.drop_table("pregnancy_assessments")
