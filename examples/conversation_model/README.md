# Simple Conversation Model

This is a beginner-friendly example of a Mesa-LLM model where agents with different personalities interact with each other using LLMs and the ReAct reasoning framework.

## Quick Start

### 1. Set Up Your Environment

First, ensure you have installed mesa-llm and python-dotenv:

```bash
pip install mesa-llm python-dotenv
```

### 2. Create a `.env` File

Create a `.env` file in this directory with your LLM API key:

```bash
# For OpenAI
OPENAI_API_KEY=your-openai-key-here

# OR for Anthropic
# ANTHROPIC_API_KEY=your-anthropic-key-here

# OR for Google Gemini
# GOOGLE_API_KEY=your-google-key-here
```

### 3. Run the Model

```bash
python run_conversation.py
```

## What This Example Shows

- **Creating LLM-powered agents**: How to extend `LLMAgent` to create custom agents
- **Using ReAct reasoning**: How agents use reasoning to plan and act
- **Tool usage**: How agents use the `speak_to` tool to communicate
- **Data collection**: How to collect and analyze agent behavior
- **Multiple LLM providers**: How to support different LLM providers

## Files

- `conversation_model.py`: The core model implementation
- `run_conversation.py`: Script to run the model
- `README.md`: This file

## Using Different LLM Providers

You can change the `llm_model` parameter in `run_conversation.py`:

```python
# OpenAI
llm_model = "openai/gpt-4o"
llm_model = "openai/gpt-4o-mini"  # Cheaper option

# Anthropic
llm_model = "anthropic/claude-3-sonnet-20240229"

# Google Gemini
llm_model = "gemini/gemini-2.0-flash"

# Local models with Ollama (free)
llm_model = "ollama/llama2"
```

## Next Steps

- Try modifying agent personalities
- Add more agents
- Implement custom tools
- Add spatial interactions using Mesa's grid system
- Check out the more complex negotiation example in `../negotiation/`

## Troubleshooting

**Issue: "API key not found"**
- Make sure your `.env` file exists in this directory
- Verify the API key name matches your provider

**Issue: "Module not found: mesa_llm"**
- Run `pip install -U mesa-llm` to ensure it's installed

**Issue: "Slow responses"**
- Try using cheaper models like `gpt-4o-mini` or `claude-3-haiku`
- Use local models with Ollama for free
