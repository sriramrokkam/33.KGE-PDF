"""
test_llm_clients.py

Example script demonstrating how to use the CL_Foundation_Service and CL_Orchestration_Service classes.
"""

import os
from dotenv import load_dotenv
from llm_client import CL_Foundation_Service, CL_Orchestration_Service

# Load environment variables
load_dotenv()

def test_foundation_service():
    """Test the Foundation Service with different models and parameters."""
    print("=" * 60)
    print("TESTING FOUNDATION SERVICE")
    print("=" * 60)
    
    # Configuration for Foundation Service
    aic_config = {
        "aic_client_id": os.getenv("AICORE_CLIENT_ID"),
        "aic_client_secret": os.getenv("AICORE_CLIENT_SECRET"),
        "aic_base_url": os.getenv("AICORE_BASE_URL"),
        "aic_resource_group": os.getenv("AICORE_RESOURCE_GROUP", "default"),
        "default_model": "gpt-4.1",  # Set your default model
        "default_temperature": 0.7
    }
    
    # Initialize Foundation Service
    foundation_service = CL_Foundation_Service(aic_config)
    
    # Test 1: Simple invocation with default settings
    print("\n1. Testing with default settings:")
    try:
        prompt = "What is the capital of France?"
        response = foundation_service.invoke_llm(prompt)
        print(f"Prompt: {prompt}")
        print(f"Response: {response[:100]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Using different model and temperature
    print("\n2. Testing with custom model and temperature:")
    try:
        prompt = "Explain photosynthesis in one sentence."
        response = foundation_service.invoke_llm(
            prompt=prompt,
            model_name="gpt-4.1",  # Specify model
            temperature=0.3  # Lower temperature for more focused response
        )
        print(f"Prompt: {prompt}")
        print(f"Response: {response[:100]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Get LLM client directly for more control
    print("\n3. Testing direct LLM client usage:")
    try:
        llm_client = foundation_service.get_llm_client(
            model_name="gpt-4.1",
            temperature=0.5
        )
        prompt = "List 3 benefits of renewable energy."
        response = llm_client.invoke(prompt)
        print(f"Prompt: {prompt}")
        print(f"Response: {response.content[:100]}...")
    except Exception as e:
        print(f"Error: {e}")


def test_orchestration_service():
    """Test the Orchestration Service with different models and parameters."""
    print("\n" + "=" * 60)
    print("TESTING ORCHESTRATION SERVICE")
    print("=" * 60)
    
    # Configuration for AI Core
    aic_config = {
        "aic_auth_url": os.getenv("AICORE_AUTH_URL"),
        "aic_client_id": os.getenv("AICORE_CLIENT_ID"),
        "aic_client_secret": os.getenv("AICORE_CLIENT_SECRET"),
        "aic_resource_group": os.getenv("AICORE_RESOURCE_GROUP", "default")
    }
    
    # Default orchestration parameters
    default_orch_params = {
        "orch_url": "https://api.ai.prod.us-east-1.aws.ml.hana.ondemand.com/v2/inference/deployments/ddaae0b631e78184",
        "orch_model": "anthropic--claude-3-sonnet",
        "parameters": {
            "temperature": 0.5,
            "max_tokens": 20000,
            "top_p": 0.9
        }
    }
    
    # Initialize Orchestration Service
    orch_service = CL_Orchestration_Service(aic_config, default_orch_params)
    
    # Test 1: Simple invocation with default settings
    print("\n1. Testing with default orchestration settings:")
    try:
        prompt = "What are the main components of a safety data sheet?"
        response = orch_service.invoke_llm(prompt)
        print(f"Prompt: {prompt}")
        print(f"Response: {response[:150]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Using different model and parameters
    print("\n2. Testing with custom model and parameters:")
    try:
        prompt = "Explain the importance of chemical hazard classification."
        response = orch_service.invoke_llm(
            prompt=prompt,
            model_name="anthropic--claude-3-sonnet",
            temperature=0.3,
            max_tokens=500
        )
        print(f"Prompt: {prompt}")
        print(f"Response: {response[:150]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Using run_orchestration method directly
    print("\n3. Testing direct orchestration method:")
    try:
        prompt = "What is the purpose of GHS classification?"
        custom_parameters = {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 0.8
        }
        response = orch_service.run_orchestration(
            prompt=prompt,
            model_name="anthropic--claude-3-sonnet",
            parameters=custom_parameters
        )
        print(f"Prompt: {prompt}")
        print(f"Response: {response[:150]}...")
    except Exception as e:
        print(f"Error: {e}")


def test_msds_knowledge_extraction():
    """Test both services with MSDS-specific prompts."""
    print("\n" + "=" * 60)
    print("TESTING MSDS KNOWLEDGE EXTRACTION")
    print("=" * 60)
    
    # Sample MSDS text
    msds_text = """
    WD-40 Multi-Use Product Aerosol is manufactured by WD-40 Company.
    It contains LVP Aliphatic Hydrocarbon (CAS# 64742-47-8) with 45-50% weight.
    The product is classified as Aspiration Toxicity Category 1.
    Flash point: >60°C (>140°F). Boiling point: 149-204°C (300-400°F).
    """
    
    # Test with Foundation Service
    print("\n1. Testing Foundation Service with MSDS extraction:")
    try:
        aic_config = {
            "aic_client_id": os.getenv("AICORE_CLIENT_ID"),
            "aic_client_secret": os.getenv("AICORE_CLIENT_SECRET"),
            "aic_base_url": os.getenv("AICORE_BASE_URL"),
            "aic_resource_group": os.getenv("AICORE_RESOURCE_GROUP", "default"),
            "default_model": "gpt-4.1"
        }
        
        foundation_service = CL_Foundation_Service(aic_config)
        
        extraction_prompt = f"""
        Extract key information from this MSDS text in the format (Subject, Predicate, Object):
        
        {msds_text}
        
        Focus on chemical composition, hazard classification, and physical properties.
        """
        
        response = foundation_service.invoke_llm(
            prompt=extraction_prompt,
            temperature=0.3
        )
        print(f"Foundation Service Response:\n{response}")
        
    except Exception as e:
        print(f"Foundation Service Error: {e}")
    
    # Test with Orchestration Service
    print("\n2. Testing Orchestration Service with MSDS extraction:")
    try:
        aic_config = {
            "aic_auth_url": os.getenv("AICORE_AUTH_URL"),
            "aic_client_id": os.getenv("AICORE_CLIENT_ID"),
            "aic_client_secret": os.getenv("AICORE_CLIENT_SECRET"),
            "aic_resource_group": os.getenv("AICORE_RESOURCE_GROUP", "default")
        }
        
        default_orch_params = {
            "orch_url": "https://api.ai.prod.us-east-1.aws.ml.hana.ondemand.com/v2/inference/deployments/ddaae0b631e78184",
            "orch_model": "anthropic--claude-3-sonnet"
        }
        
        orch_service = CL_Orchestration_Service(aic_config, default_orch_params)
        
        response = orch_service.invoke_llm(
            prompt=extraction_prompt,
            temperature=0.3,
            max_tokens=1000
        )
        print(f"Orchestration Service Response:\n{response}")
        
    except Exception as e:
        print(f"Orchestration Service Error: {e}")


def main():
    """Main function to run all tests."""
    print("LLM CLIENT TESTING SUITE")
    print("=" * 60)
    
    # Check if environment variables are set
    required_vars = [
        "AICORE_CLIENT_ID", "AICORE_CLIENT_SECRET", 
        "AICORE_BASE_URL", "AICORE_AUTH_URL"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Missing environment variables: {missing_vars}")
        print("Please set these in your .env file before running tests.")
        return
    
    try:
        # Run tests
        test_foundation_service()
        test_orchestration_service()
        test_msds_knowledge_extraction()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"Test suite error: {e}")


if __name__ == "__main__":
    main()
