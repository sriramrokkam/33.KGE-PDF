"""
chat_service.py

Chat service for querying knowledge graphs using natural language.
"""
from typing import Dict, List
from .llm_client import CL_Orchestration_Service
from .hana_client import HANAClient

class ChatService:
    """Service for natural language querying of knowledge graphs."""
    
    def __init__(self, orch_service: CL_Orchestration_Service, hana_client: HANAClient):
        """
        Initialize chat service.
        
        Args:
            orch_service: Orchestration service for LLM interactions
            hana_client: HANA client for graph queries
        """
        self.orch_service = orch_service
        self.hana_client = hana_client
        
    def chat_with_graph(self, query: str, graph_name: str) -> Dict:
        """
        Process a natural language query against a knowledge graph.
        
        Args:
            query (str): Natural language query
            graph_name (str): Name of the graph to query
            
        Returns:
            Dict: Chat response
        """
        try:
            # First, search for relevant triples
            search_results = self._search_relevant_triples(query, graph_name)
            
            if not search_results["success"] or not search_results["results"]:
                return {
                    "success": False,
                    "query": query,
                    "answer": "I couldn't find any relevant information in the knowledge graph for your query.",
                    "relevant_triples": []
                }
            
            # Generate answer using LLM with context
            answer = self._generate_answer(query, search_results["results"])
            
            return {
                "success": True,
                "query": query,
                "answer": answer,
                "relevant_triples": search_results["results"],
                "graph_name": graph_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "error": f"Chat service error: {str(e)}",
                "answer": "I encountered an error while processing your query.",
                "relevant_triples": []
            }
    
    def _search_relevant_triples(self, query: str, graph_name: str) -> Dict:
        """Search for triples relevant to the query."""
        # Extract key terms from the query
        key_terms = self._extract_key_terms(query)
        
        all_results = []
        
        # Search for each key term
        for term in key_terms:
            search_result = self.hana_client.search_triples(graph_name, term)
            if search_result["success"] and search_result["results"]:
                all_results.extend(search_result["results"])
        
        # Remove duplicates
        unique_results = []
        seen = set()
        for result in all_results:
            key = (result["subject"], result["predicate"], result["object"])
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return {
            "success": True,
            "results": unique_results[:20],  # Limit to top 20 results
            "search_terms": key_terms
        }
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from the query for searching."""
        # Simple keyword extraction - can be enhanced with NLP
        import re
        
        # Remove common stop words
        stop_words = {
            'what', 'is', 'are', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'about', 'how', 'when', 'where', 'why', 'which', 'who', 'can', 'could', 'should', 'would',
            'tell', 'me', 'show', 'find', 'get', 'give', 'list', 'describe', 'explain'
        }
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-zA-Z0-9]+\b', query.lower())
        
        # Filter out stop words and short words
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Also look for compound terms (hyphenated words, chemical names)
        compound_terms = re.findall(r'\b[a-zA-Z0-9]+[-][a-zA-Z0-9]+\b', query)
        key_terms.extend([term.lower() for term in compound_terms])
        
        return list(set(key_terms))  # Remove duplicates
    
    def _generate_answer(self, query: str, relevant_triples: List[Dict]) -> str:
        """Generate an answer using LLM with relevant triples as context."""
        # Format triples as context
        context = "Based on the following information from the MSDS knowledge graph:\n\n"
        
        for i, triple in enumerate(relevant_triples[:10], 1):  # Limit context
            context += f"{i}. {triple['subject']} {triple['predicate']} {triple['object']}\n"
        
        # Create prompt for answer generation
        prompt = f"""
You are an expert assistant helping users understand Material Safety Data Sheets (MSDS) information.

{context}

User Question: {query}

Please provide a clear, accurate answer based on the information above. If the information is not sufficient to answer the question completely, say so and explain what information is available.

Answer:"""
        
        try:
            # Generate response using orchestration service
            response = self.orch_service.invoke_llm(
                prompt=prompt,
                model_name="anthropic--claude-4-sonnet",
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.strip()
            
        except Exception as e:
            return f"I found relevant information but encountered an error generating the response: {str(e)}"
    
    def get_graph_summary(self, graph_name: str) -> Dict:
        """Get a summary of the knowledge graph."""
        try:
            # Get some sample triples to understand the graph structure
            query_result = self.hana_client.query_knowledge_graph(graph_name, "")
            
            if not query_result["success"]:
                return {
                    "success": False,
                    "error": "Failed to access graph"
                }
            
            results = query_result["results"]
            
            if not results:
                return {
                    "success": True,
                    "summary": f"The graph '{graph_name}' appears to be empty.",
                    "stats": {
                        "total_triples": 0,
                        "unique_subjects": 0,
                        "unique_predicates": 0,
                        "unique_objects": 0
                    }
                }
            
            # Analyze the graph structure
            subjects = set()
            predicates = set()
            objects = set()
            
            for result in results:
                subjects.add(result["subject"])
                predicates.add(result["predicate"])
                objects.add(result["object"])
            
            # Generate summary
            summary = f"""
The knowledge graph '{graph_name}' contains information about MSDS data with:
- {len(results)} triples
- {len(subjects)} unique subjects
- {len(predicates)} unique predicates  
- {len(objects)} unique objects

Common predicates include: {', '.join(list(predicates)[:5])}
Main subjects include: {', '.join(list(subjects)[:5])}
"""
            
            return {
                "success": True,
                "summary": summary.strip(),
                "stats": {
                    "total_triples": len(results),
                    "unique_subjects": len(subjects),
                    "unique_predicates": len(predicates),
                    "unique_objects": len(objects)
                },
                "sample_predicates": list(predicates)[:10],
                "sample_subjects": list(subjects)[:10]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate graph summary: {str(e)}"
            }
    
    def suggest_questions(self, graph_name: str) -> Dict:
        """Suggest questions that can be asked about the graph."""
        try:
            # Get graph summary first
            summary_result = self.get_graph_summary(graph_name)
            
            if not summary_result["success"]:
                return summary_result
            
            # Generate suggested questions based on common MSDS queries
            suggestions = [
                "What are the hazards of this chemical?",
                "What are the first aid measures?",
                "How should this chemical be stored?",
                "What personal protective equipment is required?",
                "What are the physical properties?",
                "What are the fire fighting measures?",
                "How should spills be cleaned up?",
                "What are the disposal considerations?",
                "What regulatory information is available?",
                "What are the ingredients or components?"
            ]
            
            # Add specific questions based on available predicates
            predicates = summary_result.get("sample_predicates", [])
            specific_suggestions = []
            
            for predicate in predicates[:5]:
                if "hazard" in predicate.lower():
                    specific_suggestions.append(f"Tell me about {predicate}")
                elif "property" in predicate.lower():
                    specific_suggestions.append(f"What {predicate} information is available?")
                elif "measure" in predicate.lower():
                    specific_suggestions.append(f"What are the {predicate}?")
            
            all_suggestions = suggestions + specific_suggestions
            
            return {
                "success": True,
                "suggestions": all_suggestions[:15],  # Limit to 15 suggestions
                "graph_name": graph_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate question suggestions: {str(e)}"
            }


def create_chat_service(aic_config: Dict, orch_model_params: Dict, hana_config: Dict) -> ChatService:
    """
    Create a chat service with all required clients.
    
    Args:
        aic_config: AI Core configuration
        orch_model_params: Orchestration model parameters
        hana_config: HANA configuration
        
    Returns:
        ChatService: Configured chat service
    """
    orch_service = CL_Orchestration_Service(aic_config, orch_model_params)
    hana_client = HANAClient(hana_config)
    return ChatService(orch_service, hana_client)


# Example usage
if __name__ == "__main__":
    # This would be used for testing
    print("Chat service module loaded successfully")
