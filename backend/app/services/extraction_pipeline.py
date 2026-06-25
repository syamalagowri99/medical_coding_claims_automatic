"""
Enhanced document extraction and semantic retrieval pipeline.
Handles text extraction, entity recognition, embedding generation, and vector similarity search.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.document import Document
from app.models.embedding import Embedding
from app.models.entity import ExtractedEntity
from app.services.llm_service import llm_service
from app.services.document_service import extract_text_from_pdf, extract_text_from_docx
from typing import List, Dict, Optional
import json


class ExtractionPipeline:
    """Pipeline for document extraction, processing, and semantic retrieval."""
    
    @staticmethod
    def extract_text(file_content: bytes, file_type: str) -> str:
        """Extract text from various file types."""
        if file_type == ".pdf":
            return extract_text_from_pdf(file_content)
        elif file_type == ".docx":
            return extract_text_from_docx(file_content)
        else:
            return file_content.decode("utf-8", errors="ignore")
    
    @staticmethod
    def generate_document_embedding(db: Session, document_id: int, text: str) -> Optional[Embedding]:
        """Generate and store embedding for a document using backend API only."""
        try:
            # Generate embedding using backend LLM service (API key is backend-only)
            embedding_vector = llm_service.generate_embedding(text[:8000])
            
            # Store embedding in pgvector
            doc_embedding = Embedding(
                entity_type="document",
                entity_id=document_id,
                content=text[:4000],
                embedding=embedding_vector,
                meta_data=json.dumps({"source": "document_extraction", "version": 1})
            )
            db.add(doc_embedding)
            db.commit()
            db.refresh(doc_embedding)
            return doc_embedding
        except Exception as e:
            print(f"Warning: Failed to generate embedding for document {document_id}: {str(e)}")
            return None
    
    @staticmethod
    def semantic_search(
        db: Session,
        query: str,
        entity_type: str = "document",
        limit: int = 5,
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Perform semantic similarity search using pgvector.
        Returns documents/entities similar to the query.
        """
        try:
            # Generate query embedding using backend LLM service
            query_embedding = llm_service.generate_embedding(query)
            
            # Convert to string format for pgvector similarity search
            embedding_str = "[" + ",".join([str(x) for x in query_embedding]) + "]"
            
            # Use pgvector's <-> operator for cosine distance similarity
            # Lower distance = higher similarity (returns as distance, not similarity)
            results = db.execute(text("""
                SELECT id, entity_type, entity_id, content, meta_data,
                       (1 - (embedding <-> :query_embedding::vector)) as similarity
                FROM embeddings
                WHERE entity_type = :entity_type
                  AND (1 - (embedding <-> :query_embedding::vector)) > :threshold
                ORDER BY embedding <-> :query_embedding::vector
                LIMIT :limit
            """), {
                "query_embedding": embedding_str,
                "entity_type": entity_type,
                "threshold": threshold,
                "limit": limit
            }).fetchall()
            
            return [
                {
                    "id": r[0],
                    "entity_type": r[1],
                    "entity_id": r[2],
                    "content": r[3],
                    "metadata": json.loads(r[4]) if r[4] else {},
                    "similarity": float(r[5])
                }
                for r in results
            ]
        except Exception as e:
            print(f"Error performing semantic search: {str(e)}")
            return []
    
    @staticmethod
    def find_similar_documents(db: Session, document_id: int, limit: int = 5) -> List[Dict]:
        """Find documents similar to a given document using vector similarity."""
        try:
            # Get the document's embedding
            doc_embedding = db.query(Embedding).filter(
                Embedding.entity_type == "document",
                Embedding.entity_id == document_id
            ).first()
            
            if not doc_embedding:
                return []
            
            # Find similar embeddings using pgvector distance
            embedding_str = "[" + ",".join([str(x) for x in doc_embedding.embedding]) + "]"
            
            results = db.execute(text("""
                SELECT e.id, e.entity_id, e.content, e.meta_data,
                       (1 - (e.embedding <-> :query_embedding::vector)) as similarity
                FROM embeddings e
                WHERE e.entity_type = 'document'
                  AND e.entity_id != :document_id
                  AND (1 - (e.embedding <-> :query_embedding::vector)) > 0.5
                ORDER BY e.embedding <-> :query_embedding::vector
                LIMIT :limit
            """), {
                "query_embedding": embedding_str,
                "document_id": document_id,
                "limit": limit
            }).fetchall()
            
            return [
                {
                    "embedding_id": r[0],
                    "document_id": r[1],
                    "content": r[2],
                    "metadata": json.loads(r[3]) if r[3] else {},
                    "similarity": float(r[4])
                }
                for r in results
            ]
        except Exception as e:
            print(f"Error finding similar documents: {str(e)}")
            return []


# Global pipeline instance
extraction_pipeline = ExtractionPipeline()
