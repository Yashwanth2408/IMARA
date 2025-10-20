# IMARA Technical Guide

## System Architecture

### Multi-Agent Workflow
User Query
↓
Researcher Agent (ArXiv Search + Web Search)
↓
Coder Agent (Code Generation)
↓
Reviewer Agent (Quality Validation)
↓
Presenter Agent (Report Compilation)
↓
Final Output (Markdown Report)


### Agent Details

#### 1. Researcher Agent
- **Purpose**: Gather and analyze research papers
- **Tools**: ArXiv API, DuckDuckGo Search
- **LLM Task**: Synthesize findings into coherent summary
- **Output**: Research summary with paper citations

#### 2. Coder Agent
- **Purpose**: Generate implementation code
- **Input**: Research summary
- **LLM Task**: Create Python code skeleton with best practices
- **Output**: Well-commented, structured code

#### 3. Reviewer Agent
- **Purpose**: Quality assurance
- **Input**: Research + Code
- **LLM Task**: Critical analysis and feedback
- **Output**: Review comments and suggestions

#### 4. Presenter Agent
- **Purpose**: Final compilation
- **Input**: All agent outputs
- **Task**: Format into professional report
- **Output**: Markdown report with download option

## Technology Stack

### Core Frameworks
- **LangGraph 1.0.0**: Multi-agent orchestration and state management
- **LangChain 1.0.0**: Agent framework and tool integration
- **Ollama**: Local LLM inference engine

### LLM
- **Model**: Llama 3.2 (3B parameters)
- **Inference**: Local CPU/GPU via Ollama
- **Context Window**: 4096 tokens
- **Temperature**: 0.7 (balanced creativity/accuracy)

### Tools & APIs
- **ArXiv API**: Academic paper search and retrieval
- **DuckDuckGo Search**: Web search fallback
- **PyPDF2**: PDF text extraction
- **Streamlit**: Web UI framework

### Data Storage
- **Session State**: In-memory (Streamlit)
- **Papers**: Local file system (`data/papers/`)
- **Future**: FAISS vector database for RAG

## Agent State Management
class AgentState(MessagesState):
next_agent: str # Routing control
research_results: str # Researcher output
code_output: str # Coder output
review_feedback: str # Reviewer output
final_report: str # Final compiled report


LangGraph manages state immutably, passing updated state between nodes.

## Routing Logic
def router(state: AgentState) -> Literal["coder", "reviewer", "presenter", "end"]:
next_agent = state.get("next_agent", "coder")
if next_agent == "END":
return "end"
return next_agent


Each agent sets `next_agent` in its output, enabling dynamic workflows.

## API Integrations

### ArXiv Search
search = arxiv.Search(
query=query,
max_results=3,
sort_by=arxiv.SortCriterion.Relevance
)

### LLM Invocation
llm = OllamaLLM(model="llama3.2:3b", temperature=0.7)
response = llm.invoke(prompt)


## Performance Considerations

- **LLM Inference Time**: 10-30 seconds per agent (CPU)
- **Web Search**: 2-5 seconds per query
- **Total Workflow**: ~60-90 seconds for complete research cycle
- **Memory Usage**: ~2-4GB RAM (with Llama 3.2)

## Scalability

### Current Limitations
- Single-threaded execution
- No parallel agent execution
- In-memory state only

### Future Improvements
- Async agent execution
- Distributed LLM inference
- Persistent storage with database
- Caching layer for repeated queries

## Error Handling

Each agent includes try-catch blocks for:
- Network failures (ArXiv, DuckDuckGo)
- LLM timeouts
- PDF parsing errors
- Invalid state transitions

Graceful degradation ensures workflow completes even with partial failures.

## Testing

### Manual Testing
python imara_v2.py

### UI Testing
streamlit run ui/app.py

### Test Cases
1. Valid research query
2. Invalid/empty query
3. Network disconnection
4. LLM unavailable
5. Long queries (edge cases)

## Deployment Options

### Local Deployment (Current)
- Runs on localhost:8501
- Requires Ollama running
- Single user

### Docker Deployment (Planned)
FROM python:3.11
COPY . /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "ui/app.py"]

### Cloud Deployment (Future)
- AWS EC2 / Azure VM
- GPU instances for faster inference
- Load balancer for multi-user

## Security

- **100% Local**: No data sent to external APIs (except ArXiv, DuckDuckGo)
- **No API Keys**: Fully open-source stack
- **Private**: User queries never logged externally

## Novelty & Innovation

1. **Fully Open-Source Multi-Agent System**: No paid APIs
2. **ArXiv Integration**: Real academic paper retrieval
3. **Local LLM with LangGraph**: Cutting-edge orchestration
4. **Modular Design**: Easy to extend with new agents
5. **Production-Ready UI**: Professional Streamlit interface

## Future Roadmap

- [ ] FAISS vector database for semantic search
- [ ] Code execution sandbox
- [ ] Multi-turn conversations
- [ ] Export to PDF
- [ ] Agent collaboration patterns (debate, consensus)
- [ ] Fine-tuned domain-specific models
