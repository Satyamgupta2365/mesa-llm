"""
Simple Conversation Model for Mesa-LLM

This is a beginner-friendly example showing how to create LLM-powered agents
that interact with each other using the ReAct reasoning framework.
"""

from mesa import Model
"""
Simple in-file scheduler to avoid relying on `mesa.time.RandomActivation`,
which may not be available in all installed Mesa versions. This scheduler
implements the small subset used by the example: `add()` and `step()` and
exposes the `agents` list used by `DataCollector`.
"""


class SimpleScheduler:
    def __init__(self, model):
        self.model = model
        self.agents = []

    def add(self, agent):
        self.agents.append(agent)

    def step(self):
        # iterate over a copy so agents can modify schedule safely
        for agent in list(self.agents):
            agent.step()
from mesa.datacollection import DataCollector
from mesa_llm.llm_agent import LLMAgent
from mesa_llm.reasoning.react import ReActReasoning as ReAct


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
            internal_state=[personality],  # Store personality as internal state
        )
        self.personality = personality
        self.messages_sent = 0

    def step(self):
        """Execute one step of the agent."""
        # For this simple example we don't rely on spatial observations;
        # pass None to reasoning.plan so the agent will use its system/step prompts.
        observation = None

        # Create a prompt for the agent
        prompt = (
            "You are participating in a casual conversation. "
            "If there are other agents nearby, try to engage in conversation. "
            "Use the speak_to tool to communicate with them. "
            "Be natural and stay true to your personality."
        )

        # Use ReAct reasoning to generate a plan
        plan = self.reasoning.plan(
            prompt=prompt, obs=observation, selected_tools=["speak_to"]
        )

        # Apply the plan (execute the tools)
        self.apply_plan(plan)
        self.messages_sent += 1

    async def astep(self):
        """Async version of step for parallel execution."""
        observation = None

        prompt = (
            "You are participating in a casual conversation. "
            "If there are other agents nearby, try to engage in conversation. "
            "Use the speak_to tool to communicate with them. "
            "Be natural and stay true to your personality."
        )

        plan = await self.reasoning.aplan(
            prompt=prompt, obs=observation, selected_tools=["speak_to"]
        )

        self.apply_plan(plan)
        self.messages_sent += 1


class ConversationModel(Model):
    """A model where agents converse with each other using ReAct reasoning."""

    def __init__(self, n_agents: int = 3, llm_model: str = "openai/gpt-4o-mini", seed: int = None):
        """
        Initialize the conversation model.

        Args:
            n_agents: Number of agents to create
            llm_model: LLM model in format 'provider/model_name'
            seed: Random seed for reproducibility
        """
        super().__init__(seed=seed)
        self.num_agents = n_agents
        self.schedule = SimpleScheduler(self)
        self.llm_model = llm_model

        # Define personalities for agents
        personalities = [
            "friendly and outgoing, always eager to help others",
            "thoughtful and philosophical, likes to reflect deeply",
            "witty and humorous, enjoys making jokes",
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
                system_prompt=system_prompt,
            )
            self.schedule.add(agent)

        # Set up data collection
        self.datacollector = DataCollector(
            model_reporters={"Total Messages": self._count_total_messages},
            agent_reporters={"Messages Sent": "messages_sent"},
        )

    def _count_total_messages(self):
        """Count total messages sent by all agents."""
        return sum(agent.messages_sent for agent in self.schedule.agents)

    def step(self):
        """Execute one step of the model."""
        self.schedule.step()
        self.datacollector.collect(self)
