# Custom-Mini-Agent

# 🎓 PhD‑Level Research Agent

An autonomous AI agent that conducts **multi‑step, PhD‑level research** on any topic using internet search and OpenAI’s GPT‑4. It decomposes questions, searches in parallel, synthesizes findings, cites sources, and iteratively refines results.

Built with production‑grade patterns: async I/O, retries with exponential backoff, Pydantic config, structured logging, and prompt separation.

---

## ✨ Features

- **Intelligent query decomposition** – Breaks a broad topic into 3–5 focused search queries.
- **Parallel web search** – Uses Tavily API (LLM‑optimised search) with async concurrency.
- **Automatic summarisation** – Truncates long results to stay within token limits.
- **Multi‑step refinement** – Optionally performs a second pass with follow‑up questions.
- **Source attribution** – Every claim is cited with source numbers `[1]` in the final report.
- **Structured outputs** – Produces a well‑organised Markdown report with executive summary, key findings, contradictions, gaps, and conclusion.
- **Production infrastructure** – Retries, logging, directory separation, environment variables.

---

## 🧱 Architecture

ResearchAgent
- **LLMClient** (OpenAI with retries)
- **SearchTool** (Tavily)
- **Prompt templates** (stored as `.txt` files)



**Flow**  
`topic` → generate queries → parallel search → summarise (if needed) → synthesise → (depth>1) follow‑up queries → synthesise again → final report

---

## 🚀 Setup

### 1. Clone the repository

```bash
git clone https://github.com/rahulbana/custom-mini-agent.git
cd custom-mini-agent
```


### 2. Create a virtual environment (recommended)

```
python -m venv venv
source venv/bin/activate      # Linux/macOS
# or
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Set up environment variables
copy .env.example and create a .env file in the project root:

```
cp .env.example .env
```

.env structure looks as below


```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
OPENAI_MODEL=gpt-4-turbo-preview   # optional
```

Get keys:

- [OpenAI API](https://openai.com/){:target="_blank"}
- [Tavily API](https://tavily.com/){:target="_blank"}


### 5. Run the agent

```
python -m research_agent.main
```

### 📂 Project Structure ###

custom-mini-agent/
├── .env
├── requirements.txt
├── README.md
├── logs/                      # auto‑created
│   └── research_agent.log
├── outputs/                   # auto‑created
│   └── research_output_YYYYMMDD_HHMMSS.md
└── research_agent/
    ├── __init__.py
    ├── config.py              # Pydantic settings, paths, env vars
    ├── llm_client.py          # OpenAI wrapper + retries
    ├── search_tool.py         # Tavily search
    ├── prompts/
    │   ├── __init__.py
    │   ├── generate_queries.txt
    │   ├── generate_followup.txt
    │   ├── summarize.txt
    │   ├── synthesize.txt
    │   └── summary_extract.txt
    ├── agent.py               # ResearchAgent core logic
    └── main.py                # CLI entry point


### ⚙️ Configuration

Edit `research_agent/config.py` or override via environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `TAVILY_API_KEY` | *(required)* | Your Tavily API key |
| `OPENAI_MODEL` | `gpt-4-turbo-preview` | OpenAI model name |
| `max_search_results_per_query` | 5 | Results per search query |
| `max_summary_tokens` | 1500 | Character limit for summarising |
| `temperature` | 0.2 | LLM creativity (0.0 – 1.0) |
| `request_timeout` | 30 | API timeout (seconds) |

You can also change the output/log directories inside `config.py` (`LOGS_DIR`, `OUTPUTS_DIR`).

### 🧠 Prompt Customisation

All prompts are stored as plain text files in r`esearch_agent/prompts/`.
You can edit them without touching Python code – perfect for iterative prompt engineering.

Example `prompts/generate_queries.txt`:

```
You are a senior research scientist. Your task is to break down the following research topic into 3-5 specific, concise search engine queries. Each query should explore a different facet of the topic.
Topic: {topic}
Return only a JSON array of strings, e.g. ["query1", "query2", ...].
```

Just edit the file and rerun. the agent will use the new prompt.


### 📊 Outputs & Logging

- **Logs** – `logs/research_agent.log` (rotated daily)
Contains all debug/info/error messages from searches, LLM calls, and retries.

- **Research reports** – `outputs/research_output_YYYYMMDD_HHMMSS.md`
Each run creates a new timestamped Markdown file with the full report and source URLs.


#### 🧪 Example

```
# during execution it will ask user query. 
example `The current state of quantum machine learning algorithms`

```


#### Sample output (truncated):

```
================================================================================
RESEARCH REPORT: The current state of quantum machine learning algorithms

Executive Summary
Quantum machine learning (QML) combines quantum computing with classical ML algorithms.
Recent advances include quantum kernel methods and variational quantum circuits [1][3]...

Key Findings
1. Quantum advantage has been demonstrated for certain small‑scale problems [2].
2. Major challenges remain in noise mitigation and qubit coherence [4].
...
================================================================================
Sources used:
  - https://arxiv.org/abs/2401.12345
  - https://www.nature.com/articles/s41586-023-06567-8
...
```

### 🤝 Contributing
Feel free to open issues or pull requests. Suggestions for better prompts, additional search backends, or performance improvements are welcome.


### 🙏 Acknowledgements

- [OpenAI](https://openai.com/){:target="_blank"} – LLM API
- [Tavily](https://tavily.com/){:target="_blank"} – Search engine for AI agents
- [Tenacity](https://tenacity.readthedocs.io/){:target="_blank"} – Retry library
- [Pydantic](https://docs.pydantic.dev/){:target="_blank"} – Data validation
- [Loguru](https://loguru.readthedocs.io/){:target="_blank"} – Logging


