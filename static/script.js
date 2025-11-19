// ============================================
// Willow Creek RPG Simulator - Frontend Script
// ============================================

let simRunning = false;
let simulationMode = "openrouter";
let debugCollapsed = false;

// ============================================
// UPDATE NARRATIVE TEXT
// ============================================
function updateNarration(text) {
    const out = document.getElementById("output");
    if (out) {
        out.innerHTML += `<p>${text}</p>`;
        out.scrollTop = out.scrollHeight;
    }
}

// ============================================
// PARSE AND UPDATE ALL STATS
// ============================================
function updateSnapshot(snap) {
    if (!snap) return;

    // Update full debug context
    if (snap.full_context) {
        const debugBox = document.getElementById("debug-box");
        if (debugBox) debugBox.innerText = "### AI CONTEXT (Live)\n\n" + snap.full_context;

        // Parse stats from full_context
        parseAndUpdateStats(snap.full_context);
    }
}

function parseAndUpdateStats(contextText) {
    if (!contextText) return;

    // Extract Malcolm's section
    const malcolmMatch = contextText.match(/## MALCOLM NEWT - COMPLETE STATE[\s\S]*?(?=##|$)/);
    if (!malcolmMatch) return;

    const malcolmSection = malcolmMatch[0];

    // Parse basic info
    parseBasicInfo(malcolmSection);

    // Parse physical needs
    parsePhysicalNeeds(malcolmSection);

    // Parse psychological state
    parsePsychologicalState(malcolmSection);

    // Parse current status
    parseCurrentStatus(malcolmSection);

    // Parse world info from TIME & ENVIRONMENT section
    const timeMatch = contextText.match(/## TIME & ENVIRONMENT[\s\S]*?(?=##|$)/);
    if (timeMatch) {
        parseWorldInfo(timeMatch[0]);
    }

    // Count population
    const popMatch = contextText.match(/## ALL TOWN RESIDENTS \((\d+) total\)/);
    if (popMatch) {
        updateElement('population-value', `${popMatch[1]} residents`);
    }
}

function parseBasicInfo(text) {
    // Age and Occupation
    const ageMatch = text.match(/Age: (\d+)/);
    const occMatch = text.match(/Occupation: ([^\n]+)/);

    if (ageMatch) updateElement('character-age', `Age: ${ageMatch[1]}`);
    if (occMatch) updateElement('character-occupation', `Occupation: ${occMatch[1].trim()}`);
}

function parsePhysicalNeeds(text) {
    // Hunger
    const hungerMatch = text.match(/Hunger: ([\d.]+)\/100/);
    if (hungerMatch) {
        const value = parseFloat(hungerMatch[1]);
        updateStat('hunger', value);
    }

    // Energy
    const energyMatch = text.match(/Energy: ([\d.]+)\/100/);
    if (energyMatch) {
        const value = parseFloat(energyMatch[1]);
        updateStat('energy', value);
    }

    // Hygiene
    const hygieneMatch = text.match(/Hygiene: ([\d.]+)\/100/);
    if (hygieneMatch) {
        const value = parseFloat(hygieneMatch[1]);
        updateStat('hygiene', value);
    }

    // Bladder
    const bladderMatch = text.match(/Bladder: ([\d.]+)\/100/);
    if (bladderMatch) {
        const value = parseFloat(bladderMatch[1]);
        updateStat('bladder', value);
    }

    // Horny
    const hornyMatch = text.match(/Horny: ([\d.]+)\/100/);
    if (hornyMatch) {
        const value = parseFloat(hornyMatch[1]);
        updateStat('horny', value);
    }
}

function parsePsychologicalState(text) {
    // Lonely
    const lonelyMatch = text.match(/Lonely: ([\d.]+)\/100/);
    if (lonelyMatch) {
        const value = parseFloat(lonelyMatch[1]);
        updateStat('lonely', value);
    }

    // Mood
    const moodMatch = text.match(/Mood: ([A-Z]+)/);
    if (moodMatch) {
        updateElement('mood-value', moodMatch[1]);
    }
}

function parseCurrentStatus(text) {
    // Location
    const locationMatch = text.match(/Location: ([^\n]+)/);
    if (locationMatch) {
        updateElement('location-value', locationMatch[1].trim());
    }

    // Activity (if present)
    const activityMatch = text.match(/Activity: ([^\n]+)/);
    if (activityMatch) {
        updateElement('activity-value', activityMatch[1].trim());
    } else {
        updateElement('activity-value', 'Idle');
    }
}

function parseWorldInfo(text) {
    // Date
    const dateMatch = text.match(/(\w+, \w+ \d+, \d+)/);
    if (dateMatch) {
        updateElement('date-value', dateMatch[1]);
    }

    // Time
    const timeMatch = text.match(/(\d+:\d+ [AP]M)/);
    if (timeMatch) {
        updateElement('time-value', timeMatch[1]);
    }

    // Season
    const seasonMatch = text.match(/Season: (\w+)/);
    if (seasonMatch) {
        updateElement('season-value', seasonMatch[1]);
    }

    // Weather
    const weatherMatch = text.match(/Weather: (\w+)/);
    if (weatherMatch) {
        updateElement('weather-value', weatherMatch[1]);
    }

    // Temperature
    const tempMatch = text.match(/Temperature: ([\d.]+°F)/);
    if (tempMatch) {
        updateElement('temp-value', tempMatch[1]);
    }

    // Day number
    const dayMatch = text.match(/Day #(\d+)/);
    if (dayMatch) {
        // Could display this somewhere if needed
    }
}

// ============================================
// UPDATE STAT BAR AND VALUE
// ============================================
function updateStat(statName, value) {
    // Update text value
    const valueEl = document.getElementById(`${statName}-value`);
    if (valueEl) {
        valueEl.innerText = Math.round(value);
    }

    // Update bar width
    const barEl = document.getElementById(`${statName}-bar`);
    if (barEl) {
        barEl.style.width = `${value}%`;

        // Add glow effect for critical values
        if (statName === 'hunger' && value > 85) {
            barEl.style.boxShadow = '0 0 20px rgba(255, 0, 0, 0.8)';
        } else if (statName === 'energy' && value < 20) {
            barEl.style.boxShadow = '0 0 20px rgba(68, 136, 255, 0.8)';
        } else if (statName === 'bladder' && value > 85) {
            barEl.style.boxShadow = '0 0 20px rgba(255, 170, 68, 0.8)';
        } else {
            // Reset to normal glow
            barEl.style.boxShadow = '';
        }
    }
}

// ============================================
// UPDATE GENERIC ELEMENT
// ============================================
function updateElement(id, value) {
    const el = document.getElementById(id);
    if (el) {
        el.innerText = value;
    }
}

// ============================================
// INITIALIZE SIMULATION
// ============================================
const initBtn = document.getElementById("init-btn");
if (initBtn) {
    initBtn.onclick = async () => {
        if (simRunning) {
            updateNarration("🔄 <em>Simulation reset...</em>");
        }

        updateNarration("⚡ <strong>Initializing Willow Creek...</strong>");

        try {
            const res = await fetch("/api/init?mode=" + simulationMode);
            const data = await res.json();

            if (data.error) {
                updateNarration(`❌ <strong>Error:</strong> ${data.error}`);
            } else {
                // Clear old output
                const out = document.getElementById("output");
                if (out) out.innerHTML = "";

                updateNarration(data.narration);
                updateSnapshot(data.snapshot);
                simRunning = true;
                initBtn.innerText = "🔄 Reset Simulation";
            }
        } catch (e) {
            updateNarration("❌ <strong>Connection failed.</strong> Is the server running?");
        }
    };
}

// ============================================
// SEND ACTION
// ============================================
async function send() {
    const inputEl = document.getElementById("user-input");
    const txt = inputEl.value.trim();
    if (!txt) return;

    inputEl.value = "";
    updateNarration(`<strong>➤ You:</strong> ${txt}`);

    try {
        const res = await fetch("/api/act", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({text: txt})
        });
        const data = await res.json();

        if (data.error) {
            updateNarration(`❌ <strong>Error:</strong> ${data.error}`);
        } else {
            updateNarration(data.narration);
            updateSnapshot(data.snapshot);
        }
    } catch (e) {
        updateNarration("❌ <strong>Error sending action.</strong>");
    }
}

const sendBtn = document.getElementById("send-btn");
if (sendBtn) sendBtn.onclick = send;

const waitBtn = document.getElementById("wait-btn");
if (waitBtn) {
    waitBtn.onclick = () => {
        document.getElementById("user-input").value = "wait 1";
        send();
    };
}

const inputField = document.getElementById("user-input");
if (inputField) {
    inputField.addEventListener("keydown", e => {
        if (e.key === "Enter") send();
    });
}

// ============================================
// DEBUG PANEL TOGGLE
// ============================================
const debugHeader = document.getElementById("debug-header");
const debugBox = document.getElementById("debug-box");
const toggleDebugBtn = document.getElementById("toggle-debug");

if (debugHeader && debugBox && toggleDebugBtn) {
    debugHeader.onclick = () => {
        debugCollapsed = !debugCollapsed;

        if (debugCollapsed) {
            debugBox.style.display = 'none';
            toggleDebugBtn.innerText = '▶';
        } else {
            debugBox.style.display = 'block';
            toggleDebugBtn.innerText = '▼';
        }
    };
}

// ============================================
// INITIAL SETUP
// ============================================
console.log("⚔ Willow Creek RPG Simulator Loaded ⚔");
