"""
graph_processor.py

Graph processing utilities for knowledge graph extraction and visualization.
"""

import os
import re
import uuid
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Dict, List, Tuple
from langchain_community.document_loaders import PyPDFLoader
from .llm_client import CL_Orchestration_Service
from .prompts import KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT

class GraphProcessor:
    """Processes documents to extract and visualize knowledge graphs."""
    
    def __init__(self, orch_service: CL_Orchestration_Service):
        """
        Initialize the graph processor.
        
        Args:
            orch_service: Orchestration service for LLM interactions
        """
        self.orch_service = orch_service
        self.extraction_cache = {}
        
    def extract_triples_from_pdf(self, pdf_path: str, extraction_id: str = None) -> Dict:
        """
        Extract knowledge graph triples from a PDF document.
        
        Args:
            pdf_path (str): Path to the PDF file
            extraction_id (str): Optional extraction ID for caching
            
        Returns:
            Dict: Extraction results
        """
        if not extraction_id:
            extraction_id = str(uuid.uuid4())
            
        try:
            # Load PDF content
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            
            doc_content = 'This is a MSDS specification: '
            for doc in docs:
                doc_content = doc_content + ' ' + doc.page_content
            
            # Extract triples using orchestration service
            triples, raw_response = self._extract_triples_with_orchestration(
                doc_content, 
                KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT.template
            )
            
            # Analyze quality
            quality_metrics = self._analyze_extraction_quality(triples, raw_response)
            
            # Cache results
            extraction_result = {
                "extraction_id": extraction_id,
                "success": True,
                "triples": [
                    {
                        "subject": subj,
                        "predicate": pred,
                        "object": obj
                    }
                    for subj, pred, obj in triples
                ],
                "triples_count": len(triples),
                "quality_metrics": quality_metrics,
                "raw_response_length": len(raw_response),
                "document_pages": len(docs),
                "document_length": len(doc_content)
            }
            
            self.extraction_cache[extraction_id] = {
                "result": extraction_result,
                "triples_raw": triples,
                "raw_response": raw_response,
                "doc_content": doc_content
            }
            
            return extraction_result
            
        except Exception as e:
            error_result = {
                "extraction_id": extraction_id,
                "success": False,
                "error": f"Failed to extract triples: {str(e)}",
                "triples": [],
                "triples_count": 0,
                "quality_metrics": {}
            }
            
            self.extraction_cache[extraction_id] = {
                "result": error_result,
                "error": str(e)
            }
            
            return error_result
    
    def _extract_triples_with_orchestration(self, doc_content: str, prompt_template: str) -> Tuple[List[Tuple], str]:
        """Extract triples using orchestration service."""
        try:
            # Format the prompt with the document content
            formatted_prompt = prompt_template.format(text=doc_content)
            
            # Use orchestration service for extraction
            response = self.orch_service.invoke_llm(
                prompt=formatted_prompt,
                model_name="anthropic--claude-4-sonnet",
                temperature=0.3,
                max_tokens=15000
            )
            
            # Parse the response to extract triples
            triples = self._parse_triples_from_response(response)
            
            return triples, response
            
        except Exception as e:
            raise Exception(f"Error during triple extraction: {str(e)}")
    
    def _parse_triples_from_response(self, response: str) -> List[Tuple]:
        """Parse triples from the LLM response with enhanced parsing."""
        triples = []
        lines = response.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Method 1: Standard parentheses format (Subject, Predicate, Object)
            if line.startswith('(') and line.endswith(')'):
                try:
                    content = line[1:-1]
                    parts = [part.strip() for part in content.split(',')]
                    
                    if len(parts) == 3:
                        subject, predicate, obj = parts
                        # Clean up quotes if present
                        subject = subject.strip('"\'')
                        predicate = predicate.strip('"\'')
                        obj = obj.strip('"\'')
                        triples.append((subject, predicate, obj))
                        continue
                        
                except Exception:
                    pass
            
            # Method 2: Text format "Subject: X, Predicate: Y, Object: Z"
            if 'subject:' in line.lower() and 'predicate:' in line.lower() and 'object:' in line.lower():
                try:
                    pattern = r'subject:\s*([^,]+),\s*predicate:\s*([^,]+),\s*object:\s*(.+)'
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        subject, predicate, obj = match.groups()
                        subject = subject.strip().strip('"\'')
                        predicate = predicate.strip().strip('"\'')
                        obj = obj.strip().strip('"\'')
                        triples.append((subject, predicate, obj))
                        continue
                except Exception:
                    pass
            
            # Method 3: Delimiter-based parsing
            if '{KG_TRIPLE_DELIMITER}' in line:
                try:
                    parts = line.split('{KG_TRIPLE_DELIMITER}')[0].strip()
                    if parts.startswith('(') and parts.endswith(')'):
                        content = parts[1:-1]
                        triple_parts = [part.strip().strip('"\'') for part in content.split(',')]
                        if len(triple_parts) == 3:
                            triples.append(tuple(triple_parts))
                            continue
                except Exception:
                    pass
            
            # Method 4: Flexible comma-separated parsing
            if ',' in line and line.count(',') >= 2:
                try:
                    if '(' in line and ')' in line:
                        start = line.find('(')
                        end = line.rfind(')')
                        if start != -1 and end != -1 and end > start:
                            content = line[start+1:end]
                            parts = [part.strip().strip('"\'') for part in content.split(',')]
                            if len(parts) >= 3:
                                # Take first 3 parts
                                subject, predicate, obj = parts[0], parts[1], parts[2]
                                if subject and predicate and obj:  # Make sure none are empty
                                    triples.append((subject, predicate, obj))
                                    continue
                except Exception:
                    pass
        
        return triples
    
    def _analyze_extraction_quality(self, triples: List[Tuple], raw_response: str) -> Dict:
        """Analyze the quality of extracted triples."""
        if not triples:
            return {
                "unique_subjects": 0,
                "unique_predicates": 0,
                "unique_objects": 0,
                "correct_format_percentage": 0.0,
                "most_common_predicates": []
            }
        
        # Analyze subjects, predicates, objects
        subjects = {s for s, _, _ in triples}
        predicates = {p for _, p, _ in triples}
        objects = {o for _, _, o in triples}
        
        # Count predicate usage
        predicate_counts = {}
        for _, pred, _ in triples:
            predicate_counts[pred] = predicate_counts.get(pred, 0) + 1
        
        sorted_predicates = sorted(predicate_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Check for correct Subject-Predicate-Object format
        correct_format_count = 0
        relationship_words = ['is a', 'has', 'includes', 'is classified as', 'is manufactured by', 
                            'is located at', 'is regulated by', 'is exposed to', 'is protected by', 
                            'is described by', 'is recommended for']
        
        for subj, pred, obj in triples:
            if any(rel_word in pred.lower() for rel_word in relationship_words):
                correct_format_count += 1
        
        correct_format_percentage = (correct_format_count / len(triples)) * 100 if triples else 0
        
        return {
            "unique_subjects": len(subjects),
            "unique_predicates": len(predicates),
            "unique_objects": len(objects),
            "correct_format_percentage": round(correct_format_percentage, 2),
            "most_common_predicates": [
                {"predicate": pred, "count": count}
                for pred, count in sorted_predicates[:5]
            ]
        }
    
    def generate_visualization(self, extraction_id: str, output_dir: str = "static/graphs") -> Dict:
        """
        Generate a visualization of the knowledge graph.
        
        Args:
            extraction_id (str): ID of the extraction
            output_dir (str): Directory to save the visualization
            
        Returns:
            Dict: Visualization results
        """
        if extraction_id not in self.extraction_cache:
            return {
                "success": False,
                "error": "Extraction ID not found"
            }
        
        try:
            cached_data = self.extraction_cache[extraction_id]
            triples = cached_data["triples_raw"]
            
            if not triples:
                return {
                    "success": False,
                    "error": "No triples found for visualization"
                }
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate visualization
            filename = f"graph_{extraction_id}.png"
            filepath = os.path.join(output_dir, filename)
            
            graph_data = self._create_graph_visualization(triples, filepath)
            
            return {
                "success": True,
                "visualization_url": f"/{filepath}",
                "filename": filename,
                "graph_data": graph_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate visualization: {str(e)}"
            }
    
    def _create_graph_visualization(self, triples: List[Tuple], output_path: str) -> Dict:
        """Create and save a graph visualization."""
        G = nx.DiGraph()
        
        # Collect all types of nodes
        subjects = {s for s, _, _ in triples}
        predicates = {p for _, p, _ in triples}
        objects = {o for _, _, o in triples}
        
        # Add nodes and edges
        for s, p, o in triples:
            G.add_node(s)
            G.add_node(p)
            G.add_node(o)
            G.add_edge(s, p)
            G.add_edge(p, o)
        
        # Set up the plot
        plt.figure(figsize=(20, 16))
        pos = nx.spring_layout(G, k=3.0, iterations=300, seed=42)
        
        # Group nodes into categories
        node_groups = {
            "predicates": list(predicates),
            "subjects": list(subjects - predicates - objects),
            "objects": list(objects - subjects - predicates),
            "shared": list((subjects & objects) - predicates)
        }
        
        # Styling for different groups
        node_styles = {
            "predicates": {'color': '#E6E6FA', 'size': 3000, 'ec': 'darkviolet'},
            "subjects":   {'color': '#98FB98', 'size': 2500, 'ec': 'darkgreen'},
            "objects":    {'color': '#FFB6C1', 'size': 2500, 'ec': 'crimson'},
            "shared":     {'color': '#DDA0DD', 'size': 2800, 'ec': 'purple'}
        }
        
        # Draw nodes
        for group, style in node_styles.items():
            if node_groups[group]:
                nx.draw_networkx_nodes(
                    G, pos, nodelist=node_groups[group],
                    node_size=style['size'],
                    node_color=style['color'],
                    edgecolors=style['ec'],
                    alpha=0.8
                )
        
        # Draw labels and edges
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
        nx.draw_networkx_edges(G, pos, width=2, alpha=0.6, edge_color='gray')
        
        # Add legend
        legend_handles = [
            mpatches.Patch(facecolor=node_styles["subjects"]['color'],
                           edgecolor=node_styles["subjects"]['ec'],
                           label='Subjects'),
            mpatches.Patch(facecolor=node_styles["predicates"]['color'],
                           edgecolor=node_styles["predicates"]['ec'],
                           label='Predicates'),
            mpatches.Patch(facecolor=node_styles["objects"]['color'],
                           edgecolor=node_styles["objects"]['ec'],
                           label='Objects'),
        ]
        plt.legend(handles=legend_handles, loc='upper right', title='Node Types', framealpha=0.9)
        
        plt.title('MSDS Knowledge Graph', fontsize=20, pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()  # Close to free memory
        
        # Return graph data for API response
        return {
            "nodes": [
                {
                    "id": node,
                    "type": self._get_node_type(node, node_groups),
                    "position": {"x": float(pos[node][0]), "y": float(pos[node][1])}
                }
                for node in G.nodes()
            ],
            "edges": [
                {
                    "source": edge[0],
                    "target": edge[1]
                }
                for edge in G.edges()
            ],
            "stats": {
                "total_nodes": G.number_of_nodes(),
                "total_edges": G.number_of_edges(),
                "node_groups": {k: len(v) for k, v in node_groups.items()}
            }
        }
    
    def _get_node_type(self, node: str, node_groups: Dict) -> str:
        """Determine the type of a node."""
        for group_type, nodes in node_groups.items():
            if node in nodes:
                return group_type
        return "unknown"
    
    def get_extraction_result(self, extraction_id: str) -> Dict:
        """Get cached extraction result."""
        if extraction_id not in self.extraction_cache:
            return {
                "success": False,
                "error": "Extraction ID not found"
            }
        
        return self.extraction_cache[extraction_id]["result"]
    
    def clear_cache(self, extraction_id: str = None):
        """Clear extraction cache."""
        if extraction_id:
            self.extraction_cache.pop(extraction_id, None)
        else:
            self.extraction_cache.clear()


# Utility functions
def create_graph_processor(aic_config: Dict, orch_model_params: Dict) -> GraphProcessor:
    """
    Create a graph processor with orchestration service.
    
    Args:
        aic_config: AI Core configuration
        orch_model_params: Orchestration model parameters
        
    Returns:
        GraphProcessor: Configured graph processor
    """
    orch_service = CL_Orchestration_Service(aic_config, orch_model_params)
    return GraphProcessor(orch_service)
