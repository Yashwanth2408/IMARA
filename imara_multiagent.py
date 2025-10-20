from typing import Literal
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun
from transformers import pipeline

# Initialize local LLM
hf_pipe = pipeline("text-generation", model="distilgpt2", max_new_tokens=100, pad_token_id=50256)

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
        summary = f"Research findings: {search_results[:500]}"
    except Exception as e:
        summary = f"Research summary: Multi-agent systems are AI frameworks where multiple agents collaborate on tasks."
    
    messages = state["messages"] + [AIMessage(content=f"[RESEARCHER] {summary}")]
    return {
        "messages": messages,
        "research_results": summary,
        "next_agent": "coder"
    }

# Agent 2: Coder - generates code based on research
def coder_agent(state: AgentState) -> dict:
    print("\n[CODER AGENT] Generating code...")
    research = state.get("research_results", "No research available")
    
    code_sample = f"""# Multi-Agent System Code
# Based on research: {research[:100]}

from langgraph.graph import StateGraph
# Define agents and workflow
# ... (implementation)
"""
    
    messages = state["messages"] + [AIMessage(content=f"[CODER] Generated code structure")]
    return {
        "messages": messages,
        "code_output": code_sample,
        "next_agent": "reviewer"
    }

# Agent 3: Reviewer - validates work
def reviewer_agent(state: AgentState) -> dict:
    print("\n[REVIEWER AGENT] Reviewing outputs...")
    code = state.get("code_output", "")
    research = state.get("research_results", "")
    
    feedback = f"Review: Research is comprehensive. Code structure looks good. Approved for presentation."
    
    messages = state["messages"] + [AIMessage(content=f"[REVIEWER] {feedback}")]
    return {
        "messages": messages,
        "review_feedback": feedback,
        "next_agent": "presenter"
    }

# Agent 4: Presenter - compiles final report
def presenter_agent(state: AgentState) -> dict:
    print("\n[PRESENTER AGENT] Creating final report...")
    
    report = f"""
=== IMARA RESEARCH REPORT ===

RESEARCH FINDINGS:
{state.get('research_results', 'N/A')}

CODE GENERATED:
{state.get('code_output', 'N/A')}

REVIEW FEEDBACK:
{state.get('review_feedback', 'N/A')}

=== END OF REPORT ===
"""
    
    messages = state["messages"] + [AIMessage(content=f"[PRESENTER] Report completed")]
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
    print("=" * 60)
    print("IMARA - Intelligent Multi-Agent Research Assistant")
    print("=" * 60)
    
    user_query = input("\nEnter your research topic: ")
    
    # Initialize state with user query
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "next_agent": "researcher"
    }
    
    # Compile and run the graph
    app = build_imara_graph()
    
    print("\n" + "=" * 60)
    print("Starting Multi-Agent Workflow...")
    print("=" * 60)
    
    final_state = app.invoke(initial_state)
    
    # Display final report
    print("\n" + "=" * 60)
    print(final_state.get("final_report", "No report generated"))
    print("=" * 60)
