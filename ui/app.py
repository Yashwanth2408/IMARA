import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import from root
sys.path.append(str(Path(__file__).parent.parent))

from langgraph.graph import StateGraph, MessagesState, START
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_ollama import OllamaLLM

# Page configuration
st.set_page_config(
    page_title="IMARA - Multi-Agent Research Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .agent-status {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid;
    }
    .researcher { border-color: #2ca02c; background-color: #e7f5e7; }
    .coder { border-color: #ff7f0e; background-color: #fff3e6; }
    .reviewer { border-color: #d62728; background-color: #ffe6e6; }
    .presenter { border-color: #9467bd; background-color: #f3e6ff; }
    .stTextArea textarea { font-family: monospace; }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .quality-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        color: white;
    }
    .grade-a { background-color: #28a745; }
    .grade-b { background-color: #17a2b8; }
    .grade-c { background-color: #ffc107; color: #000; }
    .grade-d { background-color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'agent_outputs' not in st.session_state:
    st.session_state.agent_outputs = {}
if 'final_report' not in st.session_state:
    st.session_state.final_report = ""
if 'quality_metrics' not in st.session_state:
    st.session_state.quality_metrics = {}
if 'routing_analysis' not in st.session_state:
    st.session_state.routing_analysis = {}

# Define agent state
class AgentState(MessagesState):
    next_agent: str = ""
    research_results: str = ""
    code_output: str = ""
    review_feedback: str = ""
    final_report: str = ""
    quality_metrics: dict = {}

# Initialize LLM and tools
@st.cache_resource
def init_llm():
    return OllamaLLM(model="llama3.2:3b", temperature=0.7)

@st.cache_resource
def init_search():
    return DuckDuckGoSearchRun()

llm = init_llm()
search_tool = init_search()

# Agent functions with Streamlit updates and metrics
def researcher_agent(state: AgentState) -> dict:
    with st.status("🔍 Researcher Agent Working...", expanded=True) as status:
        st.write("🔎 Searching ArXiv for academic papers...")
        last_message = state["messages"][-1].content if state["messages"] else ""
        
        # Import enhanced researcher
        try:
            from agents.research_agents import EnhancedResearcherAgent
            from agents.adaptive_router import AdaptiveRouter
            
            # Analyze query with adaptive router
            st.write("🧠 Analyzing query complexity...")
            router = AdaptiveRouter(llm)
            routing_info = router.analyze_query(last_message)
            st.session_state.routing_analysis = routing_info
            st.write(f"   → Route: **{routing_info['path']}** (Confidence: {routing_info['confidence']})")
            
            # Perform research
            researcher = EnhancedResearcherAgent(llm)
            st.write("📚 Analyzing papers with LLM...")
            result = researcher.research(last_message)
            summary = result['full_summary']
            
            # Store metrics
            if 'quality_metrics' in result:
                st.session_state.quality_metrics = result['quality_metrics']
                metrics = result['quality_metrics']
                st.write(f"   ✅ Quality Score: **{metrics['grade']}** ({metrics['overall_score']}/10)")
            
            st.session_state.agent_outputs['researcher'] = summary
            st.session_state.agent_outputs['papers_found'] = len(result.get('papers', []))
            
            status.update(label=f"✅ Research Complete - {len(result.get('papers', []))} papers found", state="complete")
            
        except Exception as e:
            st.error(f"Research agent error: {e}")
            # Fallback to basic search
            st.write("⚠️ Using fallback research method...")
            try:
                search_results = search_tool.run(f"latest research on {last_message}")
                summary = f"Research findings: {search_results[:800]}"
            except:
                summary = f"Research summary for: {last_message}"
            
            st.session_state.agent_outputs['researcher'] = summary
            status.update(label="✅ Research Complete (Fallback)", state="complete")
    
    messages = state["messages"] + [AIMessage(content=summary)]
    return {"messages": messages, "research_results": summary, "next_agent": "coder"}

def coder_agent(state: AgentState) -> dict:
    with st.status("💻 Coder Agent Working...", expanded=True) as status:
        st.write("⚙️ Generating code based on research...")
        research = state.get("research_results", "")
        
        prompt = f"""Based on this research, generate Python code skeleton for a multi-agent system:

Research: {research[:300]}

Generate clean, commented code (under 30 lines).

Code:"""
        
        code = llm.invoke(prompt)
        st.session_state.agent_outputs['coder'] = code
        st.write("✅ Code structure generated")
        status.update(label="✅ Code Generation Complete", state="complete")
    
    messages = state["messages"] + [AIMessage(content=code)]
    return {"messages": messages, "code_output": code, "next_agent": "reviewer"}

def reviewer_agent(state: AgentState) -> dict:
    with st.status("🔎 Reviewer Agent Working...", expanded=True) as status:
        st.write("🔍 Reviewing outputs for quality...")
        code = state.get("code_output", "")
        research = state.get("research_results", "")
        
        prompt = f"""Review this work:

Research: {research[:200]}

Code: {code[:400]}

Provide 2-3 sentence review focusing on quality and completeness.

Review:"""
        
        feedback = llm.invoke(prompt)
        st.session_state.agent_outputs['reviewer'] = feedback
        st.write("✅ Review completed")
        status.update(label="✅ Review Complete", state="complete")
    
    messages = state["messages"] + [AIMessage(content=feedback)]
    return {"messages": messages, "review_feedback": feedback, "next_agent": "presenter"}

def presenter_agent(state: AgentState) -> dict:
    with st.status("📊 Presenter Agent Working...", expanded=True) as status:
        st.write("📝 Compiling final report...")
        
        # Build comprehensive report
        metrics = st.session_state.quality_metrics
        grade = metrics.get('grade', 'N/A') if metrics else 'N/A'
        score = metrics.get('overall_score', 'N/A') if metrics else 'N/A'
        
        report = f"""
## IMARA Research Report

**Research Quality:** {grade} ({score}/10)

---

### Research Findings
{state.get('research_results', 'N/A')}

---

### Code Generated
{state.get('code_output', 'N/A')}


---

### Review Feedback
{state.get('review_feedback', 'N/A')}

---

**Generated by IMARA Multi-Agent System**
"""
        st.session_state.final_report = report
        st.write("✅ Report compilation finished")
        status.update(label="✅ Report Complete", state="complete")
    
    messages = state["messages"] + [AIMessage(content="Report completed")]
    return {"messages": messages, "final_report": report, "next_agent": "END"}

def router(state: AgentState):
    next_agent = state.get("next_agent", "coder")
    return "__end__" if next_agent == "END" else next_agent

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("researcher", researcher_agent)
    graph.add_node("coder", coder_agent)
    graph.add_node("reviewer", reviewer_agent)
    graph.add_node("presenter", presenter_agent)
    
    graph.add_edge(START, "researcher")
    graph.add_conditional_edges("researcher", router, ["coder", "reviewer", "presenter", "__end__"])
    graph.add_conditional_edges("coder", router, ["coder", "reviewer", "presenter", "__end__"])
    graph.add_conditional_edges("reviewer", router, ["coder", "reviewer", "presenter", "__end__"])
    graph.add_conditional_edges("presenter", router, ["coder", "reviewer", "presenter", "__end__"])
    
    return graph.compile()

# UI Layout
st.markdown('<div class="main-header">🤖 IMARA</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem;">Intelligent Multi-Agent Research Assistant</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Powered by Llama 3.2 • LangGraph • ArXiv API</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info("**Model:** Llama 3.2 (3B)\n**Framework:** LangGraph\n**Mode:** Local Inference")
    
    # NEW: Research Quality Metrics
    if st.session_state.quality_metrics:
        st.header("📊 Research Quality")
        metrics = st.session_state.quality_metrics
        
        # Display grade badge
        grade = metrics.get('grade', 'N/A')
        grade_class = 'grade-a' if 'A' in grade else 'grade-b' if 'B' in grade else 'grade-c' if 'C' in grade else 'grade-d'
        st.markdown(f'<span class="quality-badge {grade_class}">{grade}</span>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Overall Score", f"{metrics.get('overall_score', 0)}/10")
        with col2:
            st.metric("Papers Found", metrics.get('paper_count', 0))
        
        if 'breakdown' in metrics:
            st.write("**Quality Breakdown:**")
            for key, value in metrics['breakdown'].items():
                st.progress(value/10, text=f"{key.replace('_', ' ').title()}: {value}/10")
    
    # NEW: Query Analysis
    if st.session_state.routing_analysis:
        st.header("🧠 Query Analysis")
        routing = st.session_state.routing_analysis
        
        st.metric("Routing Path", routing.get('path', 'N/A').replace('_', ' ').title())
        st.metric("Confidence", f"{routing.get('confidence', 0)*100:.0f}%")
        
        if 'scores' in routing:
            with st.expander("View Complexity Scores"):
                for key, value in routing['scores'].items():
                    st.progress(value/10, text=f"{key.title()}: {value}/10")
    
    st.header("📊 Agent Status")
    if st.session_state.agent_outputs:
        agent_names = ['researcher', 'coder', 'reviewer', 'presenter']
        for agent in agent_names:
            if agent in [k.lower() for k in st.session_state.agent_outputs.keys()]:
                st.success(f"✅ {agent.capitalize()}")
            else:
                st.info(f"⏳ {agent.capitalize()}")
    
    st.markdown("---")
    
    if st.button("🔄 Clear All", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent_outputs = {}
        st.session_state.final_report = ""
        st.session_state.quality_metrics = {}
        st.session_state.routing_analysis = {}
        st.rerun()

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Query", "📋 Agent Outputs", "📄 Final Report", "📊 Analytics"])

with tab1:
    st.subheader("Enter Your Research Topic")
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        - Multi-agent reinforcement learning
        - Large language model architectures  
        - Graph neural networks for NLP
        - Retrieval augmented generation systems
        - Autonomous agent frameworks
        """)
    
    query = st.text_input("Research Topic:", placeholder="e.g., Multi-agent LLM systems, RAG architectures, etc.")
    
    if st.button("🚀 Start Research", type="primary", use_container_width=True):
        if query:
            # Clear previous results
            st.session_state.agent_outputs = {}
            st.session_state.final_report = ""
            st.session_state.quality_metrics = {}
            st.session_state.routing_analysis = {}
            
            with st.spinner("Initializing multi-agent workflow..."):
                initial_state = {
                    "messages": [HumanMessage(content=query)],
                    "next_agent": "researcher"
                }
                
                app = build_graph()
                final_state = app.invoke(initial_state)
                
            st.success("✅ All agents completed successfully!")
            st.balloons()
        else:
            st.warning("⚠️ Please enter a research topic")

with tab2:
    st.subheader("Individual Agent Outputs")
    
    if st.session_state.agent_outputs:
        display_order = ['researcher', 'coder', 'reviewer', 'presenter']
        
        for agent in display_order:
            if agent in st.session_state.agent_outputs:
                output = st.session_state.agent_outputs[agent]
                with st.expander(f"🤖 {agent.capitalize()} Agent", expanded=True):
                    st.markdown(output)
    else:
        st.info("🔍 Run a query to see agent outputs")

with tab3:
    st.subheader("Compiled Research Report")
    
    if st.session_state.final_report:
        st.markdown(st.session_state.final_report)
        
        # Download options
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download as Markdown",
                data=st.session_state.final_report,
                file_name=f"imara_report_{st.session_state.get('timestamp', 'report')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col2:
            st.download_button(
                label="📋 Copy as Text",
                data=st.session_state.final_report,
                file_name="imara_report.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.info("📄 Complete a research query to generate a report")

with tab4:
    st.subheader("Research Analytics Dashboard")
    
    if st.session_state.quality_metrics:
        metrics = st.session_state.quality_metrics
        
        # Overall metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Research Grade", metrics.get('grade', 'N/A'))
        with col2:
            st.metric("Overall Score", f"{metrics.get('overall_score', 0)}/10")
        with col3:
            st.metric("Papers Analyzed", metrics.get('paper_count', 0))
        with col4:
            routing = st.session_state.routing_analysis
            st.metric("Route Confidence", f"{routing.get('confidence', 0)*100:.0f}%")
        
        st.markdown("---")
        
        # Detailed breakdown
        if 'breakdown' in metrics:
            st.subheader("Quality Score Breakdown")
            breakdown = metrics['breakdown']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📅 Recency Score", f"{breakdown.get('recency', 0)}/10")
                st.metric("🎯 Relevance Score", f"{breakdown.get('relevance', 0)}/10")
            with col2:
                st.metric("👥 Citation Potential", f"{breakdown.get('citation_potential', 0)}/10")
                st.metric("🌈 Diversity Score", f"{breakdown.get('diversity', 0)}/10")
        
        # Routing analysis
        if st.session_state.routing_analysis:
            st.markdown("---")
            st.subheader("Query Complexity Analysis")
            routing = st.session_state.routing_analysis
            
            if 'scores' in routing:
                scores = routing['scores']
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🔬 Technical Complexity", f"{scores.get('complexity', 0)}/10")
                    st.metric("💻 Code Requirement", f"{scores.get('code', 0)}/10")
                with col2:
                    st.metric("📚 Literature Depth", f"{scores.get('literature', 0)}/10")
                    st.metric("✨ Novelty Level", f"{scores.get('novelty', 0)}/10")
    else:
        st.info("📊 Analytics will appear after running a research query")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🔒 **100% Local & Private**")
with col2:
    st.markdown("🚀 **Built with LangGraph**")
with col3:
    st.markdown("🤖 **Powered by Llama 3.2**")
