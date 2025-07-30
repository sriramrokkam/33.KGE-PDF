"""
hana_client.py

SAP HANA Cloud integration for storing and querying knowledge graphs.
"""

import os
import uuid
from typing import Dict, List, Tuple
from hdbcli import dbapi
import logging

logger = logging.getLogger(__name__)

class HANAClient:
    """Client for SAP HANA Cloud knowledge graph operations."""
    
    def __init__(self, hana_config: Dict):
        """
        Initialize HANA client.
        
        Args:
            hana_config: HANA connection configuration
        """
        self.hana_address = hana_config.get("hana_address")
        self.hana_port = hana_config.get("hana_port", "443")
        self.hana_user = hana_config.get("hana_user")
        self.hana_password = hana_config.get("hana_password")
        self.connection = None
        
    def connect(self) -> bool:
        """
        Establish connection to HANA Cloud.
        
        Returns:
            bool: True if connection successful
        """
        try:
            self.connection = dbapi.connect(
                address=self.hana_address,
                port=self.hana_port,
                user=self.hana_user,
                password=self.hana_password
            )
            logger.info("Successfully connected to HANA Cloud")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to HANA Cloud: {e}")
            return False
    
    def disconnect(self):
        """Close HANA connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from HANA Cloud")
    
    def test_connection(self) -> Dict:
        """
        Test HANA connection.
        
        Returns:
            Dict: Connection test results
        """
        try:
            if not self.connect():
                return {
                    "success": False,
                    "error": "Failed to establish connection"
                }
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT CURRENT_TIMESTAMP FROM DUMMY")
            result = cursor.fetchone()
            cursor.close()
            
            return {
                "success": True,
                "timestamp": str(result[0]),
                "status": "Connected to HANA Cloud"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection test failed: {str(e)}"
            }
        finally:
            self.disconnect()
    
    def store_knowledge_graph(self, graph_name: str, triples: List[Tuple], metadata: Dict = None) -> Dict:
        """
        Store knowledge graph triples in HANA Cloud.
        
        Args:
            graph_name (str): Name of the graph
            triples (List[Tuple]): List of (subject, predicate, object) triples
            metadata (Dict): Optional metadata
            
        Returns:
            Dict: Storage results
        """
        if not self.connect():
            return {
                "success": False,
                "error": "Failed to connect to HANA Cloud"
            }
        
        try:
            cursor = self.connection.cursor()
            graph_id = str(uuid.uuid4())
            
            # Create graph IRI
            graph_iri = self._to_iri(graph_name, base="http://graph/")
            
            # Store metadata
            if metadata:
                self._store_graph_metadata(cursor, graph_id, graph_name, metadata)
            
            # Store triples
            stored_count = 0
            for idx, (subj, pred, obj) in enumerate(triples, start=1):
                try:
                    subj_iri = self._to_iri(subj, base="http://msds.com/resource/")
                    pred_iri = self._to_iri(pred, base="http://msds.com/property/")
                    obj_literal = self._to_literal(obj)
                    
                    sparql_insert = f"""
                    INSERT DATA {{
                      GRAPH {graph_iri} {{
                        {subj_iri} {pred_iri} {obj_literal} .
                      }}
                    }}
                    """.strip()
                    
                    cursor.callproc("SPARQL_EXECUTE", [sparql_insert, "", None, None])
                    stored_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to store triple {idx}: {e}")
                    continue
            
            self.connection.commit()
            cursor.close()
            
            return {
                "success": True,
                "graph_id": graph_id,
                "graph_name": graph_name,
                "stored_triples": stored_count,
                "total_triples": len(triples),
                "hana_status": "stored",
                "graph_iri": graph_iri
            }
            
        except Exception as e:
            logger.error(f"Failed to store knowledge graph: {e}")
            return {
                "success": False,
                "error": f"Failed to store knowledge graph: {str(e)}"
            }
        finally:
            self.disconnect()
    
    def _store_graph_metadata(self, cursor, graph_id: str, graph_name: str, metadata: Dict):
        """Store graph metadata in a separate table."""
        try:
            # Create metadata table if it doesn't exist
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS MSDS_GRAPH_METADATA (
                GRAPH_ID NVARCHAR(36) PRIMARY KEY,
                GRAPH_NAME NVARCHAR(255),
                CREATED_DATE TIMESTAMP,
                TRIPLES_COUNT INTEGER,
                DOCUMENT_PAGES INTEGER,
                DOCUMENT_LENGTH INTEGER,
                VALIDATION_SCORE DECIMAL(5,2),
                METADATA NCLOB
            )
            """
            cursor.execute(create_table_sql)
            
            # Insert metadata
            insert_sql = """
            INSERT INTO MSDS_GRAPH_METADATA 
            (GRAPH_ID, GRAPH_NAME, CREATED_DATE, TRIPLES_COUNT, DOCUMENT_PAGES, DOCUMENT_LENGTH, VALIDATION_SCORE, METADATA)
            VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)
            """
            
            import json
            cursor.execute(insert_sql, [
                graph_id,
                graph_name,
                metadata.get("triples_count", 0),
                metadata.get("document_pages", 0),
                metadata.get("document_length", 0),
                metadata.get("validation_score", 0.0),
                json.dumps(metadata)
            ])
            
        except Exception as e:
            logger.warning(f"Failed to store metadata: {e}")
    
    def query_knowledge_graph(self, graph_name: str, query: str) -> Dict:
        """
        Query knowledge graph using SPARQL.
        
        Args:
            graph_name (str): Name of the graph
            query (str): SPARQL query
            
        Returns:
            Dict: Query results
        """
        if not self.connect():
            return {
                "success": False,
                "error": "Failed to connect to HANA Cloud"
            }
        
        try:
            cursor = self.connection.cursor()
            graph_iri = self._to_iri(graph_name, base="http://graph/")
            
            # Execute SPARQL query
            full_query = f"""
            SELECT ?s ?p ?o
            FROM {graph_iri}
            WHERE {{
              ?s ?p ?o .
              {query}
            }}
            LIMIT 100
            """
            
            cursor.execute(f"SELECT * FROM SPARQL_TABLE('{full_query}')")
            results = cursor.fetchall()
            cursor.close()
            
            return {
                "success": True,
                "results": [
                    {
                        "subject": str(row[0]),
                        "predicate": str(row[1]),
                        "object": str(row[2])
                    }
                    for row in results
                ],
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Failed to query knowledge graph: {e}")
            return {
                "success": False,
                "error": f"Query failed: {str(e)}"
            }
        finally:
            self.disconnect()
    
    def list_stored_graphs(self) -> Dict:
        """
        List all stored knowledge graphs.
        
        Returns:
            Dict: List of stored graphs
        """
        if not self.connect():
            return {
                "success": False,
                "error": "Failed to connect to HANA Cloud"
            }
        
        try:
            cursor = self.connection.cursor()
            
            # Query metadata table
            query_sql = """
            SELECT GRAPH_ID, GRAPH_NAME, CREATED_DATE, TRIPLES_COUNT, VALIDATION_SCORE
            FROM MSDS_GRAPH_METADATA
            ORDER BY CREATED_DATE DESC
            """
            
            cursor.execute(query_sql)
            results = cursor.fetchall()
            cursor.close()
            
            graphs = []
            for row in results:
                graphs.append({
                    "graph_id": row[0],
                    "graph_name": row[1],
                    "created_date": row[2].isoformat() if row[2] else None,
                    "triples_count": row[3],
                    "validation_score": float(row[4]) if row[4] else 0.0
                })
            
            return {
                "success": True,
                "graphs": graphs,
                "total_graphs": len(graphs)
            }
            
        except Exception as e:
            logger.error(f"Failed to list graphs: {e}")
            return {
                "success": False,
                "error": f"Failed to list graphs: {str(e)}",
                "graphs": []
            }
        finally:
            self.disconnect()
    
    def delete_knowledge_graph(self, graph_name: str) -> Dict:
        """
        Delete a knowledge graph.
        
        Args:
            graph_name (str): Name of the graph to delete
            
        Returns:
            Dict: Deletion results
        """
        if not self.connect():
            return {
                "success": False,
                "error": "Failed to connect to HANA Cloud"
            }
        
        try:
            cursor = self.connection.cursor()
            graph_iri = self._to_iri(graph_name, base="http://graph/")
            
            # Delete from SPARQL store
            sparql_delete = f"DROP GRAPH {graph_iri}"
            cursor.callproc("SPARQL_EXECUTE", [sparql_delete, "", None, None])
            
            # Delete metadata
            delete_metadata_sql = "DELETE FROM MSDS_GRAPH_METADATA WHERE GRAPH_NAME = ?"
            cursor.execute(delete_metadata_sql, [graph_name])
            
            self.connection.commit()
            cursor.close()
            
            return {
                "success": True,
                "message": f"Graph '{graph_name}' deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete graph: {e}")
            return {
                "success": False,
                "error": f"Failed to delete graph: {str(e)}"
            }
        finally:
            self.disconnect()
    
    def search_triples(self, graph_name: str, search_term: str) -> Dict:
        """
        Search for triples containing a specific term.
        
        Args:
            graph_name (str): Name of the graph
            search_term (str): Term to search for
            
        Returns:
            Dict: Search results
        """
        if not self.connect():
            return {
                "success": False,
                "error": "Failed to connect to HANA Cloud"
            }
        
        try:
            cursor = self.connection.cursor()
            graph_iri = self._to_iri(graph_name, base="http://graph/")
            
            # Search query
            sparql_query = f"""
            SELECT ?s ?p ?o
            FROM {graph_iri}
            WHERE {{
              ?s ?p ?o .
              FILTER (
                CONTAINS(LCASE(STR(?s)), LCASE("{search_term}")) ||
                CONTAINS(LCASE(STR(?p)), LCASE("{search_term}")) ||
                CONTAINS(LCASE(STR(?o)), LCASE("{search_term}"))
              )
            }}
            LIMIT 50
            """
            
            cursor.execute(f"SELECT * FROM SPARQL_TABLE('{sparql_query}')")
            results = cursor.fetchall()
            cursor.close()
            
            return {
                "success": True,
                "search_term": search_term,
                "results": [
                    {
                        "subject": str(row[0]),
                        "predicate": str(row[1]),
                        "object": str(row[2])
                    }
                    for row in results
                ],
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Failed to search triples: {e}")
            return {
                "success": False,
                "error": f"Search failed: {str(e)}"
            }
        finally:
            self.disconnect()
    
    def _to_iri(self, value: str, base: str = "http://msds.com/") -> str:
        """Convert value to IRI format."""
        import re
        encoded_part = re.sub(
            r"[^a-zA-Z0-9\\-_\\.]", lambda m: f"%{ord(m.group(0)):02X}", value
        )
        return f"<{base}{encoded_part}>"
    
    def _to_literal(self, value: str) -> str:
        """Convert value to literal format."""
        if value is None:
            return '""'
        escaped = (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
        )
        return f'"{escaped}"'


def create_hana_client(hana_config: Dict) -> HANAClient:
    """
    Create a HANA client with configuration.
    
    Args:
        hana_config: HANA connection configuration
        
    Returns:
        HANAClient: Configured HANA client
    """
    return HANAClient(hana_config)


def test_connection() -> Dict:
    """Test HANA connection using environment variables."""
    hana_config = {
        "hana_address": os.getenv("HANA_ADDRESS"),
        "hana_port": os.getenv("HANA_PORT", "443"),
        "hana_user": os.getenv("HANA_USER"),
        "hana_password": os.getenv("HANA_PASSWORD")
    }
    
    client = create_hana_client(hana_config)
    return client.test_connection()


# Example usage
if __name__ == "__main__":
    # Test connection
    result = test_connection()
    print(f"Connection test: {result}")
    
    if result["success"]:
        print("HANA Cloud connection successful!")
    else:
        print(f"Connection failed: {result.get('error')}")
