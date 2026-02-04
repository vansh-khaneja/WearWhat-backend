"""initial schema

Revision ID: cf657ebf13e3
Revises: 
Create Date: 2026-02-04 20:05:59.645290

"""

from alembic import op

revision = 'cf657ebf13e3'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Read and execute schema.sql
    with open("schema.sql", "r") as f:
        op.execute(f.read())

def downgrade():
    # Dangerous but OK for first migration
    op.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
