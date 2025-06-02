import asyncio
import logging
from typing import Optional, Dict, Any, List
import requests
from smart_sdk.tools import StdioServerParams, mcp_server_tools
from smart_sdk.agents import SMARTLLMAgent
from smart_sdk import CancellationToken, Console
from smart_sdk.model import AzureOpenAIChatCompletionClient
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
TOKEN_URL = "https://agents-hub.dev.aws.jpmchase.net/smart-runtime/v1/utility/token"
DEFAULT_USER_SID = "D649217"
MODEL_CONFIG = {
    "model": "o3-mini-2025-01-31",
    "api_version": None,  # Will be set from response
    "azure_endpoint": None,  # Will be set from response
    "azure_deployment": None  # Will be set from response
}

# MCP Server Paths
BASE_DIR = Path(__file__).parent.parent
CHASE_TRAVEL_MCP = BASE_DIR / "chase-travel-mcp" / "server" / "chase_travel_mcp_server.py"
BENEFITS_MCP = BASE_DIR / "benefits-mcp" / "server" / "benefits_mcp_server.py"
SAFEPAY_WALLET_MCP = BASE_DIR / "safepay-wallet-mcp" / "server" / "safepay_wallet_mcp_server.py"

class ModelClientError(Exception):
    """Custom exception for model client errors."""
    pass

def fetch_model_config() -> Dict[str, Any]:
    """
    Fetch model configuration from the token service.
    
    Returns:
        Dict[str, Any]: The model configuration details
        
    Raises:
        ModelClientError: If configuration fetch fails
    """
    try:
        logger.info("Fetching model configuration from token service")
        response = requests.get(TOKEN_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        error_msg = f"Failed to fetch model configuration: {str(e)}"
        logger.error(error_msg)
        raise ModelClientError(error_msg) from e

def create_model_client(model_details: Dict[str, Any]) -> AzureOpenAIChatCompletionClient:
    """
    Create an Azure OpenAI model client from configuration.
    
    Args:
        model_details: The model configuration details
        
    Returns:
        AzureOpenAIChatCompletionClient: The configured model client
    """
    logger.debug("Creating model client with retrieved configuration")
    return AzureOpenAIChatCompletionClient(
        azure_deployment=model_details["model"],
        model=MODEL_CONFIG["model"],
        api_version=model_details["api_version"],
        azure_endpoint=model_details["base_url"],
        api_key=model_details["api_key"],
        default_headers={
            "Authorization": f"Bearer {model_details['token']}", 
            "user_sid": DEFAULT_USER_SID
        }
    )

async def setup_mcp_servers() -> List[Any]:
    """
    Set up the MCP server parameters and tools for all three servers.
    
    Returns:
        List[Any]: List of configured MCP server tools
    """
    logger.info("Setting up MCP server parameters")
    
    # Configure each MCP server
    chase_travel_server = StdioServerParams(
        command="python",
        args=[str(CHASE_TRAVEL_MCP)]
    )
    
    benefits_server = StdioServerParams(
        command="python",
        args=[str(BENEFITS_MCP)]
    )
    
    safepay_wallet_server = StdioServerParams(
        command="python",
        args=[str(SAFEPAY_WALLET_MCP)]
    )
    
    logger.info("Initializing MCP server tools")
    tools = []
    for server in [chase_travel_server, benefits_server, safepay_wallet_server]:
        server_tools = await mcp_server_tools(server)
        tools.extend(server_tools)
    
    return tools

def create_agent(tools: List[Any]) -> SMARTLLMAgent:
    """
    Create a SMART LLM agent with the given tools.
    
    Args:
        tools: The MCP server tools to use
        
    Returns:
        SMARTLLMAgent: The configured agent
    """
    logger.info("Creating SMART LLM agent")
    model_details = fetch_model_config()
    model_client = create_model_client(model_details)
    
    return SMARTLLMAgent(
        name="TravelAssistant",
        description="An intelligent assistant for travel planning and payment optimization",
        system_message="""You are a helpful travel assistant specialized in helping users plan their travel and optimize their payment methods. 
        You can:
        1. Search for flights between cities
        2. Check available payment methods for users
        3. Compare card benefits and rewards
        4. Help users choose the best payment method for their travel purchases
        
        Always provide clear explanations for your recommendations and consider both the travel options and payment benefits when making suggestions.""",
        model_client=model_client,
        tools=tools,
        reflect_on_tool_use=True
    )

async def process_user_input(agent: SMARTLLMAgent, user_input: str) -> None:
    """
    Process user input and generate response using the agent.
    
    Args:
        agent: The configured agent
        user_input: The user's input text
    """
    try:
        logger.info(f"Processing user input: {user_input}")
        await Console(agent.run_stream(
            task=user_input,
            cancellation_token=CancellationToken()
        ))
    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}", exc_info=True)
        print(f"An error occurred: {str(e)}")

async def run_conversation_loop(agent: SMARTLLMAgent) -> None:
    """
    Run the main conversation loop.
    
    Args:
        agent: The configured agent
    """
    print("\nWelcome to the Travel Assistant!")
    print("I can help you plan your travel and optimize your payment methods.")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("\nExample queries:")
    print("- Search for flights from New York to London")
    print("- What payment methods do I have available?")
    print("- Which card should I use for my flight purchase?")
    print("- Compare the benefits of my cards for travel purchases")
    
    while True:
        try:
            user_input = input("\nUser: ").strip()
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                logger.info("User requested to end conversation")
                print("Ending conversation.")
                break
                
            await process_user_input(agent, user_input)
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            print("\nEnding conversation.")
            break

async def main() -> None:
    """Main entry point for the application."""
    try:
        logger.info("Starting Travel Assistant application")
        tools = await setup_mcp_servers()
        agent = create_agent(tools)
        await run_conversation_loop(agent)
                
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 