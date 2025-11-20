# Simple Mesa-LLM Tutorial: Building Your First LLM-Powered Agent Model

## Introduction

This tutorial will guide you through creating your first agent-based model using Mesa-LLM. We'll build a simple **Conversation Model** where LLM-powered agents with different personalities interact with each other using the ReAct reasoning framework.

## Prerequisites

- Python 3.11 or higher
- Basic understanding of Python programming and Mesa framework
- An API key for at least one supported LLM provider (OpenAI, Anthropic, Google, xAI, etc.)

## Installation

First, install mesa-llm:

```bash
pip install mesa-llm
```

For development or latest features:

```bash
pip install -U --pre mesa-llm
```

You'll also need the `python-dotenv` package to manage API keys:

```bash
pip install python-dotenv
```

## Setting Up Your API Keys

1. **Create a `.env` file** in your project root directory:

```bash
# .env file
OPENAI_API_KEY=your-openai-key-here
# OR use any other supported provider:
# ANTHROPIC_API_KEY=your-anthropic-key-here
# GOOGLE_API_KEY=your-google-key-here
```

2. **Load the API key in your Python code:**

```python
from dotenv import load_dotenv
load_dotenv()  # This loads your .env file
```

## What We'll Build

We'll create a simple social interaction model where:
- Multiple agents with different personalities interact using LLMs
- Agents use the ReAct (Reasoning + Acting) framework to think before speaking
- Agents maintain short-term and long-term memory of interactions
- We'll collect data on agent interactions

## Step 1: Understanding LLMAgent

Before we build our model, let's understand the key components:

- **LLMAgent**: The base class for LLM-powered agents in Mesa-LLM
- **Reasoning**: The decision-making framework (we'll use ReAct)
- **Memory**: Agents automatically get STLTMemory (Short-Term/Long-Term Memory)
- **ToolManager**: Manages tools that agents can use (we'll use `speak_to` tool)

## Step 2: Create the Conversation Model File

Create a new file called `conversation_model.py`:

```python
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa_llm.llm_agent import LLMAgent
from mesa_llm.reasoning.react import ReAct


class ConversationAgent(LLMAgent):
    """An agent that can converse with other agents using LLMs and ReAct reasoning."""
    
    def __init__(self, model, reasoning, llm_model, personality, system_prompt):
        """
        Initialize a conversation agent.
        
        Args:
            model: The Mesa model instance
            reasoning: The reasoning framework (ReAct)
            llm_model: The LLM model in format 'provider/model_name'
            personality: A description of the agent's personality
            system_prompt: The system prompt for the agent
        """
        super().__init__(
            model=model,
            reasoning=reasoning,
            llm_model=llm_model,
            system_prompt=system_prompt,
            internal_state=[personality]  # Store personality as internal state
        )
        self.personality = personality
        self.messages_sent = 0


class ConversationModel(Model):
    """A model where agents converse with each other using ReAct reasoning."""
    
    def __init__(
        self,
        n_agents: int = 3,
        llm_model: str = "openai/gpt-4o-mini",
        seed: int = None
    ):
        """
        Initialize the conversation model.
        
        Args:
            n_agents: Number of agents to create
            llm_model: LLM model in format 'provider/model_name'
            seed: Random seed for reproducibility
        """
        super().__init__(seed=seed)
        self.num_agents = n_agents
        self.schedule = RandomActivation(self)
        self.llm_model = llm_model
        
        # Define personalities for agents
        personalities = [
            "friendly and outgoing, always eager to help others",
            "thoughtful and philosophical, likes to reflect deeply",
            "witty and humorous, enjoys making jokes"
        ]
        
        # Create agents
        for i in range(self.num_agents):
            personality = personalities[i % len(personalities)]
            
            # System prompt tells the agent their role and personality
            system_prompt = (
                f"You are Agent {i} with the following personality: {personality}. "
                f"You are participating in a casual conversation. Be natural and conversational. "
                f"Use the speak_to tool to communicate with other agents."
            )
            
            agent = ConversationAgent(
                model=self,
                reasoning=ReAct,  # Using ReAct reasoning framework
                llm_model=llm_model,
                personality=personality,
                system_prompt=system_prompt
            )
            self.schedule.add(agent)
        
        # Set up data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Total Messages": self._count_total_messages
            },
            agent_reporters={
                "Messages Sent": "messages_sent"
            }
        )
    
    def _count_total_messages(self):
        """Count total messages sent by all agents."""
        return sum(agent.messages_sent for agent in self.schedule.agents)
    
    def step(self):
        """Execute one step of the model."""
        self.schedule.step()
        self.datacollector.collect(self)
```

## Step 3: Create a Script to Run the Model

Create a file called `run_conversation.py`:

```python
from dotenv import load_dotenv
from conversation_model import ConversationModel

# Load API keys from .env file
load_dotenv()

def main():
    """Run the conversation model."""
    
    # Create the model with 3 agents
    # Available models: 'openai/gpt-4o', 'anthropic/claude-3-sonnet', etc.
    model = ConversationModel(
        n_agents=3,
        llm_model="openai/gpt-4o-mini"  # Change this to your preferred model
    )
    
    # Run for 3 steps
    print("=== Starting Conversation Simulation ===\n")
    
    for step_num in range(3):
        print(f"\n--- Step {step_num + 1} ---")
        model.step()
    
    print("\n=== Simulation Complete ===\n")
    
    # Print collected data
    print("Data Collection Results:")
    model_data = model.datacollector.get_model_vars_dataframe()
    print("\nModel Data:")
    print(model_data)
    
    agent_data = model.datacollector.get_agent_vars_dataframe()
    print("\nAgent Data:")
    print(agent_data)


if __name__ == "__main__":
    main()
```

## Step 4: Using Different LLM Providers

Mesa-LLM uses litellm to support multiple providers. You can use any of these models by specifying them in the format `provider/model_name`:

### OpenAI Models
```python
llm_model = "openai/gpt-4o"
llm_model = "openai/gpt-4o-mini"  # Cheaper option
llm_model = "openai/gpt-3.5-turbo"
```

Set your API key in `.env`:
```
OPENAI_API_KEY=your-key-here
```

### Anthropic (Claude)
```python
llm_model = "anthropic/claude-3-sonnet-20240229"
llm_model = "anthropic/claude-3-haiku-20240307"
```

Set your API key in `.env`:
```
ANTHROPIC_API_KEY=your-key-here
```

### Google Gemini
```python
llm_model = "gemini/gemini-2.0-flash"
llm_model = "gemini/gemini-1.5-pro"
```

Set your API key in `.env`:
```
GOOGLE_API_KEY=your-key-here
```

### Local Models with Ollama

For free local models, install Ollama and run:

```bash
# Install from https://ollama.ai
# Then pull a model
ollama pull llama2
ollama pull mistral

# Use in your code
llm_model = "ollama/llama2"
```

## Step 5: Understanding Key Components

### ReAct Framework
The ReAct (Reasoning + Acting) framework makes agents think through their decisions before acting:
- **Reasoning**: The agent thinks about what to do
- **Acting**: The agent then uses tools to execute the plan

### Memory
Agents automatically get STLTMemory (Short-Term/Long-Term Memory) which:
- Stores recent interactions in short-term memory
- Consolidates old memories into long-term summaries
- Prevents context length exceeded errors

### Tools
Agents can use tools like `speak_to` to communicate with others. Tools are automatically registered.

## Step 6: Running Your Model

1. **Set up your environment:**
```bash
pip install mesa-llm python-dotenv
```

2. **Create your `.env` file** with API keys

3. **Run the model:**
```bash
python run_conversation.py
```

## Adding More Advanced Features

### Example: Custom Tools

You can add custom tools for agents to use:

```python
from mesa_llm.tools.tool_decorator import tool

@tool
def share_opinion(agent, opinion: str) -> str:
    """Share an opinion with other agents."""
    return f"Agent {agent.unique_id} shares: {opinion}"

# Register the tool in your agent's step method
agent.tool_manager.register_tool(share_opinion)
```

### Example: Spatial Interactions

To add spatial interactions, use Mesa's grid:

```python
from mesa.space import MultiGrid

class SpatialConversationModel(ConversationModel):
    def __init__(self, n_agents=3, llm_model="openai/gpt-4o-mini"):
        super().__init__(n_agents, llm_model)
        self.grid = MultiGrid(width=10, height=10, torus=False)
        
        # Place agents randomly on the grid
        for agent in self.schedule.agents:
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))
```

## Next Steps

Now that you've built your first mesa-llm model, you can:

1. **Explore Other Reasoning Frameworks**: Try Chain-of-Thought (CoT), ReWOO, or other reasoning methods
2. **Add Spatial Elements**: Place agents on a grid and have them interact with neighbors
3. **Implement Custom Tools**: Create domain-specific tools for your agents
4. **Complex Negotiations**: Build multi-step negotiation scenarios like the negotiation example
5. **Visualization**: Create interactive visualizations with Solara (see negotiation example's app.py)

## Reference Models

Check out the example models in the mesa-llm repository:

- **Negotiation Model** (`examples/negotiation/`): A complete example with buyer and seller agents
- **Epstein Civil Violence Model** (`examples/epstein_civil_violence/`): A complex agent-based model

## Summary

In this tutorial, you learned:
- How to install and set up Mesa-LLM
- How to create LLM-powered agents using the LLMAgent class
- How to use the ReAct reasoning framework
- How to build a simple model with agent interactions
- How to collect and analyze data from your simulations
- How to use different LLM providers

Mesa-LLM handles complexity for you:
- **Memory Management**: Agents automatically maintain short-term and long-term memory
- **Rate Limiting**: The library includes built-in retry logic via tenacity
- **Context Management**: STLTMemory prevents context length exceeded errors
- **Tool Management**: Tools are automatically managed and callable by agents

## Troubleshooting

**Issue: "API key not found"**
- Make sure your `.env` file exists and has the correct key name
- Verify you've called `load_dotenv()` before creating the model

**Issue: "Module not found: mesa_llm"**
- Reinstall with: `pip install -U mesa-llm`

**Issue: Slow responses**
- Try using cheaper/faster models like `gpt-4o-mini` or `claude-3-haiku`
- Use local models with Ollama for free

## Resources

- [Mesa Documentation](https://mesa.readthedocs.io/)
- [Mesa-LLM GitHub Repository](https://github.com/projectmesa/mesa-llm)
- [Mesa-LLM API Documentation](https://mesa-llm.readthedocs.io/)
- [Negotiation Example Model](https://github.com/projectmesa/mesa-llm/tree/main/examples/negotiation)
- [Join the Mesa Matrix Chat](https://matrix.to/#/#mesa-llm:matrix.org)

## Contributing

Found a bug or have a suggestion? Please file an issue on the [GitHub repository](https://github.com/projectmesa/mesa-llm/issues)!

---

**Tutorial created for Issue #32 - "Make a simple mesa-llm tutorial"**
**Fixed based on PR #34 feedback to use correct API and tested implementations**
