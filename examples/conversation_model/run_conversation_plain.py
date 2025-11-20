"""
Plain-text version of the Conversation Model runner.

This script runs the conversation model with real LLM providers.
Plain-text output (no rich formatting) makes it ideal for logs and terminals.

Setup:
1. Create a .env file with your API keys:
   OPENAI_API_KEY=sk-...

2. Run this script:
   python run_conversation_plain.py
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add mesa_llm to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables
load_dotenv()

from conversation_model import ConversationModel


def main():
    print("Initializing Conversation Model...")
    print("Make sure your API keys are set in the .env file.\n")
    print("=" * 70)
    print("Starting Conversation Simulation")
    print("=" * 70)
    print()

    model = ConversationModel(n_agents=3, llm_model="openai/gpt-4o-mini")

    for step in range(1, 4):
        print(f"\n--- Step {step} ---\n")
        model.step()

    print("\n" + "=" * 70)
    print("Simulation Complete")
    print("=" * 70)
    print()

    # Collect and display data
    print("Data Collection Results:\n")
    
    model_data = model.datacollector.get_model_vars_dataframe()
    print("Model Data:")
    print(model_data)
    print()

    agent_data = model.datacollector.get_agent_vars_dataframe()
    print("Agent Data:")
    print(agent_data)


if __name__ == "__main__":
    main()
