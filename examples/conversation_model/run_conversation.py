"""
Run the Conversation Model

This script demonstrates how to run the simple conversation model
with real LLM providers. Make sure you have valid API keys configured.

Setup:
1. Create a .env file in this directory with your API keys:
   OPENAI_API_KEY=sk-...
   or for other providers:
   ANTHROPIC_API_KEY=...
   GOOGLE_API_KEY=...

2. Run this script:
   python run_conversation.py
"""

from dotenv import load_dotenv
from conversation_model import ConversationModel

# Load environment variables from .env file
load_dotenv()


def main():
    """Run the conversation model with real LLM providers."""
    print("Initializing Conversation Model...")
    print("Make sure your API keys are set in the .env file.\n")
    
    # Create model with your LLM provider/model
    # Examples:
    # - "openai/gpt-4o-mini"
    # - "anthropic/claude-3-5-sonnet-20241022"
    # - "google/gemini-2.0-flash"
    model = ConversationModel(n_agents=3, llm_model="openai/gpt-4o-mini")

    # Run simulation
    steps = 3
    print("=== Starting Conversation Simulation ===\n")
    for step_num in range(steps):
        print(f"\n--- Step {step_num + 1} ---")
        model.step()

    print("\n=== Simulation Complete ===\n")

    # Display collected data
    print("Data Collection Results:")
    model_data = model.datacollector.get_model_vars_dataframe()
    print("\nModel Data:")
    print(model_data)

    agent_data = model.datacollector.get_agent_vars_dataframe()
    print("\nAgent Data:")
    print(agent_data)


if __name__ == "__main__":
    main()
