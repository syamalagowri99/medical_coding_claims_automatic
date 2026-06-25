# Medical Coding & Claims Automation System

A production-grade intelligent system for automating medical coding and claims processing using AI/LLM technologies.

## 🎯 Features

- **AI-Powered Medical Coding**: Automatically extracts medical entities from clinical documentation and suggests ICD-10, CPT, and HCPCS codes
- **Claims Automation**: End-to-end claims generation, validation, and submission workflows
- **LLM Integration**: Uses OpenAI GPT models for natural language understanding and coding suggestions
- **RAG Support**: Vector-based semantic search with pgvector for medical knowledge retrieval
- **MCP Orchestration**: Model Context Protocol tools for multi-step AI workflows
- **Audit & Compliance**: Comprehensive audit logging for HIPAA compliance
- **Modern UI**: Dell-inspired enterprise theme with React and TailwindCSS

## 🏗️ Architecture

### Backend (FastAPI)
- **API Layer**: RESTful endpoints with OpenAPI documentation
- **Business Logic Layer**: Service-oriented architecture
- **AI/LLM Service Layer**: OpenAI integration with LangChain
- **Data Layer**: PostgreSQL with pgvector extension
- **Integration Layer**: MCP tool orchestration

### Frontend (React)
- **React 18** with Vite for fast development
- **TailwindCSS** for modern styling
- **React Query** for data fetching and caching
- **React Router** for navigation
- **Lucide Icons** for consistent iconography

## 📁 Project Structure

```
medical-coding-system/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Configuration, security, dependencies
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic (LLM, documents, claims)
│   │   ├── mcp/              # MCP tool definitions
│   │   ├── db/               # Database configuration
│   │   └── utils/            # Utility functions
│   ├── alembic/              # Database migrations
│   ├── tests/                # Unit and integration tests
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile           # Backend container
│   └── alembic.ini          # Alembic configuration
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── services/         # API service layer
│   │   ├── hooks/            # Custom React hooks
│   │   ├── styles/           # Global styles
│   │   └── utils/            # Utility functions
│   ├── package.json          # Node dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── tailwind.config.js   # TailwindCSS configuration
│   └── Dockerfile           # Frontend container
├── docker-compose.yml       # Multi-container orchestration
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API Key
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd medical-coding-system
```

2. **Configure environment variables**
```bash
# Copy example environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env and add your OpenAI API key
# SECRET_KEY=your-secret-key
# OPENAI_API_KEY=your-openai-api-key
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Initialize the database**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Access the application**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development

#### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start PostgreSQL**
```bash
# Using Docker for database
docker run -d \
  --name medical-coding-db \
  -e POSTGRES_USER=medical_user \
  -e POSTGRES_PASSWORD=medical_password \
  -e POSTGRES_DB=medical_coding \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

6. **Run database migrations**
```bash
alembic upgrade head
```

7. **Start the development server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
cp .env.example .env
```

4. **Start the development server**
```bash
npm run dev
```

## 🔧 Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://medical_user:medical_password@localhost:5432/medical_coding` |
| `OPENAI_API_KEY` | OpenAI API key for LLM services | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4-turbo-preview` |
| `SECRET_KEY` | JWT secret key | Generate with `openssl rand -hex 32` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | `10080` (7 days) |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:5173","http://localhost:3000"]` |

### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |

## 📊 Database Schema

### Core Tables

- **users**: User accounts with role-based access control
- **patients**: Patient demographic information
- **documents**: Uploaded medical documents (PDF, DOCX, TXT)
- **extracted_entities**: Medical entities extracted from documents
- **medical_codes**: Suggested and approved medical codes (ICD-10, CPT, HCPCS)
- **claims**: Medical claims with line items
- **claim_items**: Individual claim line items
- **claim_validations**: Claim validation results
- **audit_logs**: System activity logs for compliance
- **embeddings**: Vector embeddings for semantic search

## 🔐 Security & Compliance

### Authentication
- JWT-based authentication
- Role-based access control (Admin, Coder, Reviewer, Viewer)
- Secure password hashing with bcrypt

### HIPAA Considerations
- Audit logging for all data access
- Input validation and sanitization
- Data encryption at rest (configure PostgreSQL)
- Secure API endpoints with authentication

### Best Practices
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Regular security updates
- Implement rate limiting
- Use environment variables for sensitive data

## 🤖 AI/LLM Integration

### LLM Services

1. **Entity Extraction**: Extracts diagnoses, procedures, medications from clinical text
2. **Code Suggestion**: Suggests ICD-10, CPT codes based on clinical context
3. **Claim Validation**: Validates claims for errors and compliance issues
4. **Code Explanation**: Provides detailed explanations of medical codes
5. **Embedding Generation**: Creates vector embeddings for semantic search

### MCP Tools

- `code_lookup`: Look up medical codes by number or description
- `claim_validation`: Validate claims for errors and compliance
- `medical_knowledge_retriever`: Retrieve medical knowledge and guidelines
- `entity_extraction`: Extract medical entities from text
- `coding_suggestion`: Suggest codes based on clinical documentation

## 🧪 Testing

### Backend Tests

The backend uses pytest for testing. Tests are located in the `backend/tests/` directory.

**Setup:**
```bash
cd backend
pip install pytest pytest-asyncio httpx
```

**Run all tests:**
```bash
pytest tests/
```

**Run specific test file:**
```bash
pytest tests/test_auth.py
```

**Run with coverage:**
```bash
pytest tests/ --cov=app --cov-report=html
```

**Run with verbose output:**
```bash
pytest tests/ -v
```

**Test files:**
- `test_auth.py` - Authentication endpoints (register, login, user management)
- `test_patients.py` - Patient CRUD operations
- `test_main.py` - Root and health check endpoints

### Frontend Tests

The frontend uses Vitest with React Testing Library. Tests are co-located with components.

**Setup:**
```bash
cd frontend
npm install
```

**Run all tests:**
```bash
npm test
```

**Run in watch mode:**
```bash
npm test -- --watch
```

**Run with UI:**
```bash
npm run test:ui
```

**Run with coverage:**
```bash
npm run test:coverage
```

**Test files:**
- `components/Button.test.jsx` - Button component variants and interactions
- `components/Card.test.jsx` - Card component rendering
- `components/Input.test.jsx` - Input component behavior

**Writing new tests:**
- Place test files next to components: `ComponentName.test.jsx`
- Use Vitest globals: `describe`, `it`, `expect`
- Use React Testing Library: `render`, `screen`, `userEvent`

## 📝 API Documentation

Once the backend is running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

#### Patients
- `POST /api/v1/patients/` - Create patient
- `GET /api/v1/patients/{id}` - Get patient by ID
- `PUT /api/v1/patients/{id}` - Update patient
- `GET /api/v1/patients/` - List patients

#### Documents
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/{id}` - Get document
- `POST /api/v1/documents/{id}/process` - Reprocess document

#### Claims
- `POST /api/v1/claims/` - Create claim
- `GET /api/v1/claims/{id}` - Get claim
- `POST /api/v1/claims/{id}/validate` - Validate claim
- `POST /api/v1/claims/{id}/submit` - Submit claim

#### MCP Tools
- `GET /api/v1/mcp/tools` - List available MCP tools
- `POST /api/v1/mcp/execute` - Execute MCP tool

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend

# Execute command in container
docker-compose exec backend bash

# Rebuild containers
docker-compose up -d --build
```

## 🔄 Database Migrations

```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1

# View migration history
docker-compose exec backend alembic history
```

## 📈 Monitoring & Logging

### Backend Logs
- Application logs: Available in container logs
- Audit logs: Stored in database `audit_logs` table

### Frontend Logs
- Browser console for client-side errors
- Network tab for API request debugging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For issues and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs`

## 🗺️ Roadmap

- [ ] EHR/HL7/FHIR integration
- [ ] Advanced analytics dashboard
- [ ] Batch document processing
- [ ] Custom code sets and mappings
- [ ] Payer-specific validation rules
- [ ] Electronic claim submission (EDI 837)
- [ ] Mobile application
- [ ] Advanced reporting features
