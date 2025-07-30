"""
debug_claude_response.py

Simple script to debug what Claude-4 Sonnet is returning for triple extraction.
"""

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from prompts import KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT
from llm_client import CL_Orchestration_Service

# Load environment variables
load_dotenv()

def main():
    print("🔍 DEBUGGING CLAUDE-4 SONNET RESPONSE")
    print("=" * 60)
    
    # Setup orchestration service
    aic_config = {
        "aic_auth_url": os.getenv("AICORE_AUTH_URL"),
        "aic_client_id": os.getenv("AICORE_CLIENT_ID"),
        "aic_client_secret": os.getenv("AICORE_CLIENT_SECRET"),
        "aic_resource_group": os.getenv("AICORE_RESOURCE_GROUP", "default")
    }
    
    orch_model_params = {
        "orch_url": "https://api.ai.prod.us-east-1.aws.ml.hana.ondemand.com/v2/inference/deployments/ddaae0b631e78184",
        "orch_model": "anthropic--claude-4-sonnet",
        "parameters": {
            "temperature": 0.3,
            "max_tokens": 20000,
            "top_p": 0.9
        }
    }
    
    orch_service = CL_Orchestration_Service(aic_config, orch_model_params)
    print("✅ Orchestration Service initialized")
    
    # Load a small sample of MSDS content for testing
    sample_text = """
    WD-40 Multi-Use Product Aerosol is manufactured by WD-40 Company.
    It contains LVP Aliphatic Hydrocarbon (CAS# 64742-47-8) with 45-50% weight.
    The product is classified as Aspiration Toxicity Category 1.
    Flash point: >60°C (>140°F). Boiling point: 149-204°C (300-400°F).
    """
    
    print(f"📝 Sample text for extraction:")
    print("-" * 40)
    print(sample_text)
    print("-" * 40)
    
    # Format the prompt
    formatted_prompt = KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT.template.format(text=sample_text)
    
    print(f"\n📏 Formatted prompt length: {len(formatted_prompt)} characters")
    print(f"\n📋 First 500 characters of prompt:")
    print("-" * 40)
    print(formatted_prompt[:500] + "...")
    print("-" * 40)
    
    try:
        print(f"\n🚀 Sending request to Claude-4 Sonnet...")
        
        # Get response from Claude-4 Sonnet
        response = orch_service.invoke_llm(
            prompt=formatted_prompt,
            model_name="anthropic--claude-4-sonnet",
            temperature=0.3,
            max_tokens=5000
        )
        
        print(f"✅ Response received!")
        print(f"📏 Response length: {len(response)} characters")
        
        print(f"\n📄 FULL RESPONSE FROM CLAUDE-4 SONNET:")
        print("=" * 80)
        print(response)
        print("=" * 80)
        
        # Now let's analyze the response line by line
        print(f"\n🔍 LINE-BY-LINE ANALYSIS:")
        print("-" * 60)
        
        lines = response.split('\n')
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if line_stripped:  # Only show non-empty lines
                print(f"Line {i:2d}: {repr(line_stripped)}")
                
                # Check if it looks like a triple
                if '(' in line_stripped and ')' in line_stripped:
                    print(f"         ^ Contains parentheses - potential triple")
                if line_stripped.count(',') >= 2:
                    print(f"         ^ Contains 2+ commas - potential triple")
        
        print(f"\n💡 PARSING SUGGESTIONS:")
        print("- Look for lines containing parentheses and commas")
        print("- Check if Claude is using a different format than expected")
        print("- Consider if the response needs different parsing logic")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
