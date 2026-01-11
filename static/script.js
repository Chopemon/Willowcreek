// script.js — Fixed Debug & Mode Handling

let simRunning = false;
let simulationMode = "openrouter"; 

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
        if (statsBox) statsBox.innerText = snap.malcolm_stats;
    }

    // Update Debug Panel (Always show full context now)
    if(snap.full_context) {
        const debugBox = document.getElementById("debug-box");
        if (debugBox) debugBox.innerText = "### AI CONTEXT (Live)\n\n" + snap.full_context;
    }
}

// Mode Switching
const btnLocal = document.getElementById("local-btn");
const btnRouter = document.getElementById("openrouter-btn");

if (btnLocal) {
    btnLocal.onclick = () => {
        simulationMode = "local";
        btnLocal.classList.add("active");
        if(btnRouter) btnRouter.classList.remove("active");
        updateNarration("Mode set to: Local (LM Studio). Click 'Start Simulation'.");
    };
}

if (btnRouter) {
    btnRouter.onclick = () => {
        simulationMode = "openrouter";
        btnRouter.classList.add("active");
        if(btnLocal) btnLocal.classList.remove("active");
        updateNarration("Mode set to: OpenRouter. Click 'Start Simulation'.");
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