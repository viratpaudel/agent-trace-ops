import streamlit as st
import pandas as pd
import json
import time
from pathlib import Path

# Local imports
from src.agent.graph import AgentGraph
from src.agent.tools.registry import default_registry
from src.agent.tools.sql_analytics import analytics_engine

st.set_page_config(
    page_title="Agent-Trace-Ops | Autonomous Agent & Observability",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for polished recruiter review
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px 16px;
        border: 1px solid #e9ecef;
    }
    .stCodeBlock {
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Agent-Trace-Ops")
st.caption("Autonomous Multi-Step AI Agent with DuckDB Analytics & Distributed OpenTelemetry Tracing")

# Sidebar
with st.sidebar:
    st.header("⚙️ Agent Controls")
    st.info("Equipped with **DuckDB In-Memory SQL**, **Safe AST Math Sandbox**, and **Web Search** tools.")
    
    st.subheader("🛠️ Registered Tools")
    for tool in default_registry.definitions:
        with st.expander(f"`{tool['name']}`"):
            st.write(tool["description"])
            st.json(tool["parameters"])

    st.divider()
    st.markdown("**Architecture Highlights:**")
    st.markdown("- Zero `eval()` security risks (AST math parser)")
    st.markdown("- Read-only analytical SQL guardrails")
    st.markdown("- Self-correction reflection loop on tool failure")
    st.markdown("- OpenTelemetry-compliant execution spans")

# Main Interface
col_query, col_actions = st.columns([4, 1])

with col_query:
    user_query = st.text_input(
        "Enter task or analytical query for the agent:",
        value="What are the top 5 highest funded AI startups and calculate their average funding?",
        help="The agent will plan steps, inspect database tables or web documents, execute queries, and synthesize findings."
    )

with col_actions:
    st.write(" ")
    st.write(" ")
    run_button = st.button("🚀 Run Agent", type="primary", use_container_width=True)

# Preset Quick Queries
st.markdown("**Quick Presets:**")
p1, p2, p3 = st.columns(3)
if p1.button("📊 Top 5 AI Startups & Valuation", use_container_width=True):
    user_query = "What are the top 5 highest funded AI startups and calculate their average funding?"
    run_button = True
if p2.button("🔍 Database Schema & Sectors", use_container_width=True):
    user_query = "Inspect database schema and list investment rounds by sector."
    run_button = True
if p3.button("🌐 Autonomous Agents & RAG Research", use_container_width=True):
    user_query = "Search research findings on autonomous agents and production RAG."
    run_button = True

if run_button and user_query:
    with st.spinner("Agent planning and executing multi-step workflow..."):
        start_t = time.time()
        graph = AgentGraph(registry=default_registry)
        state = graph.run(user_query)
        trace = state.trace

    # Display Metrics Header
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Execution Latency", f"{trace.total_duration_ms} ms")
    m2.metric("Total Spans", len(trace.spans))
    m3.metric("Tool Executions", len([s for s in trace.spans if s.span_type == "TOOL_CALL"]))
    m4.metric("Total Tokens", trace.total_tokens)
    m5.metric("Est. Cost", f"${trace.total_cost_usd:.6f}")

    tab_report, tab_timeline, tab_trace, tab_db = st.tabs([
        "📄 Executive Report",
        "🔄 Step-by-Step Execution Graph",
        "📊 OpenTelemetry Trace Spans",
        "🗄️ In-Memory Database Explorer"
    ])

    with tab_report:
        st.markdown(state.final_answer)

    with tab_timeline:
        st.subheader("Step-by-Step Reasoning & Action Loop")
        for step in state.steps:
            with st.expander(f"Step {step.step_number}: {step.action_type} - {step.tool_name or 'Synthesis'}", expanded=True):
                st.markdown(f"**Thought:** {step.thought}")
                if step.tool_input:
                    st.markdown("**Tool Arguments:**")
                    st.json(step.tool_input)
                if step.tool_output:
                    st.markdown("**Tool Output Result:**")
                    st.json(step.tool_output)
                if step.reflection:
                    st.warning(f"**Reflection & Self-Correction:** {step.reflection}")

    with tab_trace:
        st.subheader("Distributed Trace Spans")
        spans_data = []
        for s in trace.spans:
            spans_data.append({
                "Span ID": s.span_id,
                "Span Name": s.name,
                "Type": s.span_type,
                "Status": s.status,
                "Duration (ms)": s.duration_ms,
                "Tokens": s.total_tokens,
                "Cost ($)": s.estimated_cost_usd,
            })
        st.dataframe(pd.DataFrame(spans_data), use_container_width=True)

    with tab_db:
        st.subheader("Live DuckDB `tech_investments` Table")
        db_res = analytics_engine.execute_query("SELECT * FROM tech_investments")
        if db_res.get("success"):
            st.dataframe(pd.DataFrame(db_res["data"]), use_container_width=True)
        else:
            st.error("Failed to load database table.")
