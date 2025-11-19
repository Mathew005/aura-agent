# AURA: Automated Urgent Response Agent

AURA is a "God Mode" dashboard for disaster response that turns social media chaos into actionable intelligence.

## Features
- **Intelligent Extraction**: Parses unstructured text into structured incident data.
- **Automated Verification**: Cross-references reports to filter misinformation.
- **Memory Consolidation**: Merges duplicate reports into single, high-confidence incidents.
- **Live Dashboard**: Real-time map visualization and agent thought process log.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file with your API keys:
   ```
   GOOGLE_API_KEY=your_gemini_key
   MAPS_API_KEY=your_google_maps_key
   ```

3. **Run the Application**:
   ```bash
   streamlit run streamlit_app.py
   ```

## Usage
- The dashboard will load and initialize the agents.
- Toggle "Run Simulation" in the sidebar to start processing the synthetic stream.
- Watch as the agents analyze tweets, verify them, and plot them on the map.
