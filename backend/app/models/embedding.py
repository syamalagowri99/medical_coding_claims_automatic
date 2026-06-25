import os
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db.database import Base


class Embedding(Base):
    """Vector embeddings for semantic search using pgvector."""
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False, index=True)  # document, entity, claim, etc.
    entity_id = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)  # Original text content
    embedding = Column(Vector(1536), nullable=False)  # OpenAI text-embedding-3-small produces 1536 dimensions
    meta_data = Column(Text)  # JSON metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Add index for efficient vector similarity search
    __table_args__ = (
        Index('ix_embedding_entity', 'entity_type', 'entity_id'),
        Index('ix_embedding_created', 'created_at'),
    )
