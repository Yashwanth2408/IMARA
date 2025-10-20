from typing import Literal
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import AIMessage, HumanMessage
from transformers import pipeline

# Setup the local HuggingFace LLM (distilgpt2 for demo)
hf_pipe = pipeline("text-generation", model="distilgpt2", max_new_tokens=40)

def researcher_agent(state: MessagesState) -> dict:
    # Access message content using .content attribute
    last_user_message = state["messages"][-1].content if state["messages"] else ""
    response = hf_pipe(f"Search and summarize latest research on: {last_user_message}")[0]["generated_text"]
    # Add AI assistant reply to message history
    messages = state["messages"] + [AIMessage(content=response)]
    return {"messages": messages}

def human_node(state: MessagesState) -> dict:
    user_input = input("\nType your research topic/query: ")
    messages = state["messages"] + [HumanMessage(content=user_input)]
    return {"messages": messages}

# Build a graph (workflow)
graph = StateGraph(MessagesState)
graph.add_node("researcher_agent", researcher_agent)
graph.add_node("human", human_node)
graph.add_edge(START, "human")
graph.add_edge("human", "researcher_agent")
graph.add_edge("researcher_agent", END)

compiled_graph = graph.compile()

if __name__ == "__main__":
    # Start conversation
    state = {"messages": []}
    for chunk in compiled_graph.stream(state):
        for node_id, update in chunk.items():
            if isinstance(update, dict) and update.get("messages"):
                msg = update["messages"][-1]
                role = msg.type
                content = msg.content
                print(f"\n[{role}] {content}")
