import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import time
import os

# Import project modules
from src.agents.extract_agent import ExtractAgent
from src.agents.verify_agent import VerifyAgent
from src.agents.memory_agent import MemoryAgent
from src.config import DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM, SIMULATION_SPEED_SECONDS

# --- Configuration ---
st.set_page_config(
    page_title="AURA Command Center",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS (Professional Dashboard Theme) ---
st.markdown("""
<style>
    /* Global Font & Colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Column Cards */
    div[data-testid="column"] {
        background-color: #1e2126; /* Slightly lighter than bg */
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        height: 85vh;
        overflow-y: auto;
        transition: all 0.3s ease;
    }
    div[data-testid="column"]:hover {
        border-color: #58a6ff;
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.4);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -0.5px;
        text-transform: uppercase;
        color: #ffffff;
        border-bottom: 2px solid #30363d;
        padding-bottom: 15px;
        margin-bottom: 20px !important;
    }
    h3 {
        font-size: 1.2rem !important;
        color: #8b949e;
    }
    
    /* Data Streams (Monospace) */
    .stCode, .stText, div[data-testid="stCaptionContainer"], .stMarkdown p {
        font-family: 'JetBrains Mono', monospace !important;
        color: #c9d1d9;
        line-height: 1.6;
    }
    
    /* Badges & Alerts */
    .stAlert {
        background-color: #0d1117;
        border-left: 4px solid #58a6ff;
        border-radius: 4px;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(180deg, #238636 0%, #2ea043 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        box-shadow: 0 1px 0 rgba(27,31,35,0.1);
        transition: transform 0.1s;
    }
    .stButton button:active {
        transform: scale(0.98);
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #0d1117; 
    }
    ::-webkit-scrollbar-thumb {
        background: #30363d; 
        border-radius: 5px;
        border: 2px solid #0d1117;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #8b949e; 
    }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'agents_initialized' not in st.session_state:
    st.session_state.extract_agent = ExtractAgent()
    st.session_state.verify_agent = VerifyAgent()
    st.session_state.memory_agent = MemoryAgent()
    st.session_state.agents_initialized = True
    st.session_state.logs = []
    st.session_state.processed_count = 0
    st.session_state.verified_count = 0
    st.session_state.map_center = DEFAULT_MAP_CENTER
    st.session_state.map_zoom = DEFAULT_MAP_ZOOM

def log(message, level="info"):
    timestamp = time.strftime("%H:%M:%S")
    # Update structured log for UI
    if "log_entries" not in st.session_state:
        st.session_state.log_entries = []
    st.session_state.log_entries.insert(0, {
        "timestamp": timestamp,
        "level": level,
        "message": f"[{timestamp}] {message}",
        "type": level
    })
    # Keep legacy text log for backward compatibility if needed
    if "logs" not in st.session_state:
        st.session_state.logs = []
    st.session_state.logs.insert(0, f"[{timestamp}] [{level.upper()}] {message}")

# --- Sidebar ---
with st.sidebar:
    st.title("🛰️ AURA System")
    st.markdown("Automated Urgent Response Agent")
    
    st.divider()
    
    st.subheader("System Status")
    st.success("Agents Online")
    st.info(f"Memory Bank: {len(st.session_state.memory_agent.incidents)} Incidents")
    
    st.divider()
    
    # Control Panel
    st.subheader("Controls")
    speed = st.slider("Simulation Speed (s)", 0.1, 2.0, SIMULATION_SPEED_SECONDS)
    mock_mode = st.toggle("Mock Mode (Save Quota)", value=False)
    run_simulation = st.toggle("Run Simulation", value=False)

# --- Main Layout (3-Column "TweetDeck" Style) ---
# Col 1: Raw Intel (Scout Feed)
# Col 2: Agent Brain (Logs & Verification)
# Col 3: Operational Picture (Map)

col1, col2, col3 = st.columns([1, 1, 1.5])

with col1:
    st.subheader("📡 Raw Intelligence")
    st.caption("Live data stream from Scout Agent")
    
    # Container for raw feed
    feed_container = st.container(height=600)
    
    if "log_entries" not in st.session_state:
        st.session_state.log_entries = []
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "scout_updates" not in st.session_state:
        st.session_state.scout_updates = []
        
    with feed_container:
        if not st.session_state.scout_updates:
            st.info("Waiting for data...")
        
        for update in reversed(st.session_state.scout_updates):
            with st.chat_message("assistant", avatar="🕵️"):
                st.markdown(f"**{update['source']}**")
                st.caption(f"Query: `{update['query']}`")
                st.write(update['content'])
                st.caption(f"🕒 {update.get('timestamp', 'Just now')}")

with col2:
    st.subheader("🧠 Agent Brain")
    st.caption("Processing, Verification & Logic")
    
    # Log Container
    log_container = st.container(height=300)
    with log_container:
        for entry in st.session_state.log_entries:
            if entry["type"] == "info":
                st.info(entry["message"])
            elif entry["type"] == "warn":
                st.warning(entry["message"])
            elif entry["type"] == "error":
                st.error(entry["message"])
            elif entry["type"] == "success":
                st.success(entry["message"])

    st.divider()
    st.subheader("📋 Verified Incidents")
    
    # Verified Feed Container
    verified_container = st.container(height=250)
    with verified_container:
        incidents = st.session_state.memory_agent.get_all_incidents()
        if incidents:
            for incident in reversed(incidents):
                with st.expander(f"{incident['type']} - {incident['location_text']}", expanded=False):
                    st.caption(f"Severity: {incident['severity']}")
                    st.text(f"Reports: {len(incident['reports'])}")
                    if st.button("Locate", key=f"locate_{incident['id']}"):
                        st.session_state.map_center = incident['coordinates']
                        st.session_state.map_zoom = 14
                        if "map_key" not in st.session_state:
                            st.session_state.map_key = 0
                        st.session_state.map_key += 1
                        st.rerun()
                    if st.button("⚠️ Flag", key=f"flag_{incident['id']}"):
                        st.toast(f"Incident #{incident['id']} flagged.", icon="📝")
        else:
            st.info("No verified incidents yet.")

with col3:
    st.subheader("🗺️ Operational Picture")
    
    # Map
    m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)
    
    # Plot incidents
    for incident in st.session_state.memory_agent.get_all_incidents():
        color = "red"
        radius = 5 + (len(incident["reports"]) * 2)
        if incident["severity"] == "Critical":
            color = "darkred"
            radius += 5
            
        folium.CircleMarker(
            location=incident["coordinates"],
            radius=radius,
            popup=f"{incident['type']}: {incident['location_text']} ({len(incident['reports'])} reports)",
            color=color,
            fill=True,
            fill_color=color
        ).add_to(m)
        
    # Force map update by changing key when center changes OR when locate is clicked
    # We use a timestamp to ensure uniqueness on every render if needed, but primarily rely on state
    if "map_key" not in st.session_state:
        st.session_state.map_key = 0
        
    map_key = f"map_{st.session_state.map_center[0]}_{st.session_state.map_center[1]}_{st.session_state.map_zoom}_{st.session_state.map_key}"
    st_folium(m, width="100%", height=600, key=map_key)

# --- Simulation Loop ---
if run_simulation:
    try:
        # Input Source Selection
        if mock_mode:
            # MOCK MODE: Read from CSV
            df = pd.read_csv("data/disaster_stream.csv")
            if st.session_state.processed_count < len(df):
                row = df.iloc[st.session_state.processed_count]
                text = row['text']
                source = row['source']
            else:
                st.success("Mock stream complete.")
                st.stop()
        else:
            # REAL MODE: Fetch from RealIncidentFeed
            if "real_feed" not in st.session_state:
                from src.tools.real_incident_feed import RealIncidentFeed
                st.session_state.real_feed = RealIncidentFeed()
            
            incident = st.session_state.real_feed.get_next_incident()
            if incident:
                text = incident['text']
                source = incident['source']
            else:
                st.warning("No new real-world incidents found. Retrying...")
                time.sleep(2)
                st.rerun()

        # 1. Ingest
        start_time = time.time()
        log(f"Ingesting: {text[:50]}...", "info")
        
        # 2. Extract
        # with st.spinner("Extracting..."): # Removed spinner to reduce UI flicker in fast mode
        extracted_data = st.session_state.extract_agent.extract(text, mock_mode=mock_mode)
        extracted_data["source"] = source
        
        if extracted_data["incident_type"] != "Error":
            log(f"Extracted: {extracted_data['incident_type']} at {extracted_data['location_text']}", "info")
            
            # --- SCOUT AGENT INTERVENTION ---
            if "scout_agent" not in st.session_state:
                from src.agents.scout_agent import ScoutAgent
                st.session_state.scout_agent = ScoutAgent()
            
            # Generate Strategy
            queries = st.session_state.scout_agent.generate_strategy(f"{extracted_data['incident_type']} in {extracted_data['location_text']}")
            
            # Fetch Updates (This populates the Raw Intel Column)
            updates = st.session_state.scout_agent.fetch_updates(queries, mock_mode=mock_mode)
            st.session_state.scout_updates.extend(updates)
            
            # 3. Verify
            verification = st.session_state.verify_agent.verify(extracted_data)
            log(f"Verification Score: {verification['credibility_score']}/100.", "warn" if not verification['is_verified'] else "info")
            
            if verification['is_verified']:
                # 4. Memory Consolidation
                extracted_data.update(verification)
                result = st.session_state.memory_agent.consolidate(extracted_data, mock_mode=mock_mode)
                
                end_time = time.time()
                duration = end_time - start_time
                
                if result["action"] == "merged":
                    log(f"MERGED with Incident #{result['incident_id']} (Trace: {duration:.2f}s)", "info")
                else:
                    log(f"CREATED New Incident #{result['incident_id']} (Trace: {duration:.2f}s)", "info")
                    
                st.session_state.verified_count += 1
            else:
                log("Report rejected due to low credibility.", "warn")
        else:
            log("Failed to extract actionable data.", "error")
            
        st.session_state.processed_count += 1
        time.sleep(speed)
        st.rerun()
            
    except Exception as e:
        st.error(f"Simulation Error: {e}")