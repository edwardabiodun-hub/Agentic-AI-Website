"""Create initial evidence tables."""

import sqlalchemy as sa

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "data_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("site_id", sa.String(length=200), nullable=False),
        sa.Column("fingerprint", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("errors", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("site_id", "fingerprint", name="uq_run_fingerprint"),
    )
    op.create_index("ix_data_runs_site_id", "data_runs", ["site_id"])
    op.create_index("ix_data_runs_fingerprint", "data_runs", ["fingerprint"])
    op.create_table(
        "observations",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dimensions", sa.JSON(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("evidence_ref", sa.String(length=300), nullable=False),
    )
    op.create_index("ix_observations_run_id", "observations", ["run_id"])
    op.create_index("ix_observations_source", "observations", ["source"])


def downgrade() -> None:
    op.drop_index("ix_observations_source", table_name="observations")
    op.drop_index("ix_observations_run_id", table_name="observations")
    op.drop_table("observations")
    op.drop_index("ix_data_runs_fingerprint", table_name="data_runs")
    op.drop_index("ix_data_runs_site_id", table_name="data_runs")
    op.drop_table("data_runs")
