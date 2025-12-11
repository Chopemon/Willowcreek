// script.js — Fixed Debug & Mode Handling

let simRunning = false;
let simulationMode = "native";  // Default to native when model is loaded

function updateNarration(text) {
    const out = document.getElementById("output");
    if (out) {
        out.innerHTML += `\n\n> ${text}`;
        out.scrollTop = out.scrollHeight;
    }
}

function updateSnapshot(snap) {
    // Update Time Display
    if (snap.time) {
        const timeDisplay = document.getElementById("time-display");
        if (timeDisplay) {
            timeDisplay.innerText = `${snap.time.display} | Day ${snap.time.day}`;
        }
    }

    // Update Malcolm Stats Panel with structured data
    if (snap.malcolm) {
        const m = snap.malcolm;

        // Location
        const locEl = document.getElementById("malcolm-location");
        if (locEl) locEl.innerText = m.location || "---";

        // Stats with progress bars
        updateStatBar("hunger", m.hunger);
        updateStatBar("energy", m.energy);
        updateStatBar("hygiene", m.hygiene);
        updateStatBar("horny", m.horny);
        updateStatBar("social", m.social);
        updateStatBar("lonely", m.lonely);

        // Mood
        const moodEl = document.getElementById("malcolm-mood");
        if (moodEl) moodEl.innerText = m.mood || "---";
    }

    // Update NPCs Here Panel
    if (snap.npcs_here !== undefined) {
        const npcsEl = document.getElementById("npcs-list");
        if (npcsEl) {
            if (snap.npcs_here.length === 0) {
                npcsEl.innerHTML = "<span style='color:#666'>No one nearby</span>";
            } else {
                let html = "";
                for (const npc of snap.npcs_here) {
                    html += `<div class="npc-entry">
                        <span class="npc-name">${npc.name}</span>
                        <div class="npc-info">${npc.age}yo, ${npc.occupation} — ${npc.mood}</div>
                    </div>`;
                }
                npcsEl.innerHTML = html;
            }
        }
    }

    // Update Events Panel
    if (snap.events && snap.events.length > 0) {
        const eventsEl = document.getElementById("events-list");
        if (eventsEl) {
            let html = "";
            for (const evt of snap.events.slice(-5)) {  // Last 5 events
                html += `<div class="event-item">${evt}</div>`;
            }
            eventsEl.innerHTML = html || "<span style='color:#666'>---</span>";
        }
    }

    // Legacy: Update old panels if they exist
    if (snap.malcolm_stats) {
        const statsBox = document.getElementById("malcolm-stats");
        if (statsBox) statsBox.innerText = snap.malcolm_stats;
    }

    if (snap.full_context) {
        const debugBox = document.getElementById("debug-box");
        if (debugBox) debugBox.innerText = "### AI CONTEXT (Live)\n\n" + snap.full_context;
    }
}

function updateStatBar(statName, value) {
    const bar = document.getElementById(`bar-${statName}`);
    const val = document.getElementById(`val-${statName}`);

    if (bar) {
        bar.style.width = `${Math.min(100, Math.max(0, value))}%`;
    }
    if (val) {
        val.innerText = Math.round(value);
    }
}

// Mode Switching
const btnNative = document.getElementById("native-btn");
const btnLocal = document.getElementById("local-btn");
const btnRouter = document.getElementById("openrouter-btn");

function clearModeButtons() {
    if(btnNative) btnNative.classList.remove("active");
    if(btnLocal) btnLocal.classList.remove("active");
    if(btnRouter) btnRouter.classList.remove("active");
}

if (btnNative) {
    btnNative.onclick = () => {
        simulationMode = "native";
        clearModeButtons();
        btnNative.classList.add("active");
        updateNarration("Mode set to: Native (runs model directly). Click 'Start Simulation'.");
    };
    // Set native as default active
    btnNative.classList.add("active");
}

if (btnLocal) {
    btnLocal.onclick = () => {
        simulationMode = "local";
        clearModeButtons();
        btnLocal.classList.add("active");
        updateNarration("Mode set to: LM Studio (localhost:1234). Click 'Start Simulation'.");
    };
}

if (btnRouter) {
    btnRouter.onclick = () => {
        simulationMode = "openrouter";
        clearModeButtons();
        btnRouter.classList.add("active");
        updateNarration("Mode set to: OpenRouter (cloud API). Click 'Start Simulation'.");
    };
}

// Initialize / Start
const initBtn = document.getElementById("init-btn");
if (initBtn) {
    initBtn.onclick = async () => {
        if (simRunning) {
            updateNarration("Simulation reset.");
        }
        
        updateNarration("Initializing...");
        try {
            const res = await fetch("/api/init?mode=" + simulationMode);
            const data = await res.json();
            
            if (data.error) {
                updateNarration("Error: " + data.error);
            } else {
                // Clear old output and show opening
                document.getElementById("output").innerText = ""; 
                updateNarration(data.narration);
                updateSnapshot(data.snapshot);
                simRunning = true;
                initBtn.innerText = "Reset Simulation";
            }
        } catch (e) {
            updateNarration("Connection failed. Is the server running?");
        }
    };
}

// Send Action
async function send() {
    const inputEl = document.getElementById("user-input");
    const txt = inputEl.value;
    if (!txt) return;
    
    inputEl.value = "";
    updateNarration(`User: ${txt}`);
    
    try {
        const res = await fetch("/api/act", {
            method:"POST", headers:{"Content-Type":"application/json"},
            body: JSON.stringify({text: txt})
        });
        const data = await res.json();
        updateNarration(data.narration);
        updateSnapshot(data.snapshot);
    } catch (e) {
        updateNarration("Error sending action.");
    }
}

const sendBtn = document.getElementById("send-btn");
if (sendBtn) sendBtn.onclick = send;

const waitBtn = document.getElementById("wait-btn");
if (waitBtn) waitBtn.onclick = () => {
    document.getElementById("user-input").value = "wait 1"; 
    send();
};

const inputField = document.getElementById("user-input");
if (inputField) {
    inputField.addEventListener("keydown", e => {
        if (e.key === "Enter") send();
    });
}