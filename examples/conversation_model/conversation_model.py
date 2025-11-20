"""
Simple Mesa-LLM Conversation Model
A beginner-friendly example showing how to create LLM-powered agents that interact.

This model demonstrates:
- Creating LLM-powered agents with different personalities
- Agent-to-agent communication
- Basic conversation flow
- Data collection

Usage:
    python conversation_model.py

Make sure to set your API key first:
    export OPENAI_API_KEY="your-key-here"
    # or for Anthropic: export ANTHROPIC_API_KEY="your-key-here"
"""

import os
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

# For this example, you'll need to install mesa-llm
# pip install mesa-llm

try:
    from mesa_llm.llm import OpenAILLM
    # Alternative imports if you want to use different providers:
    # from mesa_llm.llm import AnthropicLLM
    # from mesa_llm.llm import OllamaLLM
except ImportError:
    print("Error: mesa-llm not installed. Please run: pip install mesa-llm")
    exit(1)


class ConversationAgent(Agent):
    """
    An agent that uses an LLM to generate conversational responses.
    
    Attributes:
        unique_id: Unique identifier for the agent
        model: The model this agent belongs to
        personality: A description of the agent's personality
        conversation_history: List of messages this agent has sent
        llm: The language model used for generating responses
    """
    
    def __init__(self, unique_id, model, personality, llm_provider="openai"):
        """
        Initialize a conversation agent.
        
        Args:
            unique_id: Unique identifier for the agent
            model: The Mesa model this agent belongs to
            personality: String describing the agent's personality
            llm_provider: Which LLM provider to use (openai, anthropic, ollama)
        """
        super().__init__(unique_id, model)
        self.personality = personality
        self.conversation_history = []
        
        # Initialize the appropriate LLM
        if llm_provider.lower() == "openai":
            self.llm = OpenAILLM(
                model_name="gpt-3.5-turbo",  # Using cheaper model for tutorial
                temperature=0.7
            )
        # Add more providers as needed
        else:
            raise ValueError(f"Unknown LLM provider: {llm_provider}")
    
    def generate_greeting(self):
        """
        Generate an initial greeting based on the agent's personality.
        
        Returns:
            str: The generated greeting message
        """
        prompt = f"""You are a person with the following personality: {self.personality}

Generate a short, casual greeting or opening statement (1-2 sentences).
Just respond with the greeting, nothing else."""
        
        try:
            response = self.llm.generate(prompt)
            self.conversation_history.append({
                "speaker": f"Agent {self.unique_id}",
                "message": response,
                "step": self.model.schedule.steps
            })
            return response
        except Exception as e:
            return f"[Error generating greeting: {e}]"
    
    def respond_to(self, message, speaker_id):
        """
        Generate a response to another agent's message.
        
        Args:
            message: The message to respond to
            speaker_id: ID of the agent who sent the message
            
        Returns:
            str: The generated response
        """
        prompt = f"""You are a person with the following personality: {self.personality}

Someone just said to you: "{message}"

Respond naturally in 1-2 sentences. Be conversational and stay in character.
Just respond with your reply, nothing else."""
        
        try:
            response = self.llm.generate(prompt)
            self.conversation_history.append({
                "speaker": f"Agent {self.unique_id}",
                "responding_to": speaker_id,
                "message": response,
                "step": self.model.schedule.steps
            })
            return response
        except Exception as e:
            return f"[Error generating response: {e}]"
    
    def step(self):
        """
        Execute one step of agent behavior.
        Called by the scheduler at each time step.
        """
        # First step: introduce yourself
        if self.model.schedule.steps == 1:
            greeting = self.generate_greeting()
            print(f"  Agent {self.unique_id}: {greeting}")
        
        # Subsequent steps: respond to others
        else:
            # Get all other agents
            other_agents = [a for a in self.model.schedule.agents if a != self]
            
            if other_agents:
                # Pick a random agent who has spoken
                agents_with_messages = [a for a in other_agents 
                                       if len(a.conversation_history) > 0]
                
                if agents_with_messages:
                    # Choose a random agent to respond to
                    target = self.random.choice(agents_with_messages)
                    last_message = target.conversation_history[-1]["message"]
                    
                    # Generate and print response
                    response = self.respond_to(last_message, target.unique_id)
                    print(f"  Agent {self.unique_id} → Agent {target.unique_id}: {response}")


class ConversationModel(Model):
    """
    A model where agents converse with each other using LLMs.
    
    This model demonstrates basic mesa-llm functionality with:
    - Multiple agents with different personalities
    - LLM-powered conversation generation
    - Random activation scheduling
    - Data collection
    """
    
    def __init__(self, n_agents=3, personalities=None, llm_provider="openai"):
        """
        Initialize the conversation model.
        
        Args:
            n_agents: Number of agents to create
            personalities: List of personality descriptions (optional)
            llm_provider: Which LLM provider to use
        """
        super().__init__()
        self.num_agents = n_agents
        self.schedule = RandomActivation(self)
        
        # Default personalities if none provided
        if personalities is None:
            personalities = [
                "friendly and outgoing",
                "shy and thoughtful",
                "humorous and witty",
                "intellectual and curious",
                "energetic and enthusiastic"
            ]
        
        # Create agents with assigned personalities
        for i in range(self.num_agents):
            personality = personalities[i % len(personalities)]
            agent = ConversationAgent(i, self, personality, llm_provider)
            self.schedule.add(agent)
        
        # Set up data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Total Messages": lambda m: sum(len(a.conversation_history) 
                                               for a in m.schedule.agents),
                "Step": lambda m: m.schedule.steps
            },
            agent_reporters={
                "Messages Sent": lambda a: len(a.conversation_history),
                "Personality": lambda a: a.personality
            }
        )
    
    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
        self.datacollector.collect(self)


def main():
    """
    Main function to run the conversation model.
    """
    # Check for API key
    if "OPENAI_API_KEY" not in os.environ:
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        print("\nAlternatively, you can use Ollama (local, free):")
        print("1. Install Ollama: https://ollama.com")
        print("2. Run: ollama pull llama2")
        print("3. Change llm_provider='ollama' in the code")
        return
    
    print("=" * 60)
    print("Mesa-LLM Conversation Model Tutorial")
    print("=" * 60)
    
    # Create the model with 3 agents and distinct personalities
    personalities = [
        "enthusiastic and energetic, loves to share ideas",
        "calm and philosophical, often contemplates deeper meaning",
        "sarcastic but kind-hearted, uses humor to connect"
    ]
    
    model = ConversationModel(
        n_agents=3,
        personalities=personalities,
        llm_provider="openai"
    )
    
    print(f"\nCreated {model.num_agents} agents with the following personalities:")
    for agent in model.schedule.agents:
        print(f"  - Agent {agent.unique_id}: {agent.personality}")
    
    # Run the simulation
    print("\n" + "=" * 60)
    print("Starting Conversation Simulation")
    print("=" * 60 + "\n")
    
    num_steps = 5
    for i in range(num_steps):
        print(f"--- Round {i+1}/{num_steps} ---")
        model.step()
        print()
    
    # Display results
    print("=" * 60)
    print("Simulation Complete - Summary Statistics")
    print("=" * 60)
    
    # Get collected data
    model_data = model.datacollector.get_model_vars_dataframe()
    agent_data = model.datacollector.get_agent_vars_dataframe()
    
    print(f"\nTotal messages exchanged: {model_data['Total Messages'].iloc[-1]}")
    print("\nMessages per agent:")
    for agent in model.schedule.agents:
        count = len(agent.conversation_history)
        print(f"  Agent {agent.unique_id}: {count} messages")
    
    # Optional: Print full conversation history
    print("\n" + "=" * 60)
    print("Full Conversation History")
    print("=" * 60 + "\n")
    
    all_messages = []
    for agent in model.schedule.agents:
        all_messages.extend(agent.conversation_history)
    
    # Sort by step
    all_messages.sort(key=lambda x: x.get('step', 0))
    
    for msg in all_messages:
        speaker = msg['speaker']
        text = msg['message']
        if 'responding_to' in msg:
            print(f"{speaker} → Agent {msg['responding_to']}: {text}")
        else:
            print(f"{speaker}: {text}")
    
    print("\n" + "=" * 60)
    print("Tutorial Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("- Try modifying agent personalities")
    print("- Add more agents")
    print("- Implement conversation topics or goals")
    print("- Add spatial elements (grid placement)")
    print("- Create custom visualizations")


if __name__ == "__main__":
    main()