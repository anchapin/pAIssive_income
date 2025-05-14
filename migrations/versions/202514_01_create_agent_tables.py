"""create agent and agent_action tables

Revision ID: 20240601_01
Revises:
Create Date: 2024-06-01 10:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '20240601_01'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    CREATE TABLE IF NOT EXISTS agent (
        id SERIAL PRIMARY KEY,
        name TEXT,
        avatar_url TEXT,
        description TEXT
        -- Add other columns as needed
    );
    """)
    op.execute("""
    CREATE TABLE IF NOT EXISTS agent_action (
        id SERIAL PRIMARY KEY,
        agent_id INTEGER REFERENCES agent(id),
        action_type TEXT,
        action_payload JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

def downgrade():
    op.execute("DROP TABLE IF EXISTS agent_action;")
    op.execute("DROP TABLE IF EXISTS agent;")