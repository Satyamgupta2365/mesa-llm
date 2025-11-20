# Simple Mesa-LLM Tutorial: Building Your First LLM-Powered Agent Model

## Introduction

This tutorial will guide you through creating your first agent-based model using Mesa-LLM. We'll build a simple **Conversation Model** where LLM-powered agents interact with each other based on their personalities.

## Prerequisites

- Python 3.8 or higher
- Basic understanding of Python programming
- An API key for one of the supported LLM providers (OpenAI, Anthropic, Ollama, etc.)

## Installation

First, install mesa-llm:

```bash
pip install mesa-llm
```

For development or latest features:

```bash
pip install -U --pre mesa-llm
```

## What We'll Build

We'll create a simple social interaction model where:
- Multiple agents with different personalities interact
- Each agent uses an LLM to generate responses
- Agents can communicate with each other
- We'll visualize the interactions

## Step 1: Setting Up the Environment

Create a new Python file called `conversation_model.py`:

```python
import os
from mesa import Model
from mesa.time import RandomActivation
from mesa_llm import LLMAgent
from mesa_llm.llm import OpenAILLM  # or your preferred LLM provider

# Set your API key (better to use environment variables)
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

## Step 2: Create the LLM-Powered Agent

```python
class ConversationAgent(LLMAgent):
    """An agent that can converse using LLMs"""
    
    def __init__(self, unique_id, model, personality):
        super().__init__(unique_id, model)
        self.personality = personality
        self.conversation_history = []
        
        # Initialize the LLM for this agent
        self.llm = OpenAILLM(
            model_name="gpt-4",
            temperature=0.7
        )
    
    def generate_greeting(self):
        """Generate an initial greeting based on personality"""
        prompt = f"""You are a person with the following personality: {self.personality}
        
Generate a short, casual greeting or opening statement (1-2 sentences).
Just respond with the greeting, nothing else."""
        
        response = self.llm.generate(prompt)
        self.conversation_history.append({
            "speaker": f"Agent {self.unique_id}",
            "message": response
        })
        return response
    
    def respond_to(self, message, speaker_id):
        """Generate a response to another agent's message"""
        prompt = f"""You are a person with the following personality: {self.personality}

Someone just said to you: "{message}"

Respond naturally in 1-2 sentences. Be conversational and stay in character.
Just respond with your reply, nothing else."""
        
        response = self.llm.generate(prompt)
        self.conversation_history.append({
            "speaker": f"Agent {self.unique_id}",
            "responding_to": speaker_id,
            "message": response
        })
        return response
    
    def step(self):
        """Called at each step of the model"""
        # If this is the first step, introduce yourself
        if self.model.schedule.steps == 1:
            greeting = self.generate_greeting()
            print(f"Agent {self.unique_id}: {greeting}")
        else:
            # Randomly choose another agent to respond to
            other_agents = [a for a in self.model.schedule.agents if a != self]
            if other_agents and len(other_agents[0].conversation_history) > 0:
                target = self.random.choice(other_agents)
                last_message = target.conversation_history[-1]["message"]
                response = self.respond_to(last_message, target.unique_id)
                print(f"Agent {self.unique_id} → Agent {target.unique_id}: {response}")
```

## Step 3: Create the Model

```python
class ConversationModel(Model):
    """A model where agents converse with each other"""
    
    def __init__(self, n_agents=3, personalities=None):
        super().__init__()
        self.num_agents = n_agents
        self.schedule = RandomActivation(self)
        
        # Default personalities if none provided
        if personalities is None:
            personalities = [
                "friendly and outgoing",
                "shy and thoughtful",
                "humorous and witty"
            ]
        
        # Create agents
        for i in range(self.num_agents):
            personality = personalities[i % len(personalities)]
            agent = ConversationAgent(i, self, personality)
            self.schedule.add(agent)
    
    def step(self):
        """Advance the model by one step"""
        self.schedule.step()
```

## Step 4: Run the Model

```python
def main():
    # Create the model with 3 agents
    model = ConversationModel(
        n_agents=3,
        personalities=[
            "enthusiastic and energetic",
            "calm and philosophical",
            "sarcastic but kind-hearted"
        ]
    )
    
    # Run for 5 steps (rounds of conversation)
    print("=== Starting Conversation Simulation ===\n")
    for i in range(5):
        print(f"\n--- Round {i+1} ---")
        model.step()
    
    print("\n=== Simulation Complete ===")

if __name__ == "__main__":
    main()
```

## Step 5: Running Your Model

Save your file and run it:

```bash
python conversation_model.py
```

You should see output like:

```
=== Starting Conversation Simulation ===

--- Round 1 ---
Agent 0: Hey there! I'm super excited to chat with everyone today!
Agent 1: Hello. It's nice to meet you all in this moment of presence.
Agent 2: Oh great, another group chat. Just what I needed today... kidding, hi everyone!

--- Round 2 ---
Agent 1 → Agent 0: Your enthusiasm is contagious. It reminds me that joy can be found in simple connections.
Agent 2 → Agent 1: Wow, that's actually pretty deep. Are you always this zen?
Agent 0 → Agent 2: Haha, I love your sense of humor! We're going to have a great time!
...
```

## Using Different LLM Providers

### Using Anthropic (Claude)

```python
from mesa_llm.llm import AnthropicLLM

self.llm = AnthropicLLM(
    model_name="claude-3-sonnet-20240229",
    temperature=0.7
)
```

### Using Ollama (Local Models)

```python
from mesa_llm.llm import OllamaLLM

self.llm = OllamaLLM(
    model_name="llama2",
    temperature=0.7
)
```

### Using Hugging Face

```python
from mesa_llm.llm import HuggingFaceLLM

self.llm = HuggingFaceLLM(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    temperature=0.7
)
```

## Next Steps

Now that you've built your first mesa-llm model, you can:

1. **Add Memory**: Implement longer conversation histories
2. **Add Spatial Elements**: Place agents in a grid and have them interact with neighbors
3. **Data Collection**: Use Mesa's DataCollector to track conversation metrics
4. **Visualization**: Create a browser-based visualization of the interactions
5. **Complex Behaviors**: Add planning, reasoning, or decision-making modules

## Advanced Example: Adding Data Collection

```python
from mesa.datacollection import DataCollector

class ConversationModel(Model):
    def __init__(self, n_agents=3, personalities=None):
        super().__init__()
        # ... previous initialization code ...
        
        # Add data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Total Messages": lambda m: sum(len(a.conversation_history) 
                                               for a in m.schedule.agents)
            },
            agent_reporters={
                "Messages Sent": lambda a: len(a.conversation_history)
            }
        )
    
    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

# After running the model:
model_data = model.datacollector.get_model_vars_dataframe()
agent_data = model.datacollector.get_agent_vars_dataframe()
print(model_data)
print(agent_data)
```

## Common Issues and Solutions

### Issue: API Rate Limits
**Solution**: Add delays between LLM calls or use batching

```python
import time

def step(self):
    time.sleep(0.5)  # Add a small delay
    # ... rest of step logic
```

### Issue: Context Length Exceeded
**Solution**: Limit conversation history

```python
def step(self):
    # Keep only last 5 messages
    if len(self.conversation_history) > 5:
        self.conversation_history = self.conversation_history[-5:]
```

### Issue: Expensive API Costs
**Solution**: Use a local model with Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2

# Use in your code
self.llm = OllamaLLM(model_name="llama2")
```

## Resources

- [Mesa Documentation](https://mesa.readthedocs.io/)
- [Mesa-LLM GitHub Repository](https://github.com/projectmesa/mesa-llm)
- [Mesa Examples](https://github.com/projectmesa/mesa-examples)
- [Join the Mesa Matrix Chat](https://matrix.to/#/#mesa-llm:matrix.org)

## Contributing

Found a bug or have a suggestion? Please file an issue on the [GitHub repository](https://github.com/projectmesa/mesa-llm/issues)!

---

**Tutorial created for Issue #32 - "Make a simple mesa-llm tutorial"**
