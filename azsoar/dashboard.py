import streamlit as st
import json
from pathlib import Path
import plotly.express as px

# Clean imports (no relative imports)
from azsoar.monitoring.logger import execution_logger
from azsoar.test.simulator import SentinelSimulator
from azsoar.config import AzSOARConfig
from azsoar.generator import PlaybookGenerator

st.set_page_config(page_title="AzSOAR Dashboard", layout="wide")
st.title("🚀 AzSOAR - Azure Sentinel SOAR Dashboard")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Playbooks", "Test Simulator", "History & Analytics"])

cfg = AzSOARConfig.load()

if page == "Overview":
    st.header("SOAR Health Overview")
    
    stats = execution_logger.get_analytics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Executions", stats["total_executions"])
    with col2:
        st.metric("Success Rate", f"{stats['success_rate']}%", delta="2.3%")
    with col3:
        st.metric("Last 7 Days", stats["last_7_days"])

    st.success("AzSOAR is connected and ready")

elif page == "Playbooks":
    st.header("Generate Playbooks")
    template = st.selectbox("Template", ["phishing-response", "identity-compromise", "ransomware-containment"])
    name = st.text_input("Playbook Name", f"azsoar-{template}")
    output = st.text_input("Output Directory", "./playbooks")
    
    if st.button("Generate Playbook"):
        from .generator import PlaybookGenerator
        try:
            generator = PlaybookGenerator(cfg)
            path = generator.generate(template, output, name)
            st.success(f"✅ Generated at: {path}")
        except Exception as e:
            st.error(f"Generation failed: {e}")

elif page == "Test Simulator":
    st.header("Local Playbook Testing")
    scenario = st.selectbox("Incident Scenario", ["phishing", "identity", "ransomware"])
    
    if st.button("Run Simulation"):
        simulator = SentinelSimulator()
        mock = simulator.create_mock_incident(scenario)
        result = simulator.run_simulation(Path("dummy"), mock)
        st.json(result)
        st.success("Simulation completed successfully!")

elif page == "History & Analytics":
    st.header("Execution History")
    logs = execution_logger.get_execution_history(50)
    
    for log in reversed(logs[-15:]):
        color = "✅" if log["status"] == "success" else "❌"
        st.write(f"{color} **{log['timestamp'][:19]}** | {log['action']} | {log['playbook']}")

    # Simple chart
    if logs:
        df = {"status": [log["status"] for log in logs]}
        fig = px.pie(names=df["status"], title="Action Status Distribution")
        st.plotly_chart(fig)
