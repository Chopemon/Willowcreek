// script.js — Fixed Debug & Mode Handling

let simRunning = false;
let simulationMode = "openrouter"; 
let selectedModel = "";
let lastSnapshotAt = null;

function updateNarration(text) {
    const out = document.getElementById("output");
    if (out) {
        out.innerHTML += `\n\n> ${text}`;
        out.scrollTop = out.scrollHeight;
    }
}

function updateSnapshot(snap) {
    // Update Malcolm Stats Panel
    if(snap.malcolm_stats) {
        const statsBox = document.getElementById("malcolm-stats");
        if (statsBox) renderStats(statsBox, snap.malcolm_stats);
    }

    // Update Debug Panel (Always show full context now)
    if(snap.full_context) {
        const debugBox = document.getElementById("debug-box");
        if (debugBox) debugBox.innerText = "### AI CONTEXT (Live)\n\n" + snap.full_context;
    }

    lastSnapshotAt = new Date();
    updateStatusPanel();
}

// Mode Switching
const btnLocal = document.getElementById("local-btn");
const btnRouter = document.getElementById("openrouter-btn");
const modelSelect = document.getElementById("model-select");
const modelStatus = document.getElementById("model-status");
const statusMode = document.getElementById("status-mode");
const statusModel = document.getElementById("status-model");
const statusState = document.getElementById("status-state");
const statusUpdated = document.getElementById("status-updated");

function updateStatusPanel(stateOverride) {
    const modeLabel = simulationMode === "local" ? "Local" : "OpenRouter";
    const modelLabel = selectedModel || "Default";
    const stateLabel = stateOverride || (simRunning ? "Running" : "Idle");
    const updatedLabel = lastSnapshotAt ? lastSnapshotAt.toLocaleTimeString() : "—";

    if (statusMode) statusMode.innerText = modeLabel;
    if (statusModel) statusModel.innerText = modelLabel;
    if (statusState) {
        statusState.innerText = stateLabel;
        statusState.classList.toggle("status-chip--running", stateLabel === "Running");
        statusState.classList.toggle("status-chip--error", stateLabel === "Error");
    }
    if (statusUpdated) statusUpdated.innerText = updatedLabel;
}

function renderStats(container, text) {
    container.innerHTML = "";
    const lines = text.split("\n").map((line) => line.trim()).filter(Boolean);
    if (!lines.length) {
        container.innerText = "Status unavailable.";
        return;
    }

    lines.forEach((line) => {
        if (line.startsWith("##") || line.startsWith("###")) {
            const header = document.createElement("div");
            header.className = "stat-header";
            header.innerText = line.replace(/^#+\s*/, "");
            container.appendChild(header);
            return;
        }

        const separator = line.includes("│") ? "│" : line.includes(":") ? ":" : null;
        if (separator) {
            const [label, ...rest] = line.split(separator);
            const value = rest.join(separator).trim();
            const row = document.createElement("div");
            row.className = "stat-row";

            const labelEl = document.createElement("span");
            labelEl.className = "stat-label";
            labelEl.innerText = label.trim();

            const valueEl = document.createElement("span");
            valueEl.className = "stat-value";
            valueEl.innerText = value || "—";

            row.appendChild(labelEl);
            row.appendChild(valueEl);
            container.appendChild(row);
            return;
        }

        const paragraph = document.createElement("div");
        paragraph.className = "stat-note";
        paragraph.innerText = line;
        container.appendChild(paragraph);
    });
}

async function loadModels() {
    if (!modelSelect) return;
    modelSelect.innerHTML = "";
    selectedModel = "";

    try {
        const res = await fetch(`/api/models?mode=${simulationMode}`);
        const data = await res.json();
        const models = data.models || [];
        const defaultModel = data.default_model || "";

        if (!models.length) {
            const opt = new Option("No models found in /models", "");
            opt.disabled = true;
            opt.selected = true;
            modelSelect.appendChild(opt);
            modelSelect.disabled = true;
            if (modelStatus) modelStatus.innerText = "No models detected. Add files/folders to /models.";
            return;
        }

        models.forEach((model) => {
            const opt = new Option(model, model);
            if (model === defaultModel) {
                opt.selected = true;
                selectedModel = model;
            }
            modelSelect.appendChild(opt);
        });

        if (!selectedModel) {
            selectedModel = modelSelect.value;
        }

        modelSelect.disabled = false;
        if (modelStatus) modelStatus.innerText = "Choose a local model before starting.";
    } catch (e) {
        const opt = new Option("Failed to load models", "");
        opt.disabled = true;
        opt.selected = true;
        modelSelect.appendChild(opt);
        modelSelect.disabled = true;
        if (modelStatus) modelStatus.innerText = "Could not load models. Check server logs.";
    }
}

function updateModelUI() {
    if (!modelSelect) return;
    if (simulationMode === "local") {
        loadModels();
    } else {
        modelSelect.innerHTML = "";
        const opt = new Option("Model selection unavailable", "");
        opt.disabled = true;
        opt.selected = true;
        modelSelect.appendChild(opt);
        modelSelect.disabled = true;
        selectedModel = "";
        if (modelStatus) modelStatus.innerText = "Model selection is only available for Local mode.";
    }
}

if (modelSelect) {
    modelSelect.addEventListener("change", () => {
        selectedModel = modelSelect.value;
        if (selectedModel) {
            updateNarration(`Model set to: ${selectedModel}`);
        }
    });
}

if (btnLocal) {
    btnLocal.onclick = () => {
        simulationMode = "local";
        btnLocal.classList.add("active");
        if(btnRouter) btnRouter.classList.remove("active");
        updateNarration("Mode set to: Local (LM Studio). Click 'Start Simulation'.");
        updateModelUI();
        updateStatusPanel();
    };
}

if (btnRouter) {
    btnRouter.onclick = () => {
        simulationMode = "openrouter";
        btnRouter.classList.add("active");
        if(btnLocal) btnLocal.classList.remove("active");
        updateNarration("Mode set to: OpenRouter. Click 'Start Simulation'.");
        updateModelUI();
        updateStatusPanel();
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
        updateStatusPanel("Starting...");
        try {
            const params = new URLSearchParams({ mode: simulationMode });
            if (simulationMode === "local" && selectedModel) {
                params.append("model", selectedModel);
            }
            const res = await fetch(`/api/init?${params.toString()}`);
            const data = await res.json();
            
            if (data.error) {
                updateNarration("Error: " + data.error);
                updateStatusPanel("Error");
            } else {
                // Clear old output and show opening
                document.getElementById("output").innerText = ""; 
                updateNarration(data.narration);
                updateSnapshot(data.snapshot);
                simRunning = true;
                initBtn.innerText = "Reset Simulation";
                updateStatusPanel();
            }
        } catch (e) {
            updateNarration("Connection failed. Is the server running?");
            updateStatusPanel("Error");
        }
    };
}

updateModelUI();
updateStatusPanel();

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
        updateStatusPanel();
    } catch (e) {
        updateNarration("Error sending action.");
        updateStatusPanel("Error");
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
