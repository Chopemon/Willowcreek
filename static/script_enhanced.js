// script_enhanced.js - Enhanced Dashboard with Real-time Monitoring

let simRunning = false;
let simulationMode = "openrouter";
let statsInterval = null;
let needsChart = null;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function updateNarration(text) {
    const out = document.getElementById("output");
    if (out) {
        out.innerHTML += `<div class="message">${text}</div>`;
        out.scrollTop = out.scrollHeight;
    }
}

function updateSnapshot(snap) {
    if (snap.malcolm_stats) {
        // Can display Malcolm stats if needed
    }
}

// ============================================================================
// TAB MANAGEMENT
// ============================================================================

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;

        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // Load data for the tab
        if (tabName === 'stats') updateStats();
        else if (tabName === 'locations') updateLocations();
        else if (tabName === 'relationships') updateRelationships();
        else if (tabName === 'checkpoints') loadCheckpointsList();
    });
});

// ============================================================================
// MODE SELECTION & INITIALIZATION
// ============================================================================

const btnLocal = document.getElementById("local-btn");
const btnRouter = document.getElementById("openrouter-btn");

btnLocal.onclick = () => {
    simulationMode = "local";
    btnLocal.classList.add("active");
    btnRouter.classList.remove("active");
    updateNarration("🔧 Mode: Local LLM (LM Studio). Click 'Start Simulation'.");
};

btnRouter.onclick = () => {
    simulationMode = "openrouter";
    btnRouter.classList.add("active");
    btnLocal.classList.remove("active");
    updateNarration("🌐 Mode: OpenRouter. Click 'Start Simulation'.");
};

const initBtn = document.getElementById("init-btn");
initBtn.onclick = async () => {
    if (simRunning) {
        updateNarration("🔄 Resetting simulation...");
    }

    try {
        const res = await fetch("/api/init?mode=" + simulationMode);
        const data = await res.json();

        if (data.error) {
            updateNarration(`❌ Error: ${data.error}`);
        } else {
            document.getElementById("output").innerHTML = "";
            updateNarration(`✅ ${data.narration}`);
            updateSnapshot(data.snapshot);
            simRunning = true;
            initBtn.innerText = "Reset Simulation";

            // Start real-time updates
            startMonitoring();
        }
    } catch (e) {
        updateNarration("❌ Connection failed. Is the server running?");
    }
};

// ============================================================================
// ACTION HANDLING
// ============================================================================

async function send() {
    const inputEl = document.getElementById("user-input");
    const txt = inputEl.value.trim();
    if (!txt) return;

    inputEl.value = "";
    updateNarration(`<strong>You:</strong> ${txt}`);

    try {
        const res = await fetch("/api/act", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: txt })
        });
        const data = await res.json();
        updateNarration(`<strong>System:</strong> ${data.narration}`);
        updateSnapshot(data.snapshot);

        // Refresh stats after action
        updateStats();
    } catch (e) {
        updateNarration("❌ Error sending action.");
    }
}

document.getElementById("send-btn").onclick = send;
document.getElementById("wait-btn").onclick = () => {
    document.getElementById("user-input").value = "wait 1";
    send();
};

document.getElementById("user-input").addEventListener("keydown", e => {
    if (e.key === "Enter") send();
});

// ============================================================================
// REAL-TIME STATS MONITORING
// ============================================================================

function startMonitoring() {
    if (statsInterval) clearInterval(statsInterval);

    // Update stats every 5 seconds
    statsInterval = setInterval(() => {
        if (simRunning) {
            updateStats();
        }
    }, 5000);

    // Initial update
    updateStats();
}

async function updateStats() {
    try {
        const res = await fetch("/api/stats");
        const stats = await res.json();

        if (stats.error) return;

        // Update stat cards
        document.getElementById("stat-day").textContent = stats.Day || "-";
        document.getElementById("stat-time").textContent = (stats.Time || "-").split(",").slice(1).join(",").trim();
        document.getElementById("stat-npcs").textContent = stats.NPCs || "-";
        document.getElementById("stat-horny").textContent = stats["Avg Horny"] || "-";
        document.getElementById("stat-lonely").textContent = stats["Avg Lonely"] || "-";
        document.getElementById("stat-secrets").textContent = stats.Secrets || "-";
        document.getElementById("stat-weather").textContent = stats.Weather || "-";
        document.getElementById("stat-season").textContent = stats.Season || "-";

        // Update chart
        updateNeedsChart(stats);
    } catch (e) {
        console.error("Failed to update stats:", e);
    }
}

function updateNeedsChart(stats) {
    const canvas = document.getElementById("needs-chart");
    const ctx = canvas.getContext("2d");

    if (!needsChart) {
        needsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Horny', 'Lonely', 'Gossip', 'Emotions'],
                datasets: [{
                    label: 'Average Values',
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, max: 100 }
                }
            }
        });
    }

    // Update chart data
    const horny = parseFloat(stats["Avg Horny"]) || 0;
    const lonely = parseFloat(stats["Avg Lonely"]) || 0;
    const gossip = stats.Gossip || 0;
    const emotions = stats["Active Emotions"] || 0;

    needsChart.data.datasets[0].data = [horny, lonely, gossip, emotions];
    needsChart.update();
}

// ============================================================================
// LOCATIONS VIEW
// ============================================================================

async function updateLocations() {
    try {
        const res = await fetch("/api/locations");
        const data = await res.json();

        if (data.error) return;

        const listEl = document.getElementById("locations-list");
        listEl.innerHTML = "";

        for (const [location, npcs] of Object.entries(data.locations)) {
            const locationDiv = document.createElement("div");
            locationDiv.className = "location-group";

            const header = document.createElement("h4");
            header.textContent = `📍 ${location} (${npcs.length})`;
            locationDiv.appendChild(header);

            const npcList = document.createElement("ul");
            npcs.forEach(npc => {
                const li = document.createElement("li");
                li.textContent = `${npc.name} - ${npc.mood}`;
                npcList.appendChild(li);
            });
            locationDiv.appendChild(npcList);

            listEl.appendChild(locationDiv);
        }
    } catch (e) {
        console.error("Failed to update locations:", e);
    }
}

// ============================================================================
// RELATIONSHIP NETWORK VISUALIZATION
// ============================================================================

async function updateRelationships() {
    try {
        const res = await fetch("/api/relationships");
        const data = await res.json();

        if (data.error) return;

        const container = document.getElementById("network-graph");

        const nodes = new vis.DataSet(data.nodes);
        const edges = new vis.DataSet(data.edges);

        const graphData = { nodes, edges };

        const options = {
            nodes: {
                shape: 'dot',
                size: 15,
                font: { size: 12 }
            },
            edges: {
                width: 2,
                arrows: { to: { enabled: false } },
                smooth: { type: 'continuous' }
            },
            physics: {
                stabilization: { iterations: 100 },
                barnesHut: { gravitationalConstant: -8000 }
            }
        };

        new vis.Network(container, graphData, options);
    } catch (e) {
        console.error("Failed to update relationships:", e);
    }
}

// ============================================================================
// CHECKPOINT MANAGEMENT
// ============================================================================

document.getElementById("save-checkpoint-btn").onclick = async () => {
    const name = document.getElementById("checkpoint-name").value.trim();
    const desc = document.getElementById("checkpoint-desc").value.trim();

    if (!name) {
        alert("Please enter a checkpoint name");
        return;
    }

    try {
        const res = await fetch("/api/checkpoint/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, description: desc })
        });

        const data = await res.json();

        if (data.success) {
            updateNarration(`✅ Checkpoint saved: ${name}`);
            document.getElementById("checkpoint-name").value = "";
            document.getElementById("checkpoint-desc").value = "";
            loadCheckpointsList();
        } else {
            updateNarration(`❌ Error: ${data.error}`);
        }
    } catch (e) {
        updateNarration("❌ Failed to save checkpoint");
    }
};

async function loadCheckpointsList() {
    try {
        const res = await fetch("/api/checkpoint/list");
        const data = await res.json();

        if (data.error) return;

        const listEl = document.getElementById("checkpoints-list");
        listEl.innerHTML = "";

        if (data.checkpoints.length === 0) {
            listEl.innerHTML = "<p>No checkpoints saved yet.</p>";
            return;
        }

        data.checkpoints.forEach(ckpt => {
            const div = document.createElement("div");
            div.className = "checkpoint-item";

            const info = document.createElement("div");
            info.className = "checkpoint-info";
            info.innerHTML = `
                <strong>${ckpt.checkpoint_name}</strong><br>
                <small>📅 ${ckpt.simulation_time}</small><br>
                <small>💾 ${new Date(ckpt.created_at).toLocaleString()}</small><br>
                ${ckpt.description ? `<small>📝 ${ckpt.description}</small>` : ""}
            `;

            const loadBtn = document.createElement("button");
            loadBtn.className = "btn-small";
            loadBtn.textContent = "Load";
            loadBtn.onclick = () => loadCheckpoint(ckpt.checkpoint_name);

            div.appendChild(info);
            div.appendChild(loadBtn);
            listEl.appendChild(div);
        });
    } catch (e) {
        console.error("Failed to load checkpoints list:", e);
    }
}

async function loadCheckpoint(name) {
    if (!confirm(`Load checkpoint "${name}"? Current progress will be lost.`)) {
        return;
    }

    try {
        const res = await fetch("/api/checkpoint/load", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name })
        });

        const data = await res.json();

        if (data.success) {
            updateNarration(`✅ Checkpoint loaded: ${name}`);
            updateStats();
        } else {
            updateNarration(`❌ Error: ${data.error}`);
        }
    } catch (e) {
        updateNarration("❌ Failed to load checkpoint");
    }
}
