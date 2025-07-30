# MSDS Knowledge Graph Extraction API

A comprehensive Flask API for extracting knowledge graphs from Material Safety Data Sheets (MSDS) and storing them in SAP HANA Cloud database.

> 📋 **For detailed technical information, see [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md)**

## 🚀 Features

- **MSDS Validation**: Validates if all 16 required MSDS sections are present
- **Knowledge Graph Extraction**: Extracts subject-predicate-object triples from MSDS documents
- **Graph Visualization**: Generates interactive knowledge graph visualizations
- **HANA Cloud Integration**: Stores extracted knowledge graphs in SAP HANA Cloud
- **RESTful API**: Complete REST API with endpoints for all operations
- **Chat Interface**: Query the knowledge graph using natural language

## 📋 MSDS Sections Validation

The system validates the presence of all 16 standard MSDS sections:

1. **Identification**
2. **Hazard(s) Identification**
3. **Composition/Information on Ingredients**
4. **First-Aid Measures**
5. **Fire-Fighting Measures**
6. **Accidental Release Measures**
7. **Handling and Storage**
8. **Exposure Controls/Personal Protection**
9. **Physical and Chemical Properties**
10. **Stability and Reactivity**
11. **Toxicological Information**
12. **Ecological Information**
13. **Disposal Considerations**
14. **Transport Information**
15. **Regulatory Information**
16. **Other Information**

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- SAP HANA Cloud access
- AI Core credentials

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd SAP_KGE_MSDS/Ref_KGE
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create/update `.env` file with your credentials:
   ```env
   # AI Core Configuration
   AICORE_AUTH_URL=your_auth_url
   AICORE_CLIENT_ID=your_client_id
   AICORE_CLIENT_SECRET=your_client_secret
   AICORE_BASE_URL=your_base_url
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

## 🚀 Running the Application

### Start the Flask Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### Alternative: Development Mode

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

## 📡 API Endpoints

### 1. Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-22T10:30:00Z"
}
```

### 2. Upload and Validate MSDS
```http
POST /api/upload
Content-Type: multipart/form-data
```
**Parameters:**
- `file`: MSDS PDF file

**Response:**
```json
{
  "success": true,
  "filename": "msds_document.pdf",
  "validation": {
    "is_valid_msds": true,
    "missing_sections": [],
    "found_sections": ["Section 1", "Section 2", ...]
  },
  "upload_id": "uuid-string"
}
```

### 3. Extract Knowledge Graph
```http
POST /api/extract/{upload_id}
```
**Response:**
```json
{
  "success": true,
  "extraction_id": "uuid-string",
  "triples_count": 45,
  "triples": [
    {
      "subject": "WD-40 Multi-Use Product",
      "predicate": "is manufactured by",
      "object": "WD-40 Company"
    }
  ],
  "quality_metrics": {
    "unique_subjects": 15,
    "unique_predicates": 8,
    "unique_objects": 22,
    "correct_format_percentage": 95.5
  }
}
```

### 4. Generate Graph Visualization
```http
GET /api/visualize/{extraction_id}
```
**Response:**
```json
{
  "success": true,
  "visualization_url": "/static/graphs/graph_uuid.png",
  "graph_data": {
    "nodes": [...],
    "edges": [...]
  }
}
```

### 5. Approve and Store in HANA
```http
POST /api/approve/{extraction_id}
```
**Request Body:**
```json
{
  "approved": true,
  "graph_name": "WD40_MSDS_Graph"
}
```
**Response:**
```json
{
  "success": true,
  "graph_id": "hana-graph-id",
  "stored_triples": 45,
  "hana_status": "stored"
}
```

### 6. Chat with Knowledge Graph
```http
POST /api/chat
```
**Request Body:**
```json
{
  "query": "What are the hazards of WD-40?",
  "graph_id": "hana-graph-id"
}
```
**Response:**
```json
{
  "success": true,
  "query": "What are the hazards of WD-40?",
  "answer": "Based on the MSDS, WD-40 has the following hazards...",
  "relevant_triples": [...]
}
```

### 7. List Stored Graphs
```http
GET /api/graphs
```
**Response:**
```json
{
  "success": true,
  "graphs": [
    {
      "graph_id": "hana-graph-id",
      "graph_name": "WD40_MSDS_Graph",
      "created_date": "2025-01-22T10:30:00Z",
      "triples_count": 45
    }
  ]
}
```

## 🧪 Testing with Postman

### 1. Import Collection
Create a Postman collection with the following requests:

### 2. Test Sequence
1. **Health Check**: `GET /health`
2. **Upload MSDS**: `POST /api/upload` (with PDF file)
3. **Extract Triples**: `POST /api/extract/{upload_id}`
4. **View Visualization**: `GET /api/visualize/{extraction_id}`
5. **Approve & Store**: `POST /api/approve/{extraction_id}`
6. **Chat Query**: `POST /api/chat`

### 3. Sample Postman Environment Variables
```json
{
  "base_url": "http://localhost:5000",
  "upload_id": "{{upload_id}}",
  "extraction_id": "{{extraction_id}}",
  "graph_id": "{{graph_id}}"
}
```

## 🏗️ System Architecture

### High-Level Overview
The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Web Browser   │    │   Postman/API   │
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

### Key Technologies
- **Backend**: Flask 2.x with Python 3.8+
- **AI/ML**: SAP AI Core (Claude 4 Sonnet)
- **Database**: SAP HANA Cloud with SPARQL support
- **Document Processing**: PyPDF, LangChain
- **Graph Processing**: NetworkX, Matplotlib
- **API**: RESTful with JSON responses

### Data Flow
1. **Document Upload** → PDF validation and text extraction
2. **Knowledge Extraction** → LLM-powered triple extraction
3. **Quality Analysis** → Validation and metrics calculation
4. **Visualization** → Interactive graph generation
5. **Storage** → HANA Cloud persistence with SPARQL
6. **Querying** → Natural language chat interface

## 🔧 Development

### Project Structure
```
SAP_KGE_MSDS/Ref_KGE/
├── app.py                          # Main Flask application
├── .env                           # Environment variables
├── requirements.txt               # Dependencies
├── README.md                      # This file
├── TECHNICAL_DESIGN.md            # Detailed technical documentation
├── srv/                          # Supporting modules
│   ├── __init__.py
│   ├── llm_client.py            # LLM client classes
│   ├── prompts.py               # Prompt templates
│   ├── msds_validator.py        # MSDS validation logic
│   ├── graph_processor.py       # Graph processing utilities
│   ├── hana_client.py           # HANA Cloud integration
│   ├── chat_service.py          # Chat functionality
│   └── msds_ontology.owl        # MSDS ontology definition
├── static/                       # Static files (graphs, images)
│   └── graphs/                  # Generated visualizations
├── templates/                    # HTML templates (if needed)
└── uploads/                      # Temporary file uploads
```

### Core Components

#### 1. MSDS Validator (`srv/msds_validator.py`)
- Validates presence of all 16 standard MSDS sections
- Uses regex patterns for section detection
- Calculates validation scores and identifies missing sections

#### 2. Graph Processor (`srv/graph_processor.py`)
- Extracts knowledge triples using LLM orchestration
- Supports multiple triple parsing formats
- Generates interactive graph visualizations
- Provides quality metrics and caching

#### 3. HANA Client (`srv/hana_client.py`)
- Manages SAP HANA Cloud connections
- Stores knowledge graphs using SPARQL
- Provides graph querying and management operations
- Handles metadata storage and retrieval

#### 4. Chat Service (`srv/chat_service.py`)
- Natural language query processing
- Context-aware response generation
- Integration with stored knowledge graphs
- Support for various query types

### Adding New Features
1. Create new modules in `srv/` directory
2. Add new endpoints in `app.py`
3. Update this README with new API documentation
4. Update the technical design document
5. Add tests for new functionality

## 🐛 Troubleshooting

### Common Issues

1. **Environment Variables Not Loaded**
   ```bash
   # Ensure .env file is in the correct location
   ls -la .env
   ```

2. **HANA Connection Issues**
   ```bash
   # Test HANA connectivity
   python -c "from srv.hana_client import test_connection; test_connection()"
   ```

3. **AI Core Authentication**
   ```bash
   # Verify AI Core credentials
   python srv/test_llm_clients.py
   ```

4. **File Upload Issues**
   - Ensure `uploads/` directory exists
   - Check file size limits (default: 16MB)
   - Verify PDF file format

### Debug Mode
Enable debug logging by setting:
```env
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
```

## 📊 Monitoring

### Health Endpoints
- `/health` - Basic health check
- `/health/detailed` - Detailed system status
- `/metrics` - Application metrics

### Logging
Logs are written to:
- Console (development)
- `logs/app.log` (production)

## 🔒 Security

### Authentication
- API key authentication (optional)
- Rate limiting
- File upload validation

### Data Protection
- Temporary file cleanup
- Secure credential storage
- HTTPS in production

## 📈 Performance

### Optimization Tips
1. Use connection pooling for HANA
2. Cache frequently accessed graphs
3. Implement async processing for large files
4. Use CDN for static graph images

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review API documentation
