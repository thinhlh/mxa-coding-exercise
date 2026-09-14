"""line item hours are integers

Revision ID: ef17c0ac0b23
Revises: d3363915e42f
Create Date: 2026-09-14 16:10:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'ef17c0ac0b23'
down_revision: Union[str, None] = 'd3363915e42f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

HOUR_COLUMNS = (
    'hours_monday',
    'hours_tuesday',
    'hours_wednesday',
    'hours_thursday',
    'hours_friday',
    'hours_saturday',
    'hours_sunday',
)


def upgrade() -> None:
    for column in HOUR_COLUMNS:
        op.alter_column(
            'timesheet_line_items',
            column,
            type_=sa.Integer(),
            existing_type=sa.Numeric(precision=4, scale=2),
            postgresql_using=f'round({column})::integer',
        )


def downgrade() -> None:
    for column in HOUR_COLUMNS:
        op.alter_column(
            'timesheet_line_items',
            column,
            type_=sa.Numeric(precision=4, scale=2),
            existing_type=sa.Integer(),
        )
