from typing import Literal
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_ollama import OllamaLLM

# Initialize Ollama LLM (much better than distilgpt2)
llm = OllamaLLM(model="llama3.2:3b", temperature=0.7)

# Initialize web search tool
search_tool = DuckDuckGoSearchRun()

# Define custom state for multi-agent system
class AgentState(MessagesState):
    next_agent: str = ""
    research_results: str = ""
    code_output: str = ""
    review_feedback: str = ""
    final_report: str = ""

# Agent 1: Researcher - searches web and summarizes
def researcher_agent(state: AgentState) -> dict:
    print("\n[RESEARCHER AGENT] Starting research...")
    last_message = state["messages"][-1].content if state["messages"] else ""
    
    # Perform web search
    try:
        search_results = search_tool.run(f"latest research papers on {last_message}")
        search_summary = search_results[:800]
    except Exception as e:
        search_summary = "Unable to perform web search at this time."
    
    # Use LLM to summarize findings
    prompt = f"""You are a research assistant. Summarize the following research findings about "{last_message}" in 3-4 sentences:

{search_summary}

Summary:"""
    
    summary = llm.invoke(prompt)
    
    messages = state["messages"] + [AIMessage(content=f"[RESEARCHER]\n{summary}")]
    return {
        "messages": messages,
        "research_results": summary,
        "next_agent": "coder"
    }

# Agent 2: Coder - generates code based on research
def coder_agent(state: AgentState) -> dict:
    print("\n[CODER AGENT] Generating code...")
    research = state.get("research_results", "No research available")
    
    prompt = f"""You are an expert Python developer. Based on this research summary, generate a Python code skeleton for implementing a multi-agent system:

Research: {research[:300]}

Generate clean, well-commented Python code with proper structure. Keep it under 30 lines.

Code:"""
    
    code = llm.invoke(prompt)
    
    messages = state["messages"] + [AIMessage(content=f"[CODER]\n{code}")]
    return {
        "messages": messages,
        "code_output": code,
        "next_agent": "reviewer"
    }

# Agent 3: Reviewer - validates work
def reviewer_agent(state: AgentState) -> dict:
    print("\n[REVIEWER AGENT] Reviewing outputs...")
    code = state.get("code_output", "")
    research = state.get("research_results", "")
    
    prompt = f"""You are a senior code reviewer. Review the following:

Research Summary: {research[:200]}

Code Generated:
{code[:400]}

Provide a brief 2-3 sentence review focusing on quality, accuracy, and completeness.

Review:"""
    
    feedback = llm.invoke(prompt)
    
    messages = state["messages"] + [AIMessage(content=f"[REVIEWER]\n{feedback}")]
    return {
        "messages": messages,
        "review_feedback": feedback,
        "next_agent": "presenter"
    }

# Agent 4: Presenter - compiles final report
def presenter_agent(state: AgentState) -> dict:
    print("\n[PRESENTER AGENT] Creating final report...")
    
    report = f"""
{'='*70}
              IMARA RESEARCH REPORT
{'='*70}

RESEARCH FINDINGS:
{state.get('research_results', 'N/A')}

{'='*70}

CODE GENERATED:
{state.get('code_output', 'N/A')}

{'='*70}

REVIEW FEEDBACK:
{state.get('review_feedback', 'N/A')}

{'='*70}
"""
    
    messages = state["messages"] + [AIMessage(content=f"[PRESENTER] Report completed and compiled.")]
    return {
        "messages": messages,
        "final_report": report,
        "next_agent": "END"
    }

# Router function to determine next agent
def router(state: AgentState) -> Literal["coder", "reviewer", "presenter", "__end__"]:
    next_agent = state.get("next_agent", "coder")
    if next_agent == "END":
        return "__end__"
    return next_agent

# Build the multi-agent graph
def build_imara_graph():
    graph = StateGraph(AgentState)
    
    # Add all agent nodes
    graph.add_node("researcher", researcher_agent)
    graph.add_node("coder", coder_agent)
    graph.add_node("reviewer", reviewer_agent)
    graph.add_node("presenter", presenter_agent)
    
    # Define workflow edges
    graph.add_edge(START, "researcher")
    graph.add_conditional_edges("researcher", router, ["coder", "reviewer", "presenter", "__end__"])
    graph.add_conditional_edges("coder", router, ["coder", "reviewer", "presenter", "__end__"])
    graph.add_conditional_edges("reviewer", router, ["coder", "reviewer", "presenter", "__end__"])
    graph.add_conditional_edges("presenter", router, ["coder", "reviewer", "presenter", "__end__"])
    
    return graph.compile()

# Main execution
if __name__ == "__main__":
    print("=" * 70)
    print("         IMARA v2 - Intelligent Multi-Agent Research Assistant")
    print("                     Powered by Llama 3.2")
    print("=" * 70)
    
    user_query = input("\nEnter your research topic: ")
    
    # Initialize state with user query
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "next_agent": "researcher"
    }
    
    # Compile and run the graph
    app = build_imara_graph()
    
    print("\n" + "=" * 70)
    print("Starting Multi-Agent Workflow...")
    print("=" * 70)
    
    final_state = app.invoke(initial_state)
    
    # Display final report
    print("\n")
    print(final_state.get("final_report", "No report generated"))
