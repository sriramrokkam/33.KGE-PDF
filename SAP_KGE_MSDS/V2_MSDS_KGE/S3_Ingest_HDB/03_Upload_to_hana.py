
"""EXECUTION INSTRUCTIONS:
----------------------
1. Install required dependencies:
   pip install hdbcli rdflib

2. Update connection parameters in the config section below

3. Execute the module:
   python 03_Upload_to_hana.py

INPUT REQUIREMENTS:
------------------
- TTL file from Module 2: ../S2_Build_Tuples/financial_data_triples.ttl
- Valid SAP HANA Cloud connection parameters

OUTPUT:
-------
- RDF triples uploaded to HANA Cloud graph store
- Basic upload confirmation

This module provides a simple, focused solution for uploading RDF triples
to SAP HANA Cloud graph store without unnecessary complexity.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Optional

# Core dependencies
from hdbcli import dbapi
from rdflib import Graph

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class SimpleHanaUploader:
    """
    Simple SAP HANA Cloud RDF Uploader - focused on core functionality only
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the HANA uploader
        
        Args:
            config (dict, optional): Configuration parameters
        """
        self.logger = logging.getLogger(__name__)
        
        # Default configuration - UPDATE THESE VALUES
        self.config = {
            'hana_host': "d93a8739-44a8-4845-bef3-8ec724dea2ce.hana.prod-us10.hanacloud.ondemand.com",
            'hana_port': "443",
            'hana_user': "DBADMIN",
            'hana_password': "Initial@1",
            'hana_ssl': True,  # Use SSL for secure connection
            'graph_name': 'SCB_CIB_Graph',
            'ttl_file': '../S2_Build_Tuples/financial_data_triples.ttl'
        }
#!/usr/bin/env python3
"""
Module 3: HANA Database Uploader - RDF Tuples to SAP HANA Cloud with KGE_MSDS Schema

EXECUTION INSTRUCTIONS:
----------------------
1. Install required dependencies:
   pip install hdbcli rdflib

2. Update connection parameters in the config section below

3. Execute the module:
   python 03_Upload_to_hana.py

INPUT REQUIREMENTS:
------------------
- TTL/RDF files from Module 2: ../S2_Build_Tupples/
- Valid SAP HANA Cloud connection parameters

OUTPUT:
-------
- RDF tuples ingested into HANA Cloud KGE_MSDS schema
- Relational tables created for structured data access
- Upload confirmation and statistics

This module provides an OOP-based solution for ingesting RDF tuples
into SAP HANA Cloud with proper schema management.
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, Optional, List, Tuple, Any
from pathlib import Path

# Core dependencies
from hdbcli import dbapi
from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class HanaKGEUploader:
    """
    SAP HANA Cloud KGE MSDS Uploader - OOP-based tuple ingestion with schema management
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the HANA KGE uploader
        
        Args:
            config (dict, optional): Configuration parameters
        """
        self.logger = logging.getLogger(__name__)
        
        # Default configuration - UPDATE THESE VALUES
        self.config = {
            'hana_host': "d93a8739-44a8-4845-bef3-8ec724dea2ce.hana.prod-us10.hanacloud.ondemand.com",
            'hana_port': "443",
            'hana_user': "DBADMIN",
            'hana_password': "Initial@1",
            'hana_ssl': True,
            'schema_name': 'KGE_MSDS',
            'input_directory': '../S2_Build_Tupples/',
            'supported_formats': ['.ttl', '.rdf', '.n3', '.json']
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
        
        self.connection = None
        self.cursor = None
        self.schema_created = False
        
        # Statistics tracking
        self.stats = {
            'files_processed': 0,
            'tuples_ingested': 0,
            'tables_created': 0,
            'errors': 0
        }
======================================================================

EXECUTION INSTRUCTIONS:
----------------------
1. Install required dependencies:
   pip install hdbcli rdflib

2. Update connection parameters in the config section below

3. Execute the module:
   python 03_Upload_to_hana.py

INPUT REQUIREMENTS:
------------------
- TTL file from Module 2: ../S2_Build_Tuples/financial_data_triples.ttl
- Valid SAP HANA Cloud connection parameters

OUTPUT:
-------
- RDF triples uploaded to HANA Cloud graph store
- Basic upload confirmation

This module provides a simple, focused solution for uploading RDF triples
to SAP HANA Cloud graph store without unnecessary complexity.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Optional

# Core dependencies
from hdbcli import dbapi
from rdflib import Graph

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class SimpleHanaUploader:
    """
    Simple SAP HANA Cloud RDF Uploader - focused on core functionality only
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the HANA uploader
        
        Args:
            config (dict, optional): Configuration parameters
        """
        self.logger = logging.getLogger(__name__)
        
        # Default configuration - UPDATE THESE VALUES
        self.config = {
            'hana_host': "d93a8739-44a8-4845-bef3-8ec724dea2ce.hana.prod-us10.hanacloud.ondemand.com",
            'hana_port': "443",
            'hana_user': "DBADMIN",
            'hana_password': "Initial@1",
            'hana_ssl': True,  # Use SSL for secure connection
            'graph_name': 'SCB_CIB_Graph',
            'ttl_file': '../S2_Build_Tuples/financial_data_triples.ttl'
        }
        
    def connect_to_hana(self) -> bool:
        """
        Establish connection to SAP HANA Cloud
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info("Connecting to SAP HANA Cloud...")
            
            # Validate connection parameters
            required_params = ['hana_host', 'hana_user', 'hana_password']
            for param in required_params:
                if isinstance(self.config[param], str) and self.config[param].startswith('<') and self.config[param].endswith('>'):
                    raise ValueError(f"Please update {param} in configuration")
            
            # Establish connection
            self.connection = dbapi.connect(
                address=self.config['hana_host'],
                port=self.config['hana_port'],
                user=self.config['hana_user'],
                password=self.config['hana_password']
            )
            
            self.cursor = self.connection.cursor()
            
            # Test connection
            self.cursor.execute("SELECT CURRENT_TIMESTAMP FROM DUMMY")
            result = self.cursor.fetchone()
            
            if result:
                self.logger.info(f"Successfully connected to HANA at {result[0]}")
            else:
                self.logger.info("Successfully connected to HANA")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to HANA: {str(e)}")
            return False
    
    def create_schema(self) -> bool:
        """
        Create KGE_MSDS schema if it doesn't exist
        
        Returns:
            bool: True if schema created/exists, False otherwise
        """
        try:
            schema_name = self.config['schema_name']
            self.logger.info(f"Creating schema: {schema_name}")
            
            # Check if schema exists
            check_schema_sql = """
            SELECT SCHEMA_NAME FROM SYS.SCHEMAS 
            WHERE SCHEMA_NAME = ?
            """
            self.cursor.execute(check_schema_sql, (schema_name,))
            result = self.cursor.fetchone()
            
            if result:
                self.logger.info(f"Schema {schema_name} already exists")
                self.schema_created = True
                return True
            
            # Create schema
            create_schema_sql = f"CREATE SCHEMA {schema_name}"
            self.cursor.execute(create_schema_sql)
            self.connection.commit()
            
            self.logger.info(f"Schema {schema_name} created successfully")
            self.schema_created = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create schema: {str(e)}")
            return False
    
    def create_tables(self) -> bool:
        """
        Create necessary tables in KGE_MSDS schema
        
        Returns:
            bool: True if tables created successfully, False otherwise
        """
        try:
            schema_name = self.config['schema_name']
            
            # Define table structures for different entity types
            tables = {
                'RDF_TRIPLES': """
                CREATE TABLE {schema}.RDF_TRIPLES (
                    ID BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    SUBJECT NVARCHAR(500) NOT NULL,
                    PREDICATE NVARCHAR(500) NOT NULL,
                    OBJECT NCLOB,
                    OBJECT_TYPE NVARCHAR(50),
                    DOCUMENT_NAME NVARCHAR(200),
                    SECTION_NAME NVARCHAR(100),
                    CONFIDENCE DECIMAL(3,2),
                    EXTRACTION_METHOD NVARCHAR(100),
                    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX IDX_SUBJECT (SUBJECT),
                    INDEX IDX_PREDICATE (PREDICATE),
                    INDEX IDX_DOCUMENT (DOCUMENT_NAME)
                )
                """,
                
                'INGREDIENTS': """
                CREATE TABLE {schema}.INGREDIENTS (
                    ID BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    INGREDIENT_NAME NVARCHAR(500) NOT NULL,
                    CAS_NUMBER NVARCHAR(50),
                    WEIGHT_PERCENT NVARCHAR(50),
                    CLASSIFICATION NVARCHAR(200),
                    EC_NUMBER NVARCHAR(50),
                    PURITY DECIMAL(5,2),
                    DOCUMENT_NAME NVARCHAR(200),
                    CONFIDENCE DECIMAL(3,2),
                    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX IDX_CAS (CAS_NUMBER),
                    INDEX IDX_NAME (INGREDIENT_NAME)
                )
                """,
                
                'HAZARDS': """
                CREATE TABLE {schema}.HAZARDS (
                    ID BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    HAZARD_STATEMENT NCLOB NOT NULL,
                    HAZARD_CATEGORY NVARCHAR(200),
                    HAZARD_CODE NVARCHAR(20),
                    SIGNAL_WORD NVARCHAR(50),
                    SEVERITY_LEVEL NVARCHAR(50),
                    DOCUMENT_NAME NVARCHAR(200),
                    CONFIDENCE DECIMAL(3,2),
                    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX IDX_CODE (HAZARD_CODE),
                    INDEX IDX_CATEGORY (HAZARD_CATEGORY)
                )
                """,
                
                'PHYSICAL_PROPERTIES': """
                CREATE TABLE {schema}.PHYSICAL_PROPERTIES (
                    ID BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    PROPERTY_NAME NVARCHAR(200) NOT NULL,
                    PROPERTY_VALUE NVARCHAR(500),
                    NUMERIC_VALUE DECIMAL(15,6),
                    UNIT NVARCHAR(50),
                    TEST_METHOD NVARCHAR(200),
                    TEMPERATURE DECIMAL(10,2),
                    PRESSURE DECIMAL(10,2),
                    DOCUMENT_NAME NVARCHAR(200),
                    CONFIDENCE DECIMAL(3,2),
                    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX IDX_PROPERTY (PROPERTY_NAME)
                )
                """,
                
                'FIRST_AID_MEASURES': """
                CREATE TABLE {schema}.FIRST_AID_MEASURES (
                    ID BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    FIRST_AID_TYPE NVARCHAR(100) NOT NULL,
                    INSTRUCTION NCLOB NOT NULL,
                    IMMEDIATE_ACTION NCLOB,
                    MEDICAL_ATTENTION BOOLEAN DEFAULT FALSE,
                    EMERGENCY_CONTACT NVARCHAR(200),
                    DOCUMENT_NAME NVARCHAR(200),
                    CONFIDENCE DECIMAL(3,2),
                    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX IDX_TYPE (FIRST_AID_TYPE)
                )
                """
            }
            
            # Create tables
            for table_name, create_sql in tables.items():
                try:
                    # Check if table exists
                    check_table_sql = """
                    SELECT TABLE_NAME FROM SYS.TABLES 
                    WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
                    """
                    self.cursor.execute(check_table_sql, (schema_name, table_name))
                    result = self.cursor.fetchone()
                    
                    if result:
                        self.logger.info(f"Table {table_name} already exists")
                        continue
                    
                    # Create table
                    formatted_sql = create_sql.format(schema=schema_name)
                    self.cursor.execute(formatted_sql)
                    self.connection.commit()
                    
                    self.logger.info(f"Table {table_name} created successfully")
                    self.stats['tables_created'] += 1
                    
                except Exception as e:
                    self.logger.error(f"Error creating table {table_name}: {str(e)}")
                    self.stats['errors'] += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create tables: {str(e)}")
            return False
    
    def discover_input_files(self) -> List[str]:
        """
        Discover RDF/TTL files in the input directory
        
        Returns:
            List[str]: List of file paths to process
        """
        input_files = []
        input_dir = Path(self.config['input_directory'])
        
        if not input_dir.exists():
            self.logger.warning(f"Input directory not found: {input_dir}")
            return input_files
        
        # Search for supported file formats
        for file_format in self.config['supported_formats']:
            pattern = f"*{file_format}"
            files = list(input_dir.glob(pattern))
            input_files.extend([str(f) for f in files])
        
        # Also check for output files from previous step
        output_patterns = ['*enhanced*.ttl', '*enhanced*.rdf', '*extraction_results.json']
        for pattern in output_patterns:
            files = list(input_dir.glob(pattern))
            input_files.extend([str(f) for f in files])
        
        self.logger.info(f"Discovered {len(input_files)} input files")
        return input_files
    
    def load_rdf_file(self, file_path: str) -> Optional[Graph]:
        """
        Load RDF file content into a graph
        
        Args:
            file_path (str): Path to the RDF file
            
        Returns:
            Graph: RDF graph or None if failed
        """
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Load RDF graph
            rdf_graph = Graph()
            
            # Determine format based on file extension
            file_ext = file_path_obj.suffix.lower()
            format_map = {
                '.ttl': 'turtle',
                '.rdf': 'xml',
                '.n3': 'n3',
                '.nt': 'nt'
            }
            
            rdf_format = format_map.get(file_ext, 'turtle')
            rdf_graph.parse(file_path, format=rdf_format)
            
            total_triples = len(rdf_graph)
            if total_triples == 0:
                self.logger.warning(f"No triples found in file: {file_path}")
                return None
            
            self.logger.info(f"Loaded {total_triples:,} triples from {file_path}")
            return rdf_graph
            
        except Exception as e:
            self.logger.error(f"Failed to load RDF file {file_path}: {str(e)}")
            return None
    
    def load_json_file(self, file_path: str) -> Optional[Dict]:
        """
        Load JSON extraction results file
        
        Args:
            file_path (str): Path to the JSON file
            
        Returns:
            Dict: JSON data or None if failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"Loaded JSON data from {file_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to load JSON file {file_path}: {str(e)}")
            return None
    
    def upload_to_graph_store(self, ttl_content: str) -> bool:
        """
        Upload TTL content to HANA graph store
        
        Args:
            ttl_content (str): TTL content to upload
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            self.logger.info(f"Uploading triples to graph: {self.config['graph_name']}")
            
            if not self.connection or not self.cursor:
                raise Exception("No active HANA connection")
            
            # Prepare SPARQL headers for upload
            request_headers = []
            request_headers.append('rqx-load-protocol: true')
            request_headers.append(f'rqx-load-filename: {self.config["ttl_file"]}')
            request_headers.append(f'rqx-load-graphname: {self.config["graph_name"]}')
            headers_string = '\r\n'.join(request_headers)
            
            # Execute the upload using SPARQL_EXECUTE
            if self.cursor:
                self.cursor.callproc(
                    'SPARQL_EXECUTE', 
                    (ttl_content, headers_string, '', None)
                )
            
            self.logger.info("Upload completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Upload failed: {str(e)}")
            return False
    
    def verify_upload(self) -> bool:
        """
        Verify the upload by counting triples in the graph
        
        Returns:
            bool: True if verification successful
        """
        try:
            self.logger.info("Verifying upload...")
            
            # Count total triples in the graph
            count_query = f"""
            SELECT (COUNT(*) as ?count) WHERE {{
                GRAPH <{self.config['graph_name']}> {{
                    ?s ?p ?o .
                }}
            }}
            """
            
            if self.cursor:
                self.cursor.callproc('SPARQL_EXECUTE', (count_query, '', '?', None))
                
                # Check for specific RDF types
                type_query = f"""
                SELECT DISTINCT ?type WHERE {{
                    GRAPH <{self.config['graph_name']}> {{
                        ?s a ?type .
                    }}
                }} LIMIT 5
                """
                
                self.cursor.callproc('SPARQL_EXECUTE', (type_query, '', '?', None))
            
            self.logger.info("Upload verification completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Upload verification failed: {str(e)}")
            return False
    
    def close_connection(self):
        """
        Close HANA connection
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            self.logger.info("HANA connection closed")
        except Exception as e:
            self.logger.error(f"Error closing connection: {str(e)}")
    
    def run(self) -> bool:
        """
        Main execution method
        
        Returns:
            bool: True if entire process successful
        """
        try:
            self.logger.info("=" * 60)
            self.logger.info("STARTING HANA UPLOAD PROCESS")
            self.logger.info("=" * 60)
            
            # Step 1: Connect to HANA
            if not self.connect_to_hana():
                return False
            
            # Step 2: Load TTL file
            ttl_content = self.load_ttl_file()
            if not ttl_content:
                return False
            
            # Step 3: Upload to graph store
            if not self.upload_to_graph_store(ttl_content):
                return False
            
            # Step 4: Verify upload
            if not self.verify_upload():
                return False
            
            self.logger.info("=" * 60)
            self.logger.info("UPLOAD PROCESS COMPLETED SUCCESSFULLY!")
            self.logger.info(f"Graph name: {self.config['graph_name']}")
            self.logger.info(f"TTL file: {self.config['ttl_file']}")
            self.logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Upload process failed: {str(e)}")
            return False
        
        finally:
            # Always close connection
            self.close_connection()


def main():
    """
    Main execution function
    """
    print("=" * 80)
    print("SIMPLE HANA RDF UPLOADER - MODULE 3")
    print("=" * 80)
    print()
    
    try:
        # Initialize uploader with default config
        uploader = SimpleHanaUploader()
        
        # Run the upload process
        success = uploader.run()
        
        if success:
            print("\n✅ Upload completed successfully!")
            print("\nNext steps:")
            print("1. Use Module 4 to query the knowledge graph")
            print("2. Run SPARQL queries against the uploaded data")
        else:
            print("\n❌ Upload failed. Check the logs above for details.")
            sys.exit(1)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
