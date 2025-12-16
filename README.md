# SJSU Virtual Assistant

An intelligent virtual assistant for San Jose State University (SJSU) that answers questions about programs, admissions, deadlines, courses, and campus resources using a ReAct-based AI agent with integrated database and web search capabilities.

## Overview

This project implements a ReAct-based AI agent that combines:
- **Database Search**: Query structured SJSU data (programs, courses, deadlines, contact info)
- **Web Search**: Real-time information retrieval from the web using Tavily API
- **LLM Backend**: Support for both local models (Ollama) and cloud APIs (Groq)
- **Interactive UI**: Streamlit-based web interface for easy interaction

## Features

- Natural language question answering about SJSU
- Multi-tool agent with database and web search capabilities
- Support for multiple LLM backends:
  - Groq API (Llama-3.3-70B) - Fast cloud inference
  - Ollama (Local Mistral-7B, Llama-3.2-11B) - Privacy-focused local inference
- Clean, professional web UI with SJSU branding
- Comprehensive evaluation framework for model comparison
- Organized test suite for reliability

## Quick Start

### Option A: Google Colab (Recommended for Quick Demo)

Run the project directly in your browser without any local setup:

1. Open the Colab notebook: [colab_setup.ipynb](colab_setup.ipynb)
2. Click "Open in Colab" or upload to Google Colab
3. Add your API keys to Colab Secrets:
   - Click the key icon in the left sidebar
   - Add `GROQ_API_KEY`, `TAVILY_API_KEY`, and `NGROK_API_KEY`
4. Run all cells (Runtime > Run all)
5. Access the UI via the ngrok public URL displayed

The notebook will automatically:
- Clone the repository
- Install all dependencies
- Populate the database
- Launch Streamlit with ngrok tunnel
- Provide a public URL to access the UI

### Option B: Local Installation

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
6. **Repeat**: Continue until answer is found (max 10 iterations)

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
| Ollama Mistral-7B | Local | Moderate (~60s) | Very Good | Privacy-focused, offline - **Recommended local option** |
| Ollama Llama-3.2-11B | Local | Slower (~72s) | Good | Alternative local option |

**Current Configuration**: Groq Llama-3.3-70B with 30x faster inference than local models.

## Performance

Based on evaluation testing with 20 diverse queries using SQLite FTS5 database + Tavily integration:

### Groq Llama-3.3-70B (Cloud API) - Recommended
| Metric | Value |
|--------|-------|
| Average Response Time | **2.0 seconds** |
| Success Rate | **100%** (20/20 queries) |
| Timeout Rate | 0% |
| Hallucination Instances | 0 |

Best for: Production use, fast responses, high accuracy, comprehensive coverage.

### Ollama Mistral-7B (Local) - Recommended for Privacy
| Metric | Value |
|--------|-------|
| Average Response Time | **59.86 seconds** |
| Success Rate | **90%** (18/20 queries) |
| Timeout Rate | 10% (2/20 queries) |

The Mistral-7B model successfully handles most query types with proper tool usage and ReAct format parsing. Recommended for privacy-focused deployments where local execution is preferred.

### Ollama Llama-3.2-11B (Local) - Alternative
| Metric | Value |
|--------|-------|
| Average Response Time | **71.71 seconds** |
| Success Rate | **85%** (17/20 queries) |
| Timeout Rate | 15% (3/20 queries) |

Despite being a larger model, Llama-3.2-11B achieves slightly lower success rate than Mistral-7B, likely due to hardware constraints limiting its performance potential.

### Model Comparison Summary

| Metric | Groq Llama-3.3-70B | Ollama Mistral-7B | Ollama Llama-3.2-11B |
|--------|-------------------|-------------------|---------------------|
| Response Time | 2.0s | 59.86s | 71.71s |
| Success Rate | 100% | 90% | 85% |
| Timeout Rate | 0% | 10% | 15% |
| Cost | Free tier | Free (local) | Free (local) |
| Privacy | Cloud-hosted | Local | Local |

### Recommendation
**Use Groq Llama-3.3-70B for best results** - it's significantly faster (30x), more reliable (100% success rate), and provides highest quality responses. For privacy-conscious deployments requiring local execution, **Mistral-7B is recommended** as it outperforms the larger Llama-3.2-11B with better success rate (90% vs 85%) and faster response time.

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
