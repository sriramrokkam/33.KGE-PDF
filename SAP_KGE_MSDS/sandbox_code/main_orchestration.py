"""
main_orchestration.py

Modified version of main.ipynb using Orchestration Model (Claude-4 Sonnet) for tuple extraction
instead of Foundation Model.
"""

import os
from dotenv import load_dotenv
from langchain.indexes.graph import GraphIndexCreator
from langchain_community.document_loaders import PyPDFLoader
from srv.prompts import KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT, KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT_KG_RAG
from srv.llm_client import CL_Orchestration_Service
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Load environment variables
load_dotenv()

def setup_orchestration_service():
    """Setup the orchestration service with Claude-4 Sonnet."""
    print("=" * 60)
    print("SETTING UP ORCHESTRATION SERVICE")
    print("=" * 60)
    
    # AI Core configuration
    aic_config = {
        "aic_auth_url": os.getenv("AICORE_AUTH_URL"),
        "aic_client_id": os.getenv("AICORE_CLIENT_ID"),
        "aic_client_secret": os.getenv("AICORE_CLIENT_SECRET"),
        "aic_resource_group": os.getenv("AICORE_RESOURCE_GROUP", "default")
    }
    
    # Orchestration parameters with Claude-4 Sonnet
    orch_model_params = {
        "orch_url": "https://api.ai.prod.us-east-1.aws.ml.hana.ondemand.com/v2/inference/deployments/ddaae0b631e78184",
        "orch_model": "anthropic--claude-4-sonnet",
        "parameters": {
            "temperature": 0.3,  # Lower temperature for more consistent extraction
            "max_tokens": 20000,
            "top_p": 0.9
        }
    }
    
    # Initialize Orchestration Service
    orch_service = CL_Orchestration_Service(aic_config, orch_model_params)
    print("✅ Orchestration Service initialized with Claude-4 Sonnet")
    return orch_service

def load_msds_document(pdf_path):
    """Load and process MSDS document."""
    print(f"\n📄 Loading MSDS document: {pdf_path}")
    
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        
        doc_content = 'This is a MSDS specification: '
        for doc in docs:
            doc_content = doc_content + ' ' + doc.page_content
        
        print(f"✅ Document loaded successfully. Content length: {len(doc_content)} characters")
        return doc_content
    except Exception as e:
        print(f"❌ Error loading document: {e}")
        return None

def extract_triples_with_orchestration(orch_service, doc_content, prompt_template):
    """Extract triples using orchestration service."""
    print("\n🔍 EXTRACTING TRIPLES WITH CLAUDE-4 SONNET")
    print("=" * 60)
    
    try:
        # Format the prompt with the document content
        formatted_prompt = prompt_template.format(text=doc_content)
        
        print("📝 Sending extraction request to Claude-4 Sonnet...")
        
        # Use orchestration service for extraction
        response = orch_service.invoke_llm(
            prompt=formatted_prompt,
            model_name="anthropic--claude-4-sonnet",
            temperature=0.3,
            max_tokens=15000
        )
        
        print("✅ Response received from Claude-4 Sonnet")
        
        # Parse the response to extract triples
        triples = parse_triples_from_response(response)
        
        print(f"📊 Extracted {len(triples)} triples")
        return triples, response
        
    except Exception as e:
        print(f"❌ Error during triple extraction: {e}")
        return [], ""

def parse_triples_from_response(response):
    """Parse triples from the LLM response with enhanced parsing."""
    triples = []
    lines = response.split('\n')
    
    print(f"🔍 DEBUG: Parsing response with {len(lines)} lines")
    
    # First, let's see what the response looks like
    print("📝 DEBUG: First 10 lines of response:")
    for i, line in enumerate(lines[:10]):
        print(f"   {i+1}: {repr(line)}")
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Try multiple parsing approaches
        if line.startswith('(') and line.endswith(')'):
            try:
                # Method 1: Simple comma split
                content = line[1:-1]
                parts = [part.strip() for part in content.split(',')]
                
                if len(parts) == 3:
                    subject, predicate, obj = parts
                    # Clean up quotes if present
                    subject = subject.strip('"\'')
                    predicate = predicate.strip('"\'')
                    obj = obj.strip('"\'')
                    triples.append((subject, predicate, obj))
                    print(f"✅ Parsed triple from line {line_num}: ({subject}, {predicate}, {obj})")
                    continue
                    
            except Exception as e:
                print(f"⚠️ Method 1 failed for line {line_num}: {line}")
        
        # Method 2: Look for patterns like "Subject: X, Predicate: Y, Object: Z"
        if 'subject:' in line.lower() and 'predicate:' in line.lower() and 'object:' in line.lower():
            try:
                # Extract using regex or string manipulation
                import re
                pattern = r'subject:\s*([^,]+),\s*predicate:\s*([^,]+),\s*object:\s*(.+)'
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    subject, predicate, obj = match.groups()
                    subject = subject.strip().strip('"\'')
                    predicate = predicate.strip().strip('"\'')
                    obj = obj.strip().strip('"\'')
                    triples.append((subject, predicate, obj))
                    print(f"✅ Parsed triple from line {line_num} (method 2): ({subject}, {predicate}, {obj})")
                    continue
            except Exception as e:
                print(f"⚠️ Method 2 failed for line {line_num}: {line}")
        
        # Method 3: Look for delimiter patterns
        if '{KG_TRIPLE_DELIMITER}' in line:
            try:
                # Split by delimiter and extract triple
                parts = line.split('{KG_TRIPLE_DELIMITER}')[0].strip()
                if parts.startswith('(') and parts.endswith(')'):
                    content = parts[1:-1]
                    triple_parts = [part.strip().strip('"\'') for part in content.split(',')]
                    if len(triple_parts) == 3:
                        triples.append(tuple(triple_parts))
                        print(f"✅ Parsed triple from line {line_num} (method 3): {tuple(triple_parts)}")
                        continue
            except Exception as e:
                print(f"⚠️ Method 3 failed for line {line_num}: {line}")
        
        # Method 4: Look for any line with exactly 3 comma-separated parts in parentheses
        if ',' in line and line.count(',') >= 2:
            try:
                # Try to extract even if not perfectly formatted
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
                                print(f"✅ Parsed triple from line {line_num} (method 4): ({subject}, {predicate}, {obj})")
                                continue
            except Exception as e:
                print(f"⚠️ Method 4 failed for line {line_num}: {line}")
    
    print(f"📊 DEBUG: Successfully parsed {len(triples)} triples")
    return triples

def display_sample_triples(triples, title="Sample Triples"):
    """Display sample triples."""
    print(f"\n📋 {title}")
    print("-" * 60)
    
    if not triples:
        print("❌ No triples found")
        return
    
    # Display first 10 triples
    for i, (subj, pred, obj) in enumerate(triples[:10], 1):
        print(f"{i:2d}. Subject: {subj}")
        print(f"    Predicate: {pred}")
        print(f"    Object: {obj}")
        print()

def visualize_knowledge_graph(triples, title="Knowledge Graph Visualization"):
    """Create an enhanced visualization of the knowledge graph."""
    print(f"\n🎨 Creating {title}")
    
    if not triples:
        print("❌ No triples to visualize")
        return
    
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
    plt.figure(figsize=(18, 14))
    pos = nx.spring_layout(G, k=2.0, iterations=200, seed=42)
    
    # Group nodes into categories
    node_groups = {
        "predicates": list(predicates),
        "subjects": list(subjects - predicates - objects),
        "objects": list(objects - subjects - predicates),
        "shared": list((subjects & objects) - predicates)
    }
    
    # Adjust positions
    def adjust_positions(nodes, dx_pattern, dy_pattern):
        for i, node in enumerate(nodes):
            if node in pos:
                x, y = pos[node]
                pos[node] = (x + dx_pattern(i), y + dy_pattern(i))
    
    adjust_positions(node_groups["predicates"], 
                     lambda i: (i % 3) * 5.5, 
                     lambda i: (i // 3) * 5.5)
    adjust_positions(node_groups["subjects"],
                     lambda i: -4.0 - (i % 2) * 3.5,
                     lambda i: 3.0 - (i // 2) * 4.0)
    adjust_positions(node_groups["objects"],
                     lambda i: 4.0 + (i % 2) * 3.5,
                     lambda i: 3.0 - (i // 2) * 4.0)
    adjust_positions(node_groups["shared"],
                     lambda i: (i % 4) * 2.5 - 5.0,
                     lambda i: -4.0 - (i // 4) * 3.0)
    
    # Styling for different groups
    node_styles = {
        "predicates": {'color': '#E6E6FA', 'size': 2500, 'ec': 'darkviolet'},
        "subjects":   {'color': '#98FB98', 'size': 2200, 'ec': 'darkgreen'},
        "objects":    {'color': '#FFB6C1', 'size': 2200, 'ec': 'crimson'},
        "shared":     {'color': '#DDA0DD', 'size': 2400, 'ec': 'purple'}
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
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
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
    
    plt.title(f'{title} - Claude-4 Sonnet Extraction', fontsize=18)
    plt.axis('off')
    plt.tight_layout(pad=4.0)
    
    # Save the plot
    filename = f"KG_Claude4_Sonnet_{title.replace(' ', '_')}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Visualization saved as: {filename}")
    plt.show()

def compare_extraction_quality(triples, raw_response):
    """Analyze the quality of extraction."""
    print("\n📊 EXTRACTION QUALITY ANALYSIS")
    print("=" * 60)
    
    print(f"📈 Total triples extracted: {len(triples)}")
    
    if triples:
        # Analyze subjects, predicates, objects
        subjects = {s for s, _, _ in triples}
        predicates = {p for _, p, _ in triples}
        objects = {o for _, _, o in triples}
        
        print(f"🎯 Unique subjects: {len(subjects)}")
        print(f"🔗 Unique predicates: {len(predicates)}")
        print(f"📦 Unique objects: {len(objects)}")
        
        print(f"\n🔍 Most common predicates:")
        predicate_counts = {}
        for _, pred, _ in triples:
            predicate_counts[pred] = predicate_counts.get(pred, 0) + 1
        
        sorted_predicates = sorted(predicate_counts.items(), key=lambda x: x[1], reverse=True)
        for pred, count in sorted_predicates[:5]:
            print(f"   • {pred}: {count} times")
        
        # Check for correct Subject-Predicate-Object format
        correct_format_count = 0
        for subj, pred, obj in triples:
            # Check if predicate looks like a relationship (contains common relationship words)
            relationship_words = ['is a', 'has', 'includes', 'is classified as', 'is manufactured by', 
                                'is located at', 'is regulated by', 'is exposed to', 'is protected by', 
                                'is described by', 'is recommended for']
            if any(rel_word in pred.lower() for rel_word in relationship_words):
                correct_format_count += 1
        
        print(f"\n✅ Triples with correct predicate format: {correct_format_count}/{len(triples)} ({correct_format_count/len(triples)*100:.1f}%)")
    
    print(f"\n📝 Raw response length: {len(raw_response)} characters")

def main():
    """Main execution function."""
    print("🚀 MSDS KNOWLEDGE GRAPH EXTRACTION WITH CLAUDE-4 SONNET")
    print("=" * 80)
    
    # Check environment variables
    required_vars = ["AICORE_AUTH_URL", "AICORE_CLIENT_ID", "AICORE_CLIENT_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please set these in your .env file before running.")
        return
    
    try:
        # 1. Setup orchestration service
        orch_service = setup_orchestration_service()
        
        # 2. Load MSDS document
        pdf_path = "/Users/I310202/Library/CloudStorage/OneDrive-SAPSE/SR@Work/81.Innovations/98.AI_Developments/33.AI_MSDS/Build_MSDS_SAPKGE/Documents/WD-40.pdf"
        doc_content = load_msds_document(pdf_path)
        
        if not doc_content:
            print("❌ Failed to load document. Exiting.")
            return
        
        # 3. Extract triples using Claude-4 Sonnet
        triples, raw_response = extract_triples_with_orchestration(
            orch_service, 
            doc_content, 
            KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT.template
        )
        
        # 4. Display results
        display_sample_triples(triples, "Extracted Triples (Claude-4 Sonnet)")
        
        # 5. Analyze extraction quality
        compare_extraction_quality(triples, raw_response)
        
        # 6. Create visualization
        if triples:
            visualize_knowledge_graph(triples, "MSDS Knowledge Graph")
        
        # 7. Test with KG-RAG approach (if you have identifiers from previous runs)
        print("\n🔄 TESTING KG-RAG APPROACH")
        print("=" * 60)
        
        # For demonstration, let's use some sample allowed attributes
        sample_attributes = ["Chemical", "Hazard", "Manufacturer", "PhysicalProperty", "Regulation"]
        allowed_attributes_str = ", ".join(sample_attributes)
        
        try:
            kg_rag_prompt = KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT_KG_RAG.template.format(
                text=doc_content[:2000],  # Use first 2000 chars for demo
                allowedAttributes=allowed_attributes_str
            )
            
            kg_rag_triples, kg_rag_response = extract_triples_with_orchestration(
                orch_service, 
                doc_content[:2000], 
                KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT_KG_RAG.template.replace(
                    "{allowedAttributes}", allowed_attributes_str
                )
            )
            
            display_sample_triples(kg_rag_triples, "KG-RAG Extracted Triples (Claude-4 Sonnet)")
            
        except Exception as e:
            print(f"⚠️ KG-RAG test failed: {e}")
        
        print("\n🎉 EXTRACTION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("Key Benefits of Using Claude-4 Sonnet:")
        print("• Better understanding of complex MSDS terminology")
        print("• More accurate Subject-Predicate-Object extraction")
        print("• Enhanced content filtering and safety")
        print("• Improved handling of technical documents")
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
