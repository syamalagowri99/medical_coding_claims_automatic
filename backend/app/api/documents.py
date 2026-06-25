from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.document import DocumentCreate, DocumentUpdate, Document, DocumentUploadResponse
from app.services.document_service import create_document, process_document, get_document, get_documents_by_patient, update_document
from app.core.deps import get_current_active_user
from app.models.user import User as UserModel
from app.core.config import settings

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    patient_id: int = Form(...),
    file: UploadFile = File(...),
    document_type: str = Form("other"),
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and process a medical document."""
    # Validate file type
    file_extension = file.filename.split('.')[-1].lower()
    if f".{file_extension}" not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type .{file_extension} not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}"
        )
    
    # Validate file size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    # Create document
    from app.models.document import DocumentType
    try:
        doc_type = DocumentType(document_type) if document_type != "other" else DocumentType.OTHER
    except ValueError:
        doc_type = DocumentType.OTHER
    
    document_create = DocumentCreate(
        patient_id=patient_id,
        filename=file.filename,
        document_type=doc_type
    )
    
    try:
        document = create_document(
            db=db,
            document=document_create,
            file_content=content,
            file_type=f".{file_extension}",
            file_size=len(content),
            uploaded_by=current_user.id
        )
        
        # Try to process document but don't fail upload if processing fails
        try:
            process_document(db, document.id)
        except Exception as process_err:
            print(f"Warning: Processing started for document {document.id} but encountered error: {str(process_err)}")
            # Document will still be available even if processing fails
        
        return DocumentUploadResponse(
            document_id=document.id,
            filename=document.filename,
            status=document.status.value,
            message="Document uploaded and processing started"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{document_id}", response_model=Document)
async def get_document_by_id(
    document_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get document by ID."""
    document = get_document(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


@router.get("/patient/{patient_id}", response_model=list[Document])
async def get_patient_documents(
    patient_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all documents for a patient."""
    return get_documents_by_patient(db, patient_id)


@router.get("/", response_model=list[Document])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all documents with pagination."""
    from app.models.document import Document as DocumentModel
    documents = db.query(DocumentModel).offset(skip).limit(limit).all()
    return documents


@router.put("/{document_id}", response_model=Document)
async def update_document_endpoint(
    document_id: int,
    document_update: DocumentUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update document information."""
    try:
        return update_document(db, document_id, document_update)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{document_id}/process", response_model=Document)
async def reprocess_document(
    document_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reprocess a document with the LLM service."""
    try:
        return process_document(db, document_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{document_id}/content")
async def get_document_content(
    document_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get document content (text) by ID."""
    document = get_document(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return {
        "id": document.id,
        "filename": document.filename,
        "content_text": document.content_text,
        "status": document.status.value
    }


@router.post("/search/semantic")
async def semantic_search(
    query: str,
    entity_type: str = "document",
    limit: int = 5,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Perform semantic similarity search across documents using vector embeddings.
    Backend-only API key usage for embedding generation.
    """
    try:
        from app.services.extraction_pipeline import extraction_pipeline
        results = extraction_pipeline.semantic_search(
            db=db,
            query=query,
            entity_type=entity_type,
            limit=limit,
            threshold=0.5
        )
        return {
            "query": query,
            "entity_type": entity_type,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )


@router.get("/{document_id}/similar")
async def get_similar_documents(
    document_id: int,
    limit: int = 5,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Find documents similar to a given document using vector similarity.
    Uses pgvector for efficient similarity search.
    """
    document = get_document(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        from app.services.extraction_pipeline import extraction_pipeline
        similar_docs = extraction_pipeline.find_similar_documents(
            db=db,
            document_id=document_id,
            limit=limit
        )
        return {
            "reference_document_id": document_id,
            "reference_filename": document.filename,
            "similar_documents": similar_docs,
            "count": len(similar_docs)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Similar document search failed: {str(e)}"
        )
