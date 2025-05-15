"""fix agent tables naming

Revision ID: 20240602_01
Revises: 20240601_01
Create Date: 2024-06-02 10:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20240602_01"
down_revision = "20240601_01"
branch_labels = None
depends_on = None


def upgrade():
    # Create the singular form tables that the API server is expecting
    op.execute("""
    CREATE TABLE IF NOT EXISTS agent (
        id SERIAL PRIMARY KEY,
        name TEXT,
        avatar_url TEXT,
        description TEXT
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
    
    # Copy data from plural to singular if the plural tables exist
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'agents') THEN
            INSERT INTO agent (id, name, description)
            SELECT id, name, description FROM agents
            ON CONFLICT (id) DO NOTHING;
        END IF;
    END
    $$;
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS agent_action;")
    op.execute("DROP TABLE IF EXISTS agent;")
