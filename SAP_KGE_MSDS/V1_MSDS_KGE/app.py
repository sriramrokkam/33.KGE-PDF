"""
app.py

Main Flask application for MSDS Knowledge Graph Extraction API.
"""

import os
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import our service modules
from srv.msds_validator import MSDSValidator
from srv.graph_processor import create_graph_processor
from srv.hana_client import create_hana_client
from srv.chat_service import create_chat_service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATIC_FOLDER'], exist_ok=True)
os.makedirs('static/graphs', exist_ok=True)

# Global configurations
AIC_CONFIG = {
    "aic_auth_url": os.getenv("AIC_AUTH_URL"),
    "aic_client_id": os.getenv("AIC_CLIENT_ID"),
    "aic_client_secret": os.getenv("AIC_CLIENT_SECRET"),
    "aic_resource_group": os.getenv("AIC_RESOURCE_GROUP", "default")
}

ORCH_MODEL_PARAMS = {
    "orch_url": os.getenv("ORCH_URL"),
    "orch_model": os.getenv("ORCH_MODEL", "anthropic--claude-4-sonnet"),
    "parameters": {
        "temperature": 0.3,
        "max_tokens": 20000,
        "top_p": 0.9
    }
}

HANA_CONFIG = {
    "hana_address": os.getenv("HANA_ADDRESS"),
    "hana_port": os.getenv("HANA_PORT", "443"),
    "hana_user": os.getenv("HANA_USER"),
    "hana_password": os.getenv("HANA_PASSWORD")
}

# Initialize services
validator = MSDSValidator()
graph_processor = create_graph_processor(AIC_CONFIG, ORCH_MODEL_PARAMS)
hana_client = create_hana_client(HANA_CONFIG)
chat_service = create_chat_service(AIC_CONFIG, ORCH_MODEL_PARAMS, HANA_CONFIG)

# Storage for upload sessions
upload_sessions = {}
extraction_sessions = {}

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    })

@app.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with service status."""
    # Test HANA connection
    hana_status = hana_client.test_connection()
    
    return jsonify({
        "status": "healthy" if hana_status["success"] else "degraded",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "hana_cloud": {
                "status": "healthy" if hana_status["success"] else "unhealthy",
                "details": hana_status
            },
            "ai_core": {
                "status": "configured",
                "model": ORCH_MODEL_PARAMS["orch_model"]
            },
            "graph_processor": {
                "status": "ready",
                "cache_size": len(graph_processor.extraction_cache)
            }
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload_msds():
    """Upload and validate MSDS document."""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file provided"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": "Only PDF files are allowed"
            }), 400
        
        # Generate upload ID and secure filename
        upload_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{upload_id}_{filename}")
        
        # Ensure upload directory exists before saving
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        logger.info(f"File uploaded: {filepath}")
        
        # Validate MSDS
        validation_result = validator.validate_pdf(filepath)
        
        # Store upload session
        upload_sessions[upload_id] = {
            "upload_id": upload_id,
            "filename": filename,
            "filepath": filepath,
            "upload_time": datetime.utcnow().isoformat(),
            "validation": validation_result
        }
        
        return jsonify({
            "success": True,
            "upload_id": upload_id,
            "filename": filename,
            "validation": {
                "is_valid_msds": validation_result["is_valid_msds"],
                "validation_score": validation_result.get("validation_score", 0),
                "missing_sections": validation_result["missing_sections"],
                "found_sections": validation_result["found_sections"],
                "sections_found_count": validation_result.get("sections_found_count", 0),
                "total_sections_required": validation_result.get("total_sections_required", 16)
            }
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({
            "success": False,
            "error": f"Upload failed: {str(e)}"
        }), 500

@app.route('/api/extract/<upload_id>', methods=['POST'])
def extract_knowledge_graph(upload_id):
    """Extract knowledge graph from uploaded document."""
    try:
        # Check if upload exists
        if upload_id not in upload_sessions:
            return jsonify({
                "success": False,
                "error": "Upload ID not found"
            }), 404
        
        upload_session = upload_sessions[upload_id]
        
        # Check if MSDS is valid (optional - can extract from invalid MSDS too)
        validation = upload_session["validation"]
        if not validation["is_valid_msds"]:
            logger.warning(f"Extracting from invalid MSDS: {upload_id}")
        
        # Extract triples
        extraction_id = str(uuid.uuid4())
        extraction_result = graph_processor.extract_triples_from_pdf(
            upload_session["filepath"], 
            extraction_id
        )
        
        # Store extraction session
        extraction_sessions[extraction_id] = {
            "extraction_id": extraction_id,
            "upload_id": upload_id,
            "extraction_time": datetime.utcnow().isoformat(),
            "result": extraction_result
        }
        
        return jsonify(extraction_result)
        
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return jsonify({
            "success": False,
            "error": f"Extraction failed: {str(e)}"
        }), 500

@app.route('/api/visualize/<extraction_id>', methods=['GET'])
def visualize_graph(extraction_id):
    """Generate graph visualization."""
    try:
        # Check if extraction exists
        if extraction_id not in extraction_sessions:
            return jsonify({
                "success": False,
                "error": "Extraction ID not found"
            }), 404
        
        # Generate visualization
        viz_result = graph_processor.generate_visualization(extraction_id)
        
        return jsonify(viz_result)
        
    except Exception as e:
        logger.error(f"Visualization error: {e}")
        return jsonify({
            "success": False,
            "error": f"Visualization failed: {str(e)}"
        }), 500

@app.route('/api/approve/<extraction_id>', methods=['POST'])
def approve_and_store(extraction_id):
    """Approve extraction and store in HANA Cloud."""
    try:
        # Check if extraction exists
        if extraction_id not in extraction_sessions:
            return jsonify({
                "success": False,
                "error": "Extraction ID not found"
            }), 404
        
        # Get request data
        data = request.get_json() or {}
        approved = data.get('approved', False)
        graph_name = data.get('graph_name', f'MSDS_Graph_{extraction_id[:8]}')
        
        if not approved:
            return jsonify({
                "success": False,
                "error": "Graph not approved for storage"
            }), 400
        
        # Get extraction result
        extraction_session = extraction_sessions[extraction_id]
        extraction_result = extraction_session["result"]
        
        if not extraction_result["success"] or not extraction_result["triples"]:
            return jsonify({
                "success": False,
                "error": "No valid triples to store"
            }), 400
        
        # Convert triples to tuple format for HANA
        triples = [
            (triple["subject"], triple["predicate"], triple["object"])
            for triple in extraction_result["triples"]
        ]
        
        # Prepare metadata
        metadata = {
            "extraction_id": extraction_id,
            "triples_count": len(triples),
            "quality_metrics": extraction_result.get("quality_metrics", {}),
            "document_pages": extraction_result.get("document_pages", 0),
            "document_length": extraction_result.get("document_length", 0),
            "validation_score": 100.0  # Default if not available
        }
        
        # Store in HANA
        storage_result = hana_client.store_knowledge_graph(graph_name, triples, metadata)
        
        return jsonify(storage_result)
        
    except Exception as e:
        logger.error(f"Storage error: {e}")
        return jsonify({
            "success": False,
            "error": f"Storage failed: {str(e)}"
        }), 500

@app.route('/api/graphs', methods=['GET'])
def list_graphs():
    """List all stored knowledge graphs."""
    try:
        result = hana_client.list_stored_graphs()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"List graphs error: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to list graphs: {str(e)}"
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_graph():
    """Chat with knowledge graph."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        query = data.get('query')
        graph_name = data.get('graph_name')
        
        if not query or not graph_name:
            return jsonify({
                "success": False,
                "error": "Both 'query' and 'graph_name' are required"
            }), 400
        
        # Process chat query
        result = chat_service.chat_with_graph(query, graph_name)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            "success": False,
            "error": f"Chat failed: {str(e)}"
        }), 500

@app.route('/api/chat/suggestions/<graph_name>', methods=['GET'])
def get_chat_suggestions(graph_name):
    """Get suggested questions for a graph."""
    try:
        result = chat_service.suggest_questions(graph_name)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to get suggestions: {str(e)}"
        }), 500

@app.route('/api/graph/summary/<graph_name>', methods=['GET'])
def get_graph_summary(graph_name):
    """Get summary of a knowledge graph."""
    try:
        result = chat_service.get_graph_summary(graph_name)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Summary error: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to get summary: {str(e)}"
        }), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (graphs, images)."""
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

@app.route('/static/graphs/<path:filename>')
def serve_graphs(filename):
    """Serve graph visualization files."""
    return send_from_directory('static/graphs', filename)

@app.route('/api/sections', methods=['GET'])
def get_msds_sections():
    """Get list of required MSDS sections."""
    try:
        result = validator.get_section_requirements()
        return jsonify({
            "success": True,
            **result
        })
        
    except Exception as e:
        logger.error(f"Sections error: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to get sections: {str(e)}"
        }), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({
        "success": False,
        "error": "File too large. Maximum size is 16MB."
    }), 413

@app.errorhandler(404)
def not_found(e):
    """Handle not found error."""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error."""
    logger.error(f"Internal server error: {e}")
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    # Check required environment variables
    required_vars = [
        "AIC_AUTH_URL", "AIC_CLIENT_ID", "AIC_CLIENT_SECRET",
        "HANA_ADDRESS", "HANA_USER", "HANA_PASSWORD"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please set these in your .env file before running the application.")
        exit(1)
    
    # Test connections on startup
    logger.info("Testing HANA connection...")
    hana_test = hana_client.test_connection()
    if hana_test["success"]:
        logger.info("✅ HANA Cloud connection successful")
    else:
        logger.warning(f"⚠️ HANA Cloud connection failed: {hana_test.get('error')}")
    
    # Start Flask app
    logger.info("🚀 Starting MSDS Knowledge Graph Extraction API")
    logger.info("📡 Available endpoints:")
    logger.info("   GET  /health - Health check")
    logger.info("   POST /api/upload - Upload MSDS document")
    logger.info("   POST /api/extract/<upload_id> - Extract knowledge graph")
    logger.info("   GET  /api/visualize/<extraction_id> - Generate visualization")
    logger.info("   POST /api/approve/<extraction_id> - Approve and store in HANA")
    logger.info("   GET  /api/graphs - List stored graphs")
    logger.info("   POST /api/chat - Chat with knowledge graph")
    logger.info("   GET  /api/sections - Get MSDS section requirements")
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
