# MSDS Knowledge Graph Extraction System - Technical Design Document

## 1. System Overview

### 1.1 Purpose
The MSDS Knowledge Graph Extraction System is a comprehensive Flask-based API that processes Material Safety Data Sheets (MSDS) documents to extract structured knowledge graphs and store them in SAP HANA Cloud. The system leverages Large Language Models (LLMs) through SAP AI Core for intelligent information extraction and provides natural language querying capabilities.

### 1.2 Key Capabilities
- **Document Validation**: Validates MSDS documents against 16 standard sections
- **Knowledge Extraction**: Extracts subject-predicate-object triples using LLMs
- **Graph Visualization**: Generates interactive knowledge graph visualizations
- **Persistent Storage**: Stores knowledge graphs in SAP HANA Cloud with SPARQL support
- **Natural Language Interface**: Chat-based querying of stored knowledge graphs
- **RESTful API**: Complete REST API for all operations

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Web Browser   │    │   Postman/API   │
│                 │    │                 │    │   Testing Tools │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────────────────┐
                    │     Flask API Server    │
                    │      (app.py)          │
                    └─────────┬───────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
┌─────────▼─────────┐ ┌───────▼───────┐ ┌─────────▼─────────┐
│  MSDS Validator   │ │ Graph         │ │  Chat Service     │
│  (validation)     │ │ Processor     │ │  (NL queries)     │
└───────────────────┘ │ (extraction)  │ └───────────────────┘
                      └───────┬───────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
┌─────────▼─────────┐ ┌───────▼───────┐ ┌─────────▼─────────┐
│   SAP AI Core     │ │  HANA Cloud   │ │  File System      │
│   (LLM Services)  │ │  (Storage)    │ │  (Temp/Static)    │
└───────────────────┘ └───────────────┘ └───────────────────┘
```

### 2.2 Component Architecture

#### 2.2.1 Core Components

1. **Flask Application (app.py)**
   - Main entry point and API orchestration
   - Request routing and response handling
   - Session management for uploads and extractions
   - Error handling and logging

2. **Service Layer (srv/)**
   - **MSDS Validator**: Document validation logic
   - **Graph Processor**: Knowledge extraction and visualization
   - **HANA Client**: Database operations and SPARQL queries
   - **Chat Service**: Natural language processing
   - **LLM Client**: AI Core integration
   - **Prompts**: Template management for LLM interactions

3. **External Integrations**
   - **SAP AI Core**: LLM services (Claude 4 Sonnet)
   - **SAP HANA Cloud**: Knowledge graph storage
   - **File System**: Temporary uploads and static assets

## 3. Detailed Component Design

### 3.1 Flask Application Layer

#### 3.1.1 Main Application (app.py)
```python
# Key configurations
AIC_CONFIG = {
    "aic_auth_url": os.getenv("AICORE_AUTH_URL"),
    "aic_client_id": os.getenv("AICORE_CLIENT_ID"),
    "aic_client_secret": os.getenv("AICORE_CLIENT_SECRET"),
    "aic_resource_group": os.getenv("AICORE_RESOURCE_GROUP", "default")
}

ORCH_MODEL_PARAMS = {
    "orch_url": "https://api.ai.prod.us-east-1.aws.ml.hana.ondemand.com/v2/inference/deployments/ddaae0b631e78184",
    "orch_model": "anthropic--claude-4-sonnet",
    "parameters": {
        "temperature": 0.3,
        "max_tokens": 20000,
        "top_p": 0.9
    }
}
```

#### 3.1.2 API Endpoints
- **Health Endpoints**: `/health`, `/health/detailed`
- **Document Processing**: `/api/upload`, `/api/extract/<id>`
- **Visualization**: `/api/visualize/<id>`
- **Storage**: `/api/approve/<id>`
- **Query Interface**: `/api/chat`, `/api/graphs`
- **Utility**: `/api/sections`, `/static/<path>`

### 3.2 MSDS Validator (srv/msds_validator.py)

#### 3.2.1 Validation Logic
```python
class MSDSValidator:
    REQUIRED_SECTIONS = [
        "Identification",
        "Hazard(s) Identification",
        "Composition/Information on Ingredients",
        # ... 13 more sections
    ]
    
    def validate_pdf(self, pdf_path: str) -> Dict:
        # Extract text from PDF
        # Check for presence of all 16 sections
        # Calculate validation score
        # Return validation results
```

#### 3.2.2 Section Detection
- Uses regex patterns to identify section headers
- Supports multiple formatting variations
- Calculates validation scores based on section coverage

### 3.3 Graph Processor (srv/graph_processor.py)

#### 3.3.1 Knowledge Extraction Pipeline
```python
class GraphProcessor:
    def extract_triples_from_pdf(self, pdf_path: str) -> Dict:
        # 1. Load PDF content using PyPDFLoader
        # 2. Format content for LLM processing
        # 3. Send to orchestration service
        # 4. Parse response for triples
        # 5. Analyze extraction quality
        # 6. Cache results
```

#### 3.3.2 Triple Parsing Methods
1. **Standard Format**: `(Subject, Predicate, Object)`
2. **Text Format**: `Subject: X, Predicate: Y, Object: Z`
3. **Delimiter-based**: Custom delimiters
4. **Flexible Parsing**: Comma-separated with validation

#### 3.3.3 Visualization Engine
- Uses NetworkX for graph structure
- Matplotlib for rendering
- Node categorization (subjects, predicates, objects)
- Interactive graph data export

### 3.4 HANA Client (srv/hana_client.py)

#### 3.4.1 Connection Management
```python
class HANAClient:
    def connect(self) -> bool:
        self.connection = dbapi.connect(
            address=self.hana_address,
            port=self.hana_port,
            user=self.hana_user,
            password=self.hana_password
        )
```

#### 3.4.2 SPARQL Operations
- **Storage**: INSERT DATA operations with graph IRIs
- **Querying**: SELECT queries with SPARQL syntax
- **Management**: Graph creation, deletion, listing

#### 3.4.3 Metadata Management
```sql
CREATE TABLE MSDS_GRAPH_METADATA (
    GRAPH_ID NVARCHAR(36) PRIMARY KEY,
    GRAPH_NAME NVARCHAR(255),
    CREATED_DATE TIMESTAMP,
    TRIPLES_COUNT INTEGER,
    DOCUMENT_PAGES INTEGER,
    DOCUMENT_LENGTH INTEGER,
    VALIDATION_SCORE DECIMAL(5,2),
    METADATA NCLOB
)
```

### 3.5 Chat Service (srv/chat_service.py)

#### 3.5.1 Natural Language Processing
- Query understanding and intent recognition
- Context-aware response generation
- Relevant triple retrieval from HANA
- Response formatting and presentation

#### 3.5.2 Query Types Supported
- **Factual Queries**: "What are the hazards of WD-40?"
- **Relationship Queries**: "What chemicals are in this product?"
- **Comparative Queries**: "Compare safety measures"
- **Exploratory Queries**: "Tell me about this MSDS"

## 4. Data Flow Architecture

### 4.1 Document Processing Flow

```
PDF Upload → Validation → Text Extraction → LLM Processing → Triple Extraction → Quality Analysis → Caching
     ↓
Visualization Generation → User Approval → HANA Storage → Metadata Recording
```

### 4.2 Query Processing Flow

```
Natural Language Query → Intent Analysis → SPARQL Generation → HANA Query → Result Processing → Response Generation
```

### 4.3 Session Management

#### 4.3.1 Upload Sessions
```python
upload_sessions[upload_id] = {
    "upload_id": upload_id,
    "filename": filename,
    "filepath": filepath,
    "upload_time": datetime.utcnow().isoformat(),
    "validation": validation_result
}
```

#### 4.3.2 Extraction Sessions
```python
extraction_sessions[extraction_id] = {
    "extraction_id": extraction_id,
    "upload_id": upload_id,
    "extraction_time": datetime.utcnow().isoformat(),
    "result": extraction_result
}
```

## 5. Technology Stack

### 5.1 Core Technologies
- **Backend Framework**: Flask 2.x
- **Language**: Python 3.8+
- **Database**: SAP HANA Cloud with SPARQL support
- **AI/ML**: SAP AI Core (Claude 4 Sonnet)
- **Document Processing**: PyPDF, LangChain
- **Graph Processing**: NetworkX, Matplotlib
- **API**: RESTful with JSON responses

### 5.2 Key Dependencies
```
flask==2.3.3
flask-cors==4.0.0
langchain==0.1.0
langchain-community==0.0.10
networkx==3.2.1
matplotlib==3.8.2
hdbcli==2.19.21
python-dotenv==1.0.0
generative-ai-hub-sdk[langchain]==1.1.0
```

### 5.3 External Services
- **SAP AI Core**: LLM orchestration and inference
- **SAP HANA Cloud**: Graph database and SPARQL engine
- **File System**: Local storage for uploads and visualizations

## 6. Security Architecture

### 6.1 Authentication & Authorization
- Environment-based credential management
- SAP AI Core OAuth2 authentication
- HANA Cloud database authentication
- API key support (configurable)

### 6.2 Data Protection
- Temporary file cleanup after processing
- Secure credential storage in environment variables
- Input validation and sanitization
- File upload restrictions (PDF only, 16MB limit)

### 6.3 Network Security
- HTTPS support for production deployment
- CORS configuration for cross-origin requests
- Rate limiting capabilities
- Request size limitations

## 7. Performance Considerations

### 7.1 Optimization Strategies
- **Connection Pooling**: HANA connection reuse
- **Caching**: Extraction result caching
- **Async Processing**: Background processing for large files
- **Resource Management**: Memory cleanup for visualizations

### 7.2 Scalability Features
- Stateless API design
- Session-based processing
- Configurable resource limits
- Horizontal scaling support

### 7.3 Performance Metrics
- Document processing time
- Triple extraction accuracy
- Query response time
- Memory usage optimization

## 8. Error Handling & Monitoring

### 8.1 Error Handling Strategy
```python
@app.errorhandler(413)
def too_large(e):
    return jsonify({
        "success": False,
        "error": "File too large. Maximum size is 16MB."
    }), 413

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500
```

### 8.2 Logging Configuration
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 8.3 Health Monitoring
- Basic health check endpoint
- Detailed service status monitoring
- Connection testing for external services
- Performance metrics collection

## 9. Deployment Architecture

### 9.1 Environment Configuration
```env
# AI Core Configuration
AICORE_AUTH_URL=your_auth_url
AICORE_CLIENT_ID=your_client_id
AICORE_CLIENT_SECRET=your_client_secret
AICORE_RESOURCE_GROUP=default

# HANA Cloud Configuration
HANA_ADDRESS=your_hana_address
HANA_PORT=443
HANA_USER=your_hana_user
HANA_PASSWORD=your_hana_password

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### 9.2 Directory Structure
```
SAP_KGE_MSDS/Ref_KGE/
├── app.py                          # Main Flask application
├── .env                           # Environment variables
├── requirements.txt               # Dependencies
├── README.md                      # Documentation
├── TECHNICAL_DESIGN.md           # This document
├── srv/                          # Service modules
│   ├── __init__.py
│   ├── llm_client.py            # LLM client classes
│   ├── prompts.py               # Prompt templates
│   ├── msds_validator.py        # MSDS validation logic
│   ├── graph_processor.py       # Graph processing utilities
│   ├── hana_client.py           # HANA Cloud integration
│   ├── chat_service.py          # Chat functionality
│   └── msds_ontology.owl        # MSDS ontology definition
├── static/                       # Static files
│   └── graphs/                  # Generated visualizations
├── templates/                    # HTML templates (if needed)
└── uploads/                      # Temporary file uploads
```

### 9.3 Production Considerations
- **Container Deployment**: Docker support
- **Load Balancing**: Multiple instance support
- **SSL/TLS**: HTTPS configuration
- **Monitoring**: Application performance monitoring
- **Backup**: Regular data backup strategies

## 10. API Design Patterns

### 10.1 RESTful Design Principles
- Resource-based URLs
- HTTP method semantics
- Consistent response formats
- Proper status codes

### 10.2 Response Format Standards
```json
{
  "success": true|false,
  "data": {...},
  "error": "error message",
  "timestamp": "ISO 8601 timestamp",
  "metadata": {...}
}
```

### 10.3 Error Response Standards
```json
{
  "success": false,
  "error": "Descriptive error message",
  "error_code": "ERROR_CODE",
  "details": {...}
}
```

## 11. Quality Assurance

### 11.1 Testing Strategy
- Unit tests for individual components
- Integration tests for API endpoints
- End-to-end testing for complete workflows
- Performance testing for large documents

### 11.2 Quality Metrics
- Triple extraction accuracy
- MSDS validation precision
- API response time
- System availability

### 11.3 Validation Processes
- Input validation for all endpoints
- Output format validation
- Data integrity checks
- Security vulnerability scanning

## 12. Future Enhancements

### 12.1 Planned Features
- **Batch Processing**: Multiple document processing
- **Advanced Analytics**: Graph analysis and insights
- **Machine Learning**: Improved extraction accuracy
- **Web Interface**: User-friendly web application

### 12.2 Scalability Improvements
- **Microservices**: Service decomposition
- **Message Queues**: Asynchronous processing
- **Caching Layer**: Redis integration
- **CDN Integration**: Static asset delivery

### 12.3 Integration Opportunities
- **SAP Integration**: BTP service integration
- **Third-party APIs**: External data sources
- **Workflow Automation**: Process orchestration
- **Mobile Applications**: Mobile API support

## 13. Maintenance & Support

### 13.1 Monitoring Requirements
- System health monitoring
- Performance metrics tracking
- Error rate monitoring
- Resource utilization tracking

### 13.2 Backup & Recovery
- Database backup procedures
- Configuration backup
- Disaster recovery planning
- Data retention policies

### 13.3 Update Procedures
- Dependency updates
- Security patches
- Feature deployments
- Database migrations

---

**Document Version**: 1.0  
**Last Updated**: January 22, 2025  
**Author**: AI Development Team  
**Review Status**: Draft
