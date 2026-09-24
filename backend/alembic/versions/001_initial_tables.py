"""001_initial_tables

Revision ID: 001_initial_tables
Revises: 
Create Date: 2026-09-23 20:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. rfqs
    op.create_table(
        'rfqs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('reference_id', sa.String(length=100), nullable=False),
        sa.Column('pickup_service_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('buyer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('bid_start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('bid_close_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('forced_bid_close_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_rfqs_reference_id'), 'rfqs', ['reference_id'], unique=True)
    op.create_index(op.f('ix_rfqs_status'), 'rfqs', ['status'], unique=False)
    op.create_index(op.f('ix_rfqs_buyer_id'), 'rfqs', ['buyer_id'], unique=False)

    # 3. auction_configurations
    op.create_table(
        'auction_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('rfq_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('rfqs.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('british_auction_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('trigger_window_minutes', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('extension_duration_minutes', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('extension_trigger_type', sa.String(length=50), nullable=False, server_default='BID_RECEIVED'),
        sa.Column('current_close_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('extension_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_auction_configurations_rfq_id'), 'auction_configurations', ['rfq_id'], unique=True)

    # 4. bids
    op.create_table(
        'bids',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('rfq_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('rfqs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('carrier_name', sa.String(length=255), nullable=False),
        sa.Column('freight_charges', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('origin_charges', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('destination_charges', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('transit_time_days', sa.Integer(), nullable=False),
        sa.Column('validity_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_bids_rfq_id'), 'bids', ['rfq_id'], unique=False)
    op.create_index(op.f('ix_bids_supplier_id'), 'bids', ['supplier_id'], unique=False)
    op.create_index(op.f('ix_bids_total_amount'), 'bids', ['total_amount'], unique=False)
    op.create_index(op.f('ix_bids_created_at'), 'bids', ['created_at'], unique=False)

    # 5. activity_logs
    op.create_table(
        'activity_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('rfq_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('rfqs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('bid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bids.id', ondelete='SET NULL'), nullable=True),
        sa.Column('old_close_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('new_close_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('extension_reason', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_activity_logs_rfq_id'), 'activity_logs', ['rfq_id'], unique=False)
    op.create_index(op.f('ix_activity_logs_event_type'), 'activity_logs', ['event_type'], unique=False)
    op.create_index(op.f('ix_activity_logs_created_at'), 'activity_logs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('activity_logs')
    op.drop_table('bids')
    op.drop_table('auction_configurations')
    op.drop_table('rfqs')
    op.drop_table('users')
