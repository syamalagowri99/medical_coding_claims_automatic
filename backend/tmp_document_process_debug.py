from app.db.database import SessionLocal
from app.services.document_service import create_document, process_document
from app.schemas.document import DocumentCreate
from app.models.document import DocumentType

path = r'C:\Users\jgowri\Downloads\Dummy_Medical_Report_2.pdf'
with open(path, 'rb') as f:
    content = f.read()

session = SessionLocal()
try:
    doc_create = DocumentCreate(patient_id=1, filename='Dummy_Medical_Report_2.pdf', document_type=DocumentType.LAB_RESULT)
    doc = create_document(
        db=session,
        document=doc_create,
        file_content=content,
        file_type='.pdf',
        file_size=len(content),
        uploaded_by=3,
    )
    print('created', doc.id, doc.status)
    processed = process_document(session, doc.id)
    print('processed', processed.id, processed.status)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    session.close()
