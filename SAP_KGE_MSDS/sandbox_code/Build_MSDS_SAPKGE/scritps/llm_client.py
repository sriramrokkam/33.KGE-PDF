"""
llm_client.py

This module provides classes to interact with AI services for foundation models and orchestration models.
"""


### Initialization of Foundation Model Client
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.proxy import GenAIHubProxyClient
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import UserMessage
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.models.azure_content_filter import AzureContentFilter 
from gen_ai_hub.orchestration.service import OrchestrationService

import logging

logger = logging.getLogger(__name__)


class CL_Foundation_Service:
    def __init__(self, config):
        self.config = config
        self.aic_client_id = config.get("aic_client_id")
        self.aic_client_secret = config.get("aic_client_secret")
        self.aic_resource_group = config.get("aic_resource_group")
        self.aic_base_url = config.get("aic_base_url")

    def invoke_llm(self, prompt, model_name=None, temperature=None):
        # Use config values if not provided

        proxy_client = get_proxy_client(
            base_url=self.aic_base_url,
            client_id=self.aic_client_id,
            client_secret=self.aic_client_secret,
            resource_group=self.aic_resource_group
        )

        llm = ChatOpenAI(
            temperature=temperature,
            proxy_model_name=model_name,
            proxy_client=proxy_client
        )

        try:
            response = llm.invoke(prompt)
            return response.content
        except ValueError as ve:
            logger.error(f"ValueError during LLM invocation: {ve}", exc_info=True)
            raise Exception("LLM deployment not found or misconfigured. Check model_name and deployment settings.")
        except Exception as e:
            logger.error(f"Error during LLM invocation: {e}", exc_info=True)
            raise Exception("Error during LLM invocation.")






### Initialization of Orchestration Model Client
class CL_Orchestration_Service:
    def __init__(self, aic_config, orch_model_params):
        """Initialize the orchestration service with configuration and model parameters."""
        self.aic_auth_url = aic_config["aic_auth_url"]
        self.aic_client_id = aic_config["aic_client_id"]
        self.aic_client_secret = aic_config["aic_client_secret"]
        self.aic_resource_group = aic_config["aic_resource_group"]
        self.orch_service_url = orch_model_params["orch_url"]
        self.orch_model = orch_model_params["orch_model"]
        self.model_parameters = orch_model_params["parameters"]
        self.content_filter = AzureContentFilter(hate=6, sexual=4, self_harm=0, violence=4)

    def get_orch_llm_client(self):
        """Initialize and return the orchestration client."""
        proxy_client = GenAIHubProxyClient(
            base_url=self.orch_service_url,
            auth_url=self.aic_auth_url,
            client_id=self.aic_client_id,
            client_secret=self.aic_client_secret,
            resource_group=self.aic_resource_group
        )
        orch_client = OrchestrationService(api_url=self.orch_service_url, proxy_client=proxy_client)
        return orch_client

    def run_orchestration(self, prompt,error_context="orchestration"):
        """Run orchestration service with content filtering."""
        try:
            # Use passed orch_model_params if provided, else use self
            model_name = self.orch_model
            parameters = self.model_parameters
    
            model_config = LLM(
                name=model_name,
                parameters=parameters
            )
            template = Template(messages=[UserMessage("{{ ?extraction_prompt }}")])
            config = OrchestrationConfig(template=template, llm=model_config)
            config.input_filter = self.content_filter
            config.output_filter = self.content_filter
            orch_client = self.get_orch_llm_client()
            
            # Support both string and dict prompt
            if isinstance(prompt, dict) and "messages" in prompt:
                user_message = prompt["messages"][0]["content"]
            else:
                user_message = str(prompt)

            response = orch_client.run(
                config=config,
                template_values=[TemplateValue("extraction_prompt", user_message)]
            )
            # Extract and return the result
            try:
                result = response.orchestration_result.choices[0].message.content
                return result
            except Exception:
                logger.error(f"Unexpected response format: {response}", exc_info=True)
                raise Exception("Unexpected response format from orchestration result")
        except KeyError as e:
            logger.error(f"Missing key in model_params: {str(e)}", exc_info=True)
            raise Exception(f"Missing key in model_params: {str(e)}")
        except Exception as e:
            logger.error(f"Error in {error_context}: {str(e)}", exc_info=True)
            raise Exception(f"Error in {error_context}: {str(e)}")