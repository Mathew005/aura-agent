// --- 1. CONFIGURATION & STATE ---
const config = {
    mapStart: [20.0, 0.0], // Global View
    zoomLevel: 2,
    apiUrl: 'http://localhost:8000'
};

let state = {
    isRunning: false,
    intervalId: null,
    incidentCount: 0,
    simulationSpeed: 5000,
    markers: {},
    isProcessing: false
};

// --- 2. UI CONTROLLER ---
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    setupListeners();
    fetchStatus();
    fetchIncidents(); // Load persisted data on startup
});

let map;

function initMap() {
    // Dark Matter Map Tiles
    map = L.map('map').setView(config.mapStart, config.zoomLevel);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);
}

function setupListeners() {
    // Toggle Simulation
    document.getElementById('sim-toggle').addEventListener('change', (e) => {
        if (e.target.checked) startSimulation();
        else stopSimulation();
    });

    // Speed Slider
    document.getElementById('speed-slider').addEventListener('input', (e) => {
        state.simulationSpeed = 6500 - e.target.value; // Invert logic: higher slider = lower ms
        if (state.isRunning) {
            stopSimulation();
            startSimulation();
        }
    });

    // Reset Button
    document.getElementById('clear-btn').addEventListener('click', async () => {
        if (confirm('Reset System Memory?')) {
            await fetch(`${config.apiUrl}/reset`, { method: 'POST' });
            location.reload();
        }
    });
}

// --- 3. CORE SIMULATION LOGIC ---
function startSimulation() {
    if (state.isRunning) return;
    state.isRunning = true;
    logConsole('info', 'Simulation sequence initiated.');

    // Initial call
    runSimulationStep();
}

function stopSimulation() {
    state.isRunning = false;
    if (state.intervalId) clearTimeout(state.intervalId); // Clear any pending timeout
    logConsole('warn', 'Simulation paused by user.');
}

async function runSimulationStep() {
    if (!state.isRunning || state.isProcessing) return;

    state.isProcessing = true;
    const mockMode = document.getElementById('mock-mode').checked;

    try {
        const start = Date.now();
        const response = await fetch(`${config.apiUrl}/simulate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mock_mode: mockMode })
        });

        const data = await response.json();
        const latency = Date.now() - start;
        document.getElementById('latency').innerText = `${latency}ms`;

        if (data.status === 'success') {
            // A. Add Raw Intel Card
            if (data.raw_data) {
                addIntelCard(data.raw_data.source, data.raw_data.timestamp, data.raw_data.text, data.incident);
            }

            // B. Process Logs (Timeline)
            if (data.logs) {
                processAgentLogs(data.logs, data.incident);
            }

            // C. Update Map & List if Incident Verified
            if (data.incident) {
                addMapMarker(data.incident);
                addVerifiedItem(data.incident);
                updateStats();
            }

        } else if (data.status === 'complete') {
            stopSimulation();
            document.getElementById('sim-toggle').checked = false;
            alert('Simulation Complete');
            state.isProcessing = false;
            return; // Stop loop
        }

    } catch (error) {
        console.error(error);
        logConsole('error', `API Error: ${error.message}`);
    } finally {
        state.isProcessing = false;

        // Schedule next step only if still running
        if (state.isRunning) {
            state.intervalId = setTimeout(runSimulationStep, state.simulationSpeed);
        }
    }
}

function addIntelCard(source, time, text, incident) {
    const container = document.getElementById('intel-feed');
    const card = document.createElement('div');

    // Determine border color based on severity if incident exists, else default
    let colorClass = '';
    if (incident) {
        if (incident.severity === 'Critical') colorClass = 'critical';
        else if (incident.severity === 'High') colorClass = 'warning';
        else colorClass = 'verified';
    }

    card.className = `intel-card ${colorClass}`;
    card.innerHTML = `
        <div class="card-meta">
            <span>${source ? source.toUpperCase() : 'UNKNOWN'}</span>
            <span>${time}</span>
        </div>
        <div class="card-body">
            ${text}
        </div>
    `;
    container.prepend(card);

    // Limit items
    if (container.children.length > 20) container.lastChild.remove();
}

function processAgentLogs(logs, incident) {
    const container = document.getElementById('timeline-feed');

    logs.forEach(log => {
        const item = document.createElement('div');
        let isFinal = log.includes('Action: MERGED') || log.includes('Action: CREATED');
        let isActive = !isFinal;

        item.className = `timeline-item ${isFinal ? 'verified' : 'active'}`;
        item.innerHTML = `
            <div class="timeline-node"></div>
            <div class="log-text">${log}</div>
        `;
        container.prepend(item);

        // Also log to console
        let level = 'info';
        if (log.includes('Rejected')) level = 'warn';
        if (log.includes('Action:')) level = 'success';
        logConsole(level, log);
    });
}

function addVerifiedItem(incident) {
    const list = document.getElementById('verified-list');
    // Strict Deduplication: Check if ID exists
    if (document.getElementById(`inc-${incident.id}`)) {
        return;
    }

    const item = document.createElement('div');
    item.id = `inc-${incident.id}`;
    item.className = 'intel-card verified'; // Reuse card style but smaller
    item.style.cursor = 'pointer';
    item.style.marginBottom = '8px';

    // Add Sources/Citations
    let sourcesHtml = '';
    if (incident.sources && incident.sources.length > 0) {
        sourcesHtml = `<div style="margin-top: 6px; display: flex; gap: 4px; flex-wrap: wrap;">`;
        incident.sources.slice(0, 3).forEach(src => {
            const label = src.source || src.title || 'Source';
            // Fallback to Google Search if no URL
            const searchQuery = encodeURIComponent(`${incident.incident_type || incident.type} ${incident.location_text}`);
            const url = src.url || `https://www.google.com/search?q=${searchQuery}`;

            sourcesHtml += `
                <a href="${url}" target="_blank" style="
                    font-size: 0.65rem; 
                    color: var(--accent-blue); 
                    text-decoration: none; 
                    border: 1px solid var(--border-subtle); 
                    padding: 2px 4px; 
                    border-radius: 2px;
                    max-width: 100px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                ">${label}</a>
            `;
        });
        sourcesHtml += `</div>`;
    }

    const confidenceVal = incident.confidence !== undefined ? (incident.confidence <= 1 ? Math.round(incident.confidence * 100) : incident.confidence) : 'HIGH';

    item.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <strong>${incident.incident_type || incident.type}</strong>
            <span style="font-size: 0.7rem; color: var(--text-muted);">${confidenceVal}% CONF</span>
        </div>
        <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">
            ${incident.location_text}
            <div style="font-size: 0.65rem; color: var(--text-muted); opacity: 0.7; margin-top: 2px; font-family: var(--font-mono); display: flex; align-items: center; gap: 4px;">
                ${incident.coordinates ? `${incident.coordinates[0].toFixed(4)}, ${incident.coordinates[1].toFixed(4)}` : ''}
                ${incident.coordinates ? `<a href="https://google.com/maps?q=${incident.coordinates[0]},${incident.coordinates[1]}&z=8" target="_blank" style="text-decoration: none; color: var(--accent-blue); cursor: pointer;" title="Open in Google Maps">◳</a>` : ''}
            </div>
        </div>
        ${sourcesHtml}
    `;

    item.addEventListener('click', () => {
        map.flyTo(incident.coordinates, 12, { duration: 1.5 });
    });

    list.prepend(item);

    // Update badge and main counter to stay in sync
    const count = list.children.length;
    document.getElementById('verified-count-badge').innerText = count;
    document.getElementById('incident-counter').innerText = count;
    document.getElementById('active-zones').innerText = count;
}

function addMapMarker(incident) {
    if (state.markers[incident.id]) return; // Already mapped

    const color = incident.severity === 'Critical' ? '#ef4444' : '#f59e0b';

    const circle = L.circleMarker(incident.coordinates, {
        color: color,
        fillColor: color,
        fillOpacity: 0.5,
        radius: 8
    }).addTo(map);

    circle.bindPopup(`
        <div style="font-family: sans-serif; color: #333;">
            <strong>${incident.incident_type || incident.type}</strong><br>
            ${incident.location_text}
            <a href="https://google.com/maps?q=${incident.coordinates[0]},${incident.coordinates[1]}&z=8" target="_blank" style="text-decoration: none; color: #3b82f6; margin-left: 4px;" title="Open in Google Maps">◳</a>
        </div>
    `);

    state.markers[incident.id] = circle;

    // Pan map to latest
    map.flyTo(incident.coordinates, 10, { duration: 1.5 });
}

function logConsole(level, msg) {
    const consoleDiv = document.getElementById('console-logs');
    const line = document.createElement('div');
    line.className = 'console-line';

    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    let color = '#a1a1aa';
    if (level === 'info') color = '#3b82f6';
    if (level === 'warn') color = '#f59e0b';
    if (level === 'success') color = '#10b981';
    if (level === 'error') color = '#ef4444';

    line.innerHTML = `
        <span style="color: ${color}">[${level.toUpperCase()}]</span>
        <span style="color: var(--text-muted)">${time}</span>
        <span style="color: var(--text-main)">${msg}</span>
    `;
    consoleDiv.prepend(line);
}

async function fetchStatus() {
    try {
        const res = await fetch(`${config.apiUrl}/status`);
        const data = await res.json();
        state.incidentCount = data.incidents_count;
        document.getElementById('incident-counter').innerText = state.incidentCount;
        document.getElementById('active-zones').innerText = state.incidentCount;
    } catch (e) {
        console.error(e);
    }
}

async function fetchIncidents() {
    try {
        const res = await fetch(`${config.apiUrl}/incidents`);
        const incidents = await res.json();

        // 1. Add/Update existing
        incidents.forEach(incident => {
            addMapMarker(incident);
            addVerifiedItem(incident);
        });

        // 2. Remove stale items (Clean up duplicates or merged items)
        const validIds = new Set(incidents.map(i => `inc-${i.id}`));
        const list = document.getElementById('verified-list');
        Array.from(list.children).forEach(child => {
            if (!validIds.has(child.id)) {
                child.remove();
            }
        });

        // 3. Sync Counters
        const count = incidents.length;
        document.getElementById('verified-count-badge').innerText = count;
        document.getElementById('incident-counter').innerText = count;
        document.getElementById('active-zones').innerText = count;

    } catch (e) {
        console.error("Failed to fetch incidents:", e);
    }
}

async function updateStats() {
    await fetchStatus();
    await fetchIncidents(); // Call fetchIncidents on load/update
}
