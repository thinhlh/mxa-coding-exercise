"""initial schema

Revision ID: d3363915e42f
Revises: 
Create Date: 2026-09-14 15:23:54.549969
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd3363915e42f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('employees',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('display_name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('projects',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('code', sa.String(length=6), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('manager_id', sa.UUID(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['manager_id'], ['employees.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('timesheets',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('employee_id', sa.UUID(), nullable=False),
    sa.Column('week_start', sa.Date(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('submit_message', sa.String(), nullable=True),
    sa.Column('review_message', sa.String(), nullable=True),
    sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('reviewed_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
    sa.ForeignKeyConstraint(['reviewed_by'], ['employees.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('employee_id', 'week_start')
    )
    op.create_table('timesheet_line_items',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('timesheet_id', sa.UUID(), nullable=False),
    sa.Column('project_id', sa.UUID(), nullable=False),
    sa.Column('hours_monday', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('hours_tuesday', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('hours_wednesday', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('hours_thursday', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('hours_friday', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('hours_saturday', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('hours_sunday', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['timesheet_id'], ['timesheets.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('timesheet_id', 'project_id')
    )


def downgrade() -> None:
    op.drop_table('timesheet_line_items')
    op.drop_table('timesheets')
    op.drop_table('projects')
    op.drop_table('employees')
