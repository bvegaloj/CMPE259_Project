# SJSU Virtual Assistant

An intelligent virtual assistant for San Jose State University (SJSU) that answers questions about programs, admissions, deadlines, courses, and campus resources using a ReAct-based AI agent with integrated database and web search capabilities.

## Overview

This project implements a production-ready ReAct (Reasoning + Acting) AI agent that combines:
- **SQLite Database with FTS5**: Fast full-text search on structured SJSU data (76 records including programs, courses, prerequisites, deadlines)
- **Tavily Web Search**: AI-powered web search with automatic fallback for courses/info not in database
- **Groq Llama-3.3-70B**: Lightning-fast cloud inference (~2s average response time)
- **Streamlit UI**: Clean, professional web interface with SJSU branding
- **Anti-Hallucination**: Enhanced prompts and validation to ensure accurate responses

## Key Features

✅ **Accurate Prerequisites**: Returns exact course prerequisites from database  
✅ **Automatic Web Fallback**: Uses Tavily AI search when course not in database  
✅ **No Hallucination**: Admits limitations when information is unavailable  
✅ **Fast Response**: ~2 seconds average with Groq Llama-3.3-70B  
✅ **Comprehensive Data**: 76 records covering CMPE courses, programs, FAQs, resources  
✅ **Production Ready**: Fully tested ReAct loop with proper error handling

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/bvegaloj/CMPE259_Project.git
cd CMPE259_Project

# Run setup script
python setup.py
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up the project structure

### 2. Configuration

Create a `.env` file with your API keys:

```bash
# Required for Groq API (recommended)
GROQ_API_KEY=gsk_your_groq_key_here

# Required for web search
TAVILY_API_KEY=tvly-your_tavily_key_here
```

**Get API Keys:**
- **Groq** (Required): https://console.groq.com/keys - Free tier: 14,400 requests/day
- **Tavily** (Required): https://tavily.com/ - Free tier: 1,000 searches/month

**Why These APIs?**
- Groq provides the fastest Llama-3.3-70B inference available (70x faster than local)
- Tavily offers AI-powered search with content extraction (much better than web scraping)

### 3. Launch the UI

```bash
# Option 1: Using the launch script
python launch_ui.py

# Option 2: Using the shell script
./run_ui.sh

# Option 3: Direct streamlit command
streamlit run ui/streamlit_app.py
```

The UI will open in your browser at `http://localhost:8501`

## Project Structure

```
CMPE259_Project/
├── src/                    # Source code
│   ├── agent/             # ReAct agent orchestration
│   │   └── agent_orchestrator.py  # Main agent with anti-hallucination logic
│   ├── llm/               # LLM client wrappers
│   │   ├── groq_llama_model.py    # Groq Llama-3.3-70B (recommended)
│   │   └── model_loader.py         # Dynamic model loading
│   ├── tools/             # Agent tools
│   │   ├── database_tool.py        # SQLite FTS5 search with course validation
│   │   └── web_search_tool.py      # Tavily AI-powered search
│   ├── database/          # Database layer
│   │   └── db_manager.py           # SQLite with FTS5 full-text search
│   └── utils/             # Utilities
├── ui/                    # Streamlit web interface
│   └── streamlit_app.py   # Main UI with SJSU branding
├── data/                  # SJSU data
│   ├── sjsu_database.db   # SQLite database (76 records)
│   └── queries/           # Test queries for evaluation
├── evaluation/            # Evaluation framework
│   ├── scripts/          # Evaluation scripts
│   │   ├── evaluator_custom.py     # Custom query evaluation
│   │   ├── evaluator_groq.py       # Groq vs local comparison
│   │   ├── evaluator_llama_groq.py # Groq Llama evaluation
│   │   └── groq_speed_test.py      # Performance testing
│   ├── metrics.py        # Evaluation metrics
│   └── data/results/     # Evaluation results
├── demos/                 # Demo scripts
│   └── demo_agent.py     # CLI demonstration
├── tests/                 # Organized test suite
├── requirements.txt       # Python dependencies
├── setup.py              # Setup script
├── launch_ui.py          # UI launcher
└── README.md             # This file
```

## Usage Examples

### Web Interface

1. Launch the UI (see Quick Start above)
2. Type your question in the chat input
3. Example questions:
   - "What are the admission requirements for Computer Science?"
   - "When is the Fall 2025 application deadline?"
   - "What courses are required for CMPE 259?"
   - "Tell me about the MS in AI program"

### Command Line (Demo)

```bash
# Interactive demo
python demos/demo_agent.py

# Tool demonstration
python demos/demo_tools.py
```

## Development

### Running Tests

Tests are organized by category:

```bash
# Test Groq API integration
python tests/models/groq/test_groq.py

# Test Ollama models
python tests/models/ollama/test_ollama.py

# Test agent functionality
python tests/agent/test_agent.py

# Test database tools
python tests/tools/test_database.py
```

### Running Evaluations

Evaluation scripts have been reorganized into `evaluation/scripts/`:

```bash
# Evaluate Groq Llama-3.3-70B performance
python evaluation/scripts/evaluator_llama_groq.py

# Evaluate Groq with custom queries
python evaluation/scripts/evaluator_custom.py

# Run speed tests
python evaluation/scripts/groq_speed_test.py

# View results summary
python evaluation/scripts/print_results.py
```

**Note:** If you previously used commands like `python evaluation/evaluator_*.py`, update them to `python evaluation/scripts/evaluator_*.py`

### Model Management

```bash
# Download models for local inference (Ollama required)
python scripts/download_models.py llama-3-11b
python scripts/download_models.py mistral-7b
```

## Architecture

### Agent System

The agent uses a **ReAct (Reasoning + Acting)** framework with anti-hallucination measures:
1. **Thought**: Agent reasons about the query
2. **Action**: Agent selects and uses a tool (database_query or web_search)
3. **Observation**: Agent observes tool output
4. **Auto-Fallback**: If course not in database, automatically triggers Tavily web search
5. **Validation**: Enhanced parser prioritizes Action before Final Answer to prevent hallucination
6. **Repeat**: Continue until answer is found (max 5 iterations)

### Data Flow

```
User Query
    ↓
DatabaseTool (SQLite FTS5)
    ↓
    Found? → Return exact prerequisites
    ↓
    Not Found? → Auto-trigger Tavily Web Search
    ↓
    Return AI summary + sources
```

### Available Tools

1. **database_query**: SQLite FTS5 full-text search
   - 76 records: programs, courses, prerequisites, deadlines, FAQs, resources
   - Course validation: Checks prerequisites table for CMPE courses
   - Fast response: <100ms
   - Example: "CMPE 259 prerequisites" → "CMPE 252 or CMPE 255 or CMPE 257, or instructor consent"

2. **web_search**: Tavily AI-powered search with automatic fallback
   - Triggers automatically when course not in database
   - Returns AI-generated summary + individual results with content
   - Advanced search depth for comprehensive coverage
   - Example: "CMPE 275 prerequisites" → AI summary + SJSU catalog sources

### LLM Configuration

| Model | Type | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| Groq Llama-3.3-70B | Cloud API | Very Fast (~2s) | Excellent | **Recommended** for production |
| Ollama Mistral-7B | Local | Slower (~85s) | Good | Privacy-focused, offline |
| Ollama Llama-3.2-11B | Local | Moderate (~60s) | Good | Balance of speed/quality |

**Current Configuration**: Groq Llama-3.3-70B with 70x faster inference than local models.

## Performance

Based on production testing with SQLite FTS5 database + Tavily integration:

**Groq Llama-3.3-70B (Cloud API):**
- Average response time: **~2 seconds** (database queries: <100ms, web fallback: 1.5-2.5s)
- Success rate: **100%** on database queries (76 validated records)
- Accuracy: **Zero hallucination** - system admits when data unavailable or uses web search
- Coverage: **Complete** - database + automatic web fallback for missing courses
- Model: 70B parameters, cloud-hosted (14,400 free requests/day)
- Best for: Production use, fast responses, high accuracy, comprehensive coverage

**Local Ollama Mistral-7B:**
- Average response time: **171.59s** (range: 61.60s - 224.96s)
- Success rate: **15%** (3/20 queries) - struggles with ReAct parsing
- Model: 7B parameters, local inference
- Note: Requires improved prompt engineering for better reliability

**Local Ollama Llama-3.2-11B:** *(estimated based on model size)*
- Expected response time: ~60-90s
- Expected success rate: 70-85%
- Model: 11B parameters, local inference  
- Best for: Balance of speed/quality in offline scenarios

### Recommendation
**Use Groq Llama-3.3-70B for best results** - it's significantly faster (70x), more reliable (100% vs 15% success), and provides higher quality responses. The free tier is sufficient for most use cases.

## Requirements

- Python 3.10+
- API Keys (Groq, Tavily)
- Optional: Ollama (for local inference)

## Dependencies

Key packages (see `requirements.txt` for full list):
- `langchain` - Agent framework
- `streamlit` - Web UI
- `groq` - Groq API client
- `tavily-python` - Web search
- `ollama` (optional) - Local inference

## Contributing

This project is part of CMPE 259 at San Jose State University, Fall 2025.

## License

Academic project for educational purposes.

## Authors

- San Jose State University, CMPE 259 Fall 2025

## Acknowledgments

- SJSU for project data and support
- Groq for fast cloud inference
- Tavily for web search API
- LangChain for agent framework
