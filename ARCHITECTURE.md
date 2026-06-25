# AI_Learnings-Main: Medical Coding & Claims Automation System - Architecture

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND LAYER (React)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Dashboard  │  │    Claims    │  │   Patients   │  │   Documents  │   │
│  │    (UI)      │  │    (UI)      │  │    (UI)      │  │    (UI)      │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ React Query (TanStack Query) - Data Fetching & Caching           │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ Axios HTTP Client - API Communication (No API Key stored)        │    │
│  │ Base URL: http://localhost:8000/api/v1                           │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│  Technology: React 18, Vite, TailwindCSS, Lucide Icons, React Router v6    │
│  Port: 5173                                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ║
                                    ║ HTTPS/JSON
                                    ║
┌─────────────────────────────────────────────────────────────────────────────┐
│                    API GATEWAY / CORS LAYER                                 │
│              (FastAPI CORS Middleware - No credentials exposed)             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ║
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BACKEND LAYER (FastAPI)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ API LAYER (RESTful Endpoints)                                      │   │
│  │ ├─ POST   /claims - Create claim                                  │   │
│  │ ├─ GET    /claims/{id} - Get claim details                        │   │
│  │ ├─ POST   /claims/{id}/validate - Validate claim (calls LLM)      │   │
│  │ ├─ POST   /claims/{id}/submit - Submit claim                      │   │
│  │ ├─ POST   /claims/{id}/approve - Approve claim                    │   │
│  │ ├─ POST   /claims/{id}/reject - Reject claim                      │   │
│  │ ├─ POST   /documents/upload - Upload medical documents            │   │
│  │ ├─ POST   /documents/{id}/extract - Extract data from document    │   │
│  │ ├─ GET    /patients - Get patient list                            │   │
│  │ └─ POST   /auth/login - JWT authentication                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ BUSINESS LOGIC LAYER (Services)                                   │   │
│  │                                                                    │   │
│  │ ┌──────────────────────┐  ┌──────────────────────┐               │   │
│  │ │ claim_service.py     │  │ document_service.py  │               │   │
│  │ ├─ create_claim()      │  ├─ process_document() │               │   │
│  │ ├─ validate_claim()    │  ├─ extract_entities() │               │   │
│  │ ├─ submit_claim()      │  └─ generate_summary() │               │   │
│  │ ├─ approve_claim()     │                        │               │   │
│  │ ├─ reject_claim()      │  ┌──────────────────────┐               │   │
│  │ └─ update_claim()      │  │ llm_service.py       │               │   │
│  │                        │  ├─ validate_claim()   │               │   │
│  │ ┌──────────────────────┐  ├─ extract_entities() │               │   │
│  │ │ auth_service.py      │  ├─ suggest_codes()    │               │   │
│  │ ├─ authenticate()      │  ├─ explain_code()     │               │   │
│  │ ├─ verify_token()      │  └─ generate_embedding()               │   │
│  │ └─ create_token()      │                        │               │   │
│  │                        │  ┌──────────────────────┐               │   │
│  │                        │  │ extraction_pipeline  │               │   │
│  │                        │  │ .py                  │               │   │
│  │                        │  └─ Multi-step NLP     │               │   │
│  │                        │    pipeline            │               │   │
│  │ ┌──────────────────────┐  ┌──────────────────────┐               │   │
│  │ │ entity_service.py    │  │ code_service.py      │               │   │
│  │ └─ manage entities     │  └─ manage codes       │               │   │
│  └──────────────────────────────────────────────────┘               │   │
│                                                                       │   │
│  Port: 8000                                                          │   │
└─────────────────────────────────────────────────────────────────────┘   │
                                    ║
                ┌───────────────────╫───────────────────┐
                ║                   ║                   ║
┌───────────────────────┐  ┌──────────────────────┐  ┌───────────────────┐
│  SECRETS MANAGEMENT   │  │  DATABASE LAYER      │  │  AI/LLM LAYER     │
└───────────────────────┘  └──────────────────────┘  └───────────────────┘
        (Backend Only)              (Backend Only)         (Backend Only)
        │                           │                      │
        │ .env file                 │ PostgreSQL           │ Azure OpenAI
        │ JWT Secret                │                      │ API Key
        │ API Keys                  │                      │
        │                           │                      │
```

---

## 📋 Component Breakdown

### 1️⃣ FRONTEND (React + Vite)
**Location**: `/frontend`  
**Port**: 5173  
**Key Technologies**: React 18, Vite, TailwindCSS, React Query, Axios

#### Structure:
```
frontend/
├── src/
│   ├── pages/               # Page components (Claims, Patients, Documents, etc.)
│   ├── components/          # Reusable UI components (Button, Card, Input)
│   ├── hooks/               # Custom React hooks (useAuth)
│   ├── services/
│   │   └── api.js          # Axios instance - communicates with backend
│   ├── utils/               # Utility functions
│   └── styles/              # Tailwind CSS configuration
├── vite.config.js          # Vite bundler configuration
└── package.json            # Dependencies: react, react-query, axios, tailwind
```

#### Key API Calls:
```javascript
// api.js - All API calls go through here
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1'
});

claimAPI = {
  getById: (id) => api.get(`/claims/${id}`),
  validate: (id) => api.post(`/claims/${id}/validate`),
  submit: (id) => api.post(`/claims/${id}/submit`),
  approveClaim: (id) => api.post(`/claims/${id}/approve`),
  // ...
}
```

**IMPORTANT**: No API keys, LLM endpoints, or secrets stored in frontend!

---

### 2️⃣ BACKEND (FastAPI + Python)
**Location**: `/backend`  
**Port**: 8000  
**Framework**: FastAPI 0.109+  
**Python**: 3.11+

#### Architecture Layers:

##### A. API Layer (`/app/api`)
- RESTful endpoints exposing business logic
- JWT authentication on all routes
- Dependency injection via FastAPI `Depends()`
- OpenAPI/Swagger documentation at `http://localhost:8000/docs`

##### B. Business Logic Layer (`/app/services`)

**`claim_service.py`**:
```python
- create_claim(db, claim, user_id)        → Create new claim
- validate_claim(db, claim_id)            → Call LLM to validate
- submit_claim(db, claim_id)              → Change status to SUBMITTED
- approve_claim(db, claim_id, user_id)    → Change status to APPROVED
- reject_claim(db, claim_id, user_id)     → Change status to DENIED
- get_claim(db, claim_id)                 → Retrieve claim details
```

**`llm_service.py`**:
```python
- validate_claim(claim_data)              → Call Azure OpenAI
- extract_entities(text)                  → Extract medical entities using LLM
- suggest_codes(description)              → Suggest ICD-10/CPT codes
- explain_code(code)                      → Explain medical code
- generate_embedding(text)                → Create vector embedding (pgvector)
- ping()                                  → Test Azure OpenAI connectivity
```

**`document_service.py`**:
```python
- process_document(file)                  → Upload and analyze medical document
- extract_entities(document)              → Extract data using Azure Document Intelligence
- generate_summary(document)              → Create document summary
```

**`auth_service.py`**:
```python
- authenticate_user(username, password)   → Verify credentials
- create_access_token(user_id)            → Generate JWT token
- verify_token(token)                     → Validate JWT
```

##### C. Data Layer (`/app/models`)
SQLAlchemy ORM Models:

```python
class User:
  ├─ id, username, email
  ├─ hashed_password
  └─ role (admin, doctor, coder)

class Patient:
  ├─ patient_id, first_name, last_name
  ├─ date_of_birth, gender
  ├─ email, phone, address
  └─ → links to Claims

class Claim:
  ├─ id, claim_number
  ├─ patient_id → FK(Patient)
  ├─ status (DRAFT, SUBMITTED, PROCESSING, APPROVED, DENIED, PAID)
  ├─ total_amount, insurance_provider, policy_number
  ├─ rendering_provider_npi, place_of_service
  ├─ submission_date, processing_date
  ├─ claim_items → relationship(ClaimItem)
  └─ validations → relationship(ClaimValidation)

class ClaimItem:
  ├─ id, claim_id → FK(Claim)
  ├─ description, procedure_code (CPT), diagnosis_code (ICD-10)
  ├─ service_date_start, service_date_end
  ├─ amount, quantity, units
  └─ code_id → FK(MedicalCode)

class ClaimValidation:
  ├─ id, claim_id → FK(Claim)
  ├─ validation_type (documentation, coding, medical_necessity, compliance)
  ├─ error_message
  ├─ severity (error, warning, info)
  └─ is_valid

class Document:
  ├─ id, claim_id → FK(Claim)
  ├─ file_name, file_path
  ├─ uploaded_by → FK(User)
  ├─ extracted_text, extracted_entities
  └─ processing_status (pending, processed, failed)

class MedicalCode:
  ├─ code (ICD-10, CPT, HCPCS)
  ├─ code_system
  ├─ description
  ├─ status (SUGGESTED, APPROVED, REJECTED)
  └─ approved_by → FK(User)

class ExtractedEntity:
  ├─ entity_type (medication, diagnosis, procedure)
  ├─ entity_value
  ├─ confidence_score
  └─ document_id → FK(Document)

class AuditLog:
  ├─ action (CREATE, UPDATE, APPROVE, REJECT, SUBMIT)
  ├─ entity_type, entity_id
  ├─ changed_by → FK(User)
  ├─ old_value, new_value
  └─ timestamp
```

##### D. Configuration Layer (`/app/core`)

**`config.py`** - Environment-based settings:
```python
# Database
DATABASE_URL = "postgresql://user:pwd@localhost:5432/medical_coding"

# LLM - Azure OpenAI (Backend Only!)
AZURE_OPENAI_ENDPOINT = "https://pkvaidemo.services.ai.azure.com/openai/v1"
AZURE_OPENAI_API_KEY = "BHwCZ0xmIUgGFfvrK1SHpWd56hTSF0Oottj9eVww5HxtYrUjgrC3JQQJ99CEACYeBjFXJ3w3AAAAACOGB7Yk"
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-5.4"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = "text-embedding-3-small"
AZURE_OPENAI_API_VERSION = "2024-02-01"

# Document Intelligence (OCR)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = "https://..."
AZURE_DOCUMENT_INTELLIGENCE_API_KEY = "..."

# Security
SECRET_KEY = "jwt-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7 days
ALGORITHM = "HS256"

# CORS
BACKEND_CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

# File Upload
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = [".pdf", ".txt", ".docx"]
```

**`security.py`** - JWT token handling:
```python
def create_access_token(user_id: int) → str
def verify_token(token: str) → int (user_id)
def get_current_active_user() → User (FastAPI Depends)
```

**`deps.py`** - Dependency injection:
```python
get_db() → Session (database session)
get_current_active_user() → User (authenticated user)
```

---

### 3️⃣ DATABASE LAYER (PostgreSQL)
**Location**: localhost:5433  
**Database Name**: medical_coding  
**Extensions**: pgvector (vector embeddings)

#### Tables:
```
┌─────────────────┐
│   users         │ Authentication & audit trail
├─────────────────┤
│ id (PK)         │
│ username        │
│ email           │
│ hashed_password │
│ role            │
└─────────────────┘

┌─────────────────┐
│   patients      │ Patient demographics
├─────────────────┤
│ id (PK)         │
│ patient_id      │
│ first_name      │
│ last_name       │
│ date_of_birth   │
└─────────────────┘

┌──────────────────┐
│   claims         │ Main claim records
├──────────────────┤
│ id (PK)          │
│ claim_number     │
│ patient_id (FK)  │
│ status           │
│ total_amount     │
│ insurance_prov   │
│ policy_number    │
│ npi              │
│ place_of_service │
│ submission_date  │
└──────────────────┘

┌──────────────────┐
│   claim_items    │ Line items in claims
├──────────────────┤
│ id (PK)          │
│ claim_id (FK)    │
│ procedure_code   │
│ diagnosis_code   │
│ service_date_*   │
│ amount           │
│ quantity         │
└──────────────────┘

┌──────────────────┐
│ claim_validations│ Validation results from LLM
├──────────────────┤
│ id (PK)          │
│ claim_id (FK)    │
│ validation_type  │
│ error_message    │
│ severity         │
└──────────────────┘

┌──────────────────┐
│   documents      │ Uploaded medical docs
├──────────────────┤
│ id (PK)          │
│ claim_id (FK)    │
│ file_name        │
│ extracted_text   │
└──────────────────┘

┌──────────────────┐
│extracted_entities│ Entities from LLM + NLP
├──────────────────┤
│ id (PK)          │
│ document_id (FK) │
│ entity_type      │
│ entity_value     │
│ confidence_score │
└──────────────────┘

┌──────────────────┐
│   medical_codes  │ Suggested/approved codes
├──────────────────┤
│ id (PK)          │
│ code (ICD-10/CPT)│
│ description      │
│ status           │
│ approved_by (FK) │
└──────────────────┘

┌──────────────────┐
│   audit_logs     │ HIPAA compliance
├──────────────────┤
│ id (PK)          │
│ action           │
│ entity_type      │
│ entity_id        │
│ changed_by (FK)  │
│ old_value        │
│ new_value        │
└──────────────────┘
```

#### Connection:
```python
DATABASE_URL = "postgresql://medical_user:medical_password@localhost:5433/medical_coding"
Engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=Engine)
```

---

### 4️⃣ LLM INTEGRATION LAYER (Azure OpenAI)
**Provider**: Microsoft Azure OpenAI  
**Model**: GPT-5.4 (gpt-5.4 deployment)  
**Embedding Model**: text-embedding-3-small  

#### Configuration (.env):
```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://pkvaidemo.services.ai.azure.com/openai/v1
AZURE_OPENAI_API_KEY=BHwCZ0xmIUgGFfvrK1SHpWd56hTSF0Oottj9eVww5HxtYrUjgrC3JQQJ99CEACYeBjFXJ3w3AAAAACOGB7Yk
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-02-01
```

#### Usage in Backend (`llm_service.py`):

```python
from azure.ai.openai import AzureOpenAI

class LLMService:
    def __init__(self, settings):
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
    
    def validate_claim(self, claim_data: dict) → dict:
        """
        Sends claim to Azure OpenAI for validation.
        Returns JSON with validations grouped by category:
        - documentation: Missing/incomplete fields
        - coding: ICD-10/CPT code issues
        - medical_necessity: Clinical justification issues
        - compliance: Regulatory compliance issues
        """
        prompt = f"""
        Validate this medical claim:
        {json.dumps(claim_data, indent=2)}
        
        Return JSON with validation_type, error_message, severity
        """
        
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        return json.loads(response.choices[0].message.content)
    
    def generate_embedding(self, text: str) → list:
        """
        Generates vector embedding for semantic search in pgvector.
        Stored in database for RAG (Retrieval Augmented Generation).
        """
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_deployment_name
        )
        return response.data[0].embedding
```

#### LLM Workflow:
```
User submits claim
        ↓
Backend receives POST /claims/{id}/validate
        ↓
Call llm_service.validate_claim(claim_data)
        ↓
Send HTTP request to Azure OpenAI endpoint with API key
        ↓
Azure OpenAI processes with GPT-5.4 model
        ↓
Returns JSON: {
  "validations": [
    {
      "validation_type": "documentation",
      "error_message": "Missing NPI",
      "severity": "warning"
    },
    ...
  ]
}
        ↓
Store results in ClaimValidation table
        ↓
Return to frontend with validation results
        ↓
Frontend displays grouped by category in UI
```

---

### 5️⃣ API KEY & SECURITY ARCHITECTURE

#### Secret Management Strategy:
```
┌─────────────────────────────────────────────────────────┐
│            SECRETS NEVER EXPOSED TO FRONTEND            │
└─────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Backend            Database         LLM
    (Secured)         (Secured)       (Secured)
        │                │                │
    .env file      PostgreSQL      Azure OpenAI
    (localhost:8000)  (localhost:5433)  (cloud)
        │                │                │
    ├─ DATABASE_URL    ├─ Password    ├─ API Key
    ├─ JWT SECRET      ├─ CORS rules  ├─ Endpoint
    ├─ API KEYS        └─ pgvector    └─ Deployment
    └─ LLM KEYS           extension       name
```

#### Key Files:
- **`.env`** (Git-ignored):
  ```
  DATABASE_URL=postgresql://medical_user:pwd@localhost:5433/medical_coding
  AZURE_OPENAI_API_KEY=BHwCZ0xmIUgGFfvrK1SHpWd56hTSF0Oottj9eVww5HxtYrUjgrC3JQQJ99CEACYeBjFXJ3w3AAAAACOGB7Yk
  AZURE_OPENAI_ENDPOINT=https://pkvaidemo.services.ai.azure.com/openai/v1
  SECRET_KEY=your-jwt-secret
  ```

- **Frontend only gets**: JWT token (for session)
- **Backend always controls**: All API keys, DB credentials, LLM calls

#### JWT Flow:
```
1. Frontend: POST /auth/login {username, password}
2. Backend: Verify credentials → Generate JWT token
3. Backend: Return JWT to frontend
4. Frontend: Store JWT in memory (not localStorage for security)
5. Frontend: Include JWT in all requests: Authorization: Bearer <JWT>
6. Backend: Verify JWT on each request
7. Backend: Never expose API keys to frontend
```

---

## 🔄 Request/Response Flow Example

### Example: Claim Validation & Submission

```
1. FRONTEND (React Component)
   ┌────────────────────────────────────┐
   │ ClaimDetails.jsx                   │
   │ ├─ User clicks "Validate" button   │
   │ └─ claimAPI.validate(claimId)      │
   └────────────────────────────────────┘
                    │
                    │ POST /claims/{id}/validate
                    │ Header: Authorization: Bearer JWT
                    │
2. BACKEND (FastAPI)
   ┌────────────────────────────────────┐
   │ api/claims.py                      │
   │ ├─ @router.post("/validate")       │
   │ ├─ verify JWT token                │
   │ ├─ call validate_claim_endpoint()  │
   │ └─ get_current_active_user()       │
   └────────────────────────────────────┘
                    │
                    │ Service call
                    │
3. BACKEND (Service Layer)
   ┌────────────────────────────────────┐
   │ services/claim_service.py          │
   │ ├─ validate_claim(db, claim_id)    │
   │ ├─ gather claim_data               │
   │ ├─ call llm_service.validate_claim │
   └────────────────────────────────────┘
                    │
                    │ LLM call
                    │
4. BACKEND (LLM Service)
   ┌────────────────────────────────────┐
   │ services/llm_service.py            │
   │ ├─ validate_claim(claim_data)      │
   │ ├─ HTTP POST to Azure OpenAI       │
   │ │  URL: .../deployments/gpt-5.4/   │
   │ │        chat/completions?api-ver..│
   │ │  Header: api-key: AZURE_KEY      │
   │ │  Body: {messages, model, params} │
   │ └─ Parse response                  │
   └────────────────────────────────────┘
                    │
                    │ API Response
                    │
5. BACKEND (Database)
   ┌────────────────────────────────────┐
   │ Store validation results:          │
   │ INSERT INTO claim_validations      │
   │ (claim_id, validation_type,        │
   │  error_message, severity)          │
   │                                    │
   │ UPDATE claims                      │
   │ SET status = 'SUBMITTED'           │
   │ (if no blocking errors)            │
   └────────────────────────────────────┘
                    │
                    │ JSON Response
                    │
6. FRONTEND (React Query)
   ┌────────────────────────────────────┐
   │ Invalidate queries                 │
   │ Refetch claim data                 │
   │ Display validation results grouped │
   │ by category:                       │
   │ - 📄 Documentation (blue)          │
   │ - 💻 Coding (orange)               │
   │ - 🏥 Medical Necessity (red)       │
   │ - ⚖️ Compliance (purple)           │
   │ - ⚠️ Other (yellow)                │
   └────────────────────────────────────┘
```

---

## 📊 Claim Status Workflow

```
┌──────┐
│DRAFT │ (User creates claim)
└──────┘
   │
   ├─ Click "Validate" → LLM validation
   │
   ├─ Click "Submit" → status = SUBMITTED
   │
┌──────────────┐
│   SUBMITTED  │
└──────────────┘
   │
   ├─ Admin reviews validations
   │
   ├─ Click "Approve"
   │        ↓
   │  ┌──────────┐
   │  │ APPROVED │ → Ready for payment
   │  └──────────┘
   │
   └─ Click "Reject" + reason
            ↓
      ┌──────────┐
      │  DENIED  │ → Claims rejected
      └──────────┘

Optional: PROCESSING state (during review)
```

---

## 🛡️ Security Best Practices

| Layer | Security |
|-------|----------|
| **Frontend** | No secrets stored. JWT in memory only. HTTPS only. |
| **API** | JWT authentication on all endpoints. CORS restricted. |
| **Backend** | Secrets in `.env` (Git-ignored). Async SSL patching. |
| **Database** | Username/password auth. Encrypted connections. |
| **LLM** | API key backend-only. Endpoint never exposed. |
| **Audit** | All actions logged with user, timestamp, changes. |

---

## 📦 Deployment Architecture

```
Production:
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐ │
│ │   Frontend  │  │   Backend   │  │  PostgreSQL +    │ │
│ │  Container  │  │  Container  │  │  pgvector        │ │
│ │             │  │             │  │  Container       │ │
│ │  Vite       │  │  FastAPI    │  │                  │ │
│ │  Nginx      │  │  Gunicorn   │  │  medical_coding  │ │
│ │  Port 80    │  │  Port 8000  │  │  Port 5432       │ │
│ └─────────────┘  └─────────────┘  └──────────────────┘ │
│       ↑               ↑                    ↑             │
│       │ HTTP          │ HTTPS              │ Internal    │
│       └───────────────┴────────────────────┘             │
│                                                          │
│  External: Azure OpenAI (HTTPS calls)                   │
│  External: Azure Document Intelligence (OCR)           │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Summary Table

| Component | Technology | Purpose | Port |
|-----------|-----------|---------|------|
| **Frontend** | React 18, Vite, TailwindCSS | User interface | 5173 |
| **Backend** | FastAPI, SQLAlchemy, Pydantic | Business logic, APIs | 8000 |
| **Database** | PostgreSQL + pgvector | Persistent data storage | 5433 |
| **LLM** | Azure OpenAI (GPT-5.4) | AI validation & suggestions | Cloud |
| **OCR** | Azure Document Intelligence | Medical document extraction | Cloud |
| **Auth** | JWT (HS256) | Token-based authentication | Backend |
| **Validation** | LLM + Custom Rules | Claim validation | Backend |
| **Audit** | audit_logs table | Compliance tracking | DB |

---

## 🚀 Startup Sequence

1. **Database**: `docker run -d postgres:15-alpine` → pgvector
2. **Backend**: `cd backend && uvicorn app.main:app --reload`
3. **Frontend**: `cd frontend && npm run dev`
4. **Access**:
   - UI: http://localhost:5173
   - API Docs: http://localhost:8000/docs
   - API Health: http://localhost:8000/health

---

## 📝 Key Concepts

- **Claim**: Medical billing document with line items, validations
- **LLM Integration**: Validation logic powered by Azure OpenAI
- **RAG**: Vector embeddings stored in pgvector for semantic search
- **MCP**: Model Context Protocol for multi-step AI workflows
- **HIPAA**: Audit logging for compliance
- **JWT**: Stateless authentication between frontend & backend

This architecture ensures **security** (secrets backend-only), **scalability** (microservices-ready), and **maintainability** (layered design).
