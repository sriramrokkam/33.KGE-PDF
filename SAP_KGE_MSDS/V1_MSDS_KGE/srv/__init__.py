"""
srv package - Supporting modules for MSDS Knowledge Graph Extraction

This package contains all the supporting modules for the MSDS Knowledge Graph
extraction system using Claude-4 Sonnet orchestration model.
"""

# Make imports available at package level
from .llm_client import CL_Foundation_Service, CL_Orchestration_Service
from .prompts import KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT, KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT_KG_RAG

__all__ = [
    'CL_Foundation_Service',
    'CL_Orchestration_Service', 
    'KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT',
    'KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT_KG_RAG'
]
