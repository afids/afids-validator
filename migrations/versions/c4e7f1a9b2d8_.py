"""Add knowledge_chunks table for RAG vector store

Revision ID: c4e7f1a9b2d8
Revises: 56d89145adbb
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c4e7f1a9b2d8"
down_revision = "56d89145adbb"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=256), nullable=False),
        sa.Column("landmark_tag", sa.String(length=32), nullable=True),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        # JSON-encoded float list (embedding vector).
        # For production deployments with large knowledge bases this can be
        # migrated to pgvector's native vector type and an HNSW index added:
        #   ALTER TABLE knowledge_chunks
        #     ADD COLUMN embedding vector(1536)
        #     GENERATED ALWAYS AS (embedding_json::vector) STORED;
        #   CREATE INDEX ON knowledge_chunks
        #     USING hnsw (embedding vector_cosine_ops);
        sa.Column("embedding_json", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_knowledge_chunks_landmark_tag",
        "knowledge_chunks",
        ["landmark_tag"],
        unique=False,
    )
    op.create_index(
        "ix_knowledge_chunks_source",
        "knowledge_chunks",
        ["source"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_knowledge_chunks_source", table_name="knowledge_chunks")
    op.drop_index(
        "ix_knowledge_chunks_landmark_tag", table_name="knowledge_chunks"
    )
    op.drop_table("knowledge_chunks")
