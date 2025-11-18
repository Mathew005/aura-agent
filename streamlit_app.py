# streamlit_app.py

import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os
import pandas as pd
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="AURA Command Center",
    page_icon="🛰️",
    layout="wide",
)

# --- Load API Keys ---
load_dotenv()
st.session_state.google_api_key = os.getenv("GOOGLE_API_KEY")
st.session_state.maps_api_key = os.getenv("MAPS_API_KEY")

# --- UI ---
st.title("🛰️ AURA Crisis Command Center")

# --- API Key Check ---
if not st.session_state.google_api_key or not st.session_state.maps_api_key:
    st.error("API keys not found. Please create a .env file with your GOOGLE_API_KEY and MAPS_API_KEY.")
else:
    st.success("API keys loaded successfully!")

# --- Map Display ---
st.header("Live Incident Map")
map_center = [34.0522, -118.2437] # Default to Los Angeles
m = folium.Map(location=map_center, zoom_start=10)

# Render the map in Streamlit
st_folium(m, width='100%')

st.info("AURA is standing by. The system is ready to process the incident stream.")