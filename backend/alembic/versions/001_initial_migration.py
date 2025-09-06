"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('subscription_tier', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create broker_accounts table
    op.create_table('broker_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('broker_name', sa.String(length=50), nullable=False),
        sa.Column('account_id', sa.String(length=100), nullable=False),
        sa.Column('api_key_encrypted', sa.Text(), nullable=True),
        sa.Column('api_secret_encrypted', sa.Text(), nullable=True),
        sa.Column('access_token_encrypted', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_paper_trading', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create market_data table
    op.create_table('market_data',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('exchange', sa.String(length=20), nullable=False),
        sa.Column('open', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('high', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('low', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('close', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('volume', sa.Integer(), nullable=False),
        sa.Column('vwap', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('timeframe', sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint('time', 'symbol')
    )
    
    # Create orders table
    op.create_table('orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('broker_account_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('exchange', sa.String(length=20), nullable=False),
        sa.Column('order_type', sa.String(length=20), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('filled_quantity', sa.Integer(), nullable=True),
        sa.Column('average_price', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('order_id_broker', sa.String(length=100), nullable=True),
        sa.Column('strategy_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['broker_account_id'], ['broker_accounts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create positions table
    op.create_table('positions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('broker_account_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('exchange', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('average_price', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('current_price', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('unrealized_pnl', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('realized_pnl', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['broker_account_id'], ['broker_accounts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_market_data_symbol_time', 'market_data', ['symbol', 'time'])
    op.create_index('idx_orders_user_id', 'orders', ['user_id'])
    op.create_index('idx_positions_user_id', 'positions', ['user_id'])

def downgrade():
    op.drop_index('idx_positions_user_id', table_name='positions')
    op.drop_index('idx_orders_user_id', table_name='orders')
    op.drop_index('idx_market_data_symbol_time', table_name='market_data')
    op.drop_table('positions')
    op.drop_table('orders')
    op.drop_table('market_data')
    op.drop_table('broker_accounts')
    op.drop_table('users')
