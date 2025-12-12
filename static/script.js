// ============================================
// WILLOW CREEK 2025 - Dashboard Script
// ============================================

// State
let simRunning = false;
let simulationMode = "native";
let allNPCs = [];
let allEvents = [];
let currentSnapshot = null;

// ==================== NAVIGATION ====================

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        const page = item.dataset.page;
        switchPage(page);
    });
});

function switchPage(pageName) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector(`[data-page="${pageName}"]`)?.classList.add('active');

    // Update pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`page-${pageName}`)?.classList.add('active');
}

// ==================== TABS ====================

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        const parent = btn.closest('.tabbed-card');

        parent.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        parent.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

        btn.classList.add('active');
        parent.querySelector(`#tab-${tab}`)?.classList.add('active');
    });
});

// ==================== SIMULATION TOGGLE ====================

const simToggle = document.getElementById('sim-toggle');
const toggleLabel = document.getElementById('toggle-label');
const modeSelect = document.getElementById('mode-select');

if (simToggle) {
    simToggle.addEventListener('change', async () => {
        if (simToggle.checked) {
            await startSimulation();
        } else {
            stopSimulation();
        }
    });
}

if (modeSelect) {
    modeSelect.addEventListener('change', () => {
        simulationMode = modeSelect.value;
    });
}

async function startSimulation() {
    toggleLabel.textContent = 'Starting...';

    try {
        const res = await fetch(`/api/init?mode=${simulationMode}`);
        const data = await res.json();

        if (data.error) {
            updateNarration(`Error: ${data.error}`);
            simToggle.checked = false;
            toggleLabel.textContent = 'Start Simulation';
            return;
        }

        simRunning = true;
        toggleLabel.textContent = 'Running';
        updateSimStatus(true);

        document.getElementById('output').innerHTML = '';
        updateNarration(data.narration);
        updateSnapshot(data.snapshot);

        // Load NPCs for explorer
        loadNPCExplorer();

    } catch (e) {
        updateNarration('Connection failed. Is the server running?');
        simToggle.checked = false;
        toggleLabel.textContent = 'Start Simulation';
    }
}

function stopSimulation() {
    simRunning = false;
    toggleLabel.textContent = 'Start Simulation';
    updateSimStatus(false);
}

function updateSimStatus(running) {
    const statusEl = document.getElementById('sim-status');
    if (statusEl) {
        const dot = statusEl.querySelector('.status-dot');
        const text = statusEl.querySelector('span:last-child');

        if (running) {
            dot.className = 'status-dot online';
            text.textContent = 'Running';
        } else {
            dot.className = 'status-dot offline';
            text.textContent = 'Offline';
        }
    }
}

// ==================== NARRATIVE ====================

function updateNarration(text) {
    const out = document.getElementById('output');
    if (out) {
        out.innerHTML += `<div class="narrative-entry">${text}</div>`;
        out.scrollTop = out.scrollHeight;
    }
}

// Send action
async function send() {
    const inputEl = document.getElementById('user-input');
    const txt = inputEl.value.trim();
    if (!txt || !simRunning) return;

    inputEl.value = '';
    updateNarration(`<strong>You:</strong> ${txt}`);

    try {
        const res = await fetch('/api/act', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: txt })
        });
        const data = await res.json();
        updateNarration(data.narration);
        updateSnapshot(data.snapshot);

        // Add to events log
        if (data.snapshot?.events) {
            data.snapshot.events.forEach(e => addEvent(e, 'system'));
        }
    } catch (e) {
        updateNarration('Error sending action.');
    }
}

document.getElementById('send-btn')?.addEventListener('click', send);
document.getElementById('wait-btn')?.addEventListener('click', () => {
    document.getElementById('user-input').value = 'wait 1';
    send();
});
document.getElementById('user-input')?.addEventListener('keydown', e => {
    if (e.key === 'Enter') send();
});

// ==================== SNAPSHOT UPDATE ====================

function updateSnapshot(snap) {
    if (!snap) return;
    currentSnapshot = snap;

    // Time
    if (snap.time) {
        const timeEl = document.getElementById('time-display');
        if (timeEl) timeEl.textContent = `${snap.time.display} | Day ${snap.time.day}`;
    }

    // Malcolm stats
    if (snap.malcolm) {
        const m = snap.malcolm;

        document.getElementById('malcolm-location').textContent = m.location || '---';

        updateStatBar('hunger', m.hunger);
        updateStatBar('energy', m.energy);
        updateStatBar('hygiene', m.hygiene);
        updateStatBar('horny', m.horny);
        updateStatBar('social', m.social);
        updateStatBar('lonely', m.lonely);

        document.getElementById('malcolm-mood').textContent = m.mood || '---';
    }

    // NPCs nearby
    if (snap.npcs_here !== undefined) {
        updateNearbyNPCs(snap.npcs_here);
    }

    // Events
    if (snap.events) {
        updateEventsTab(snap.events);
    }

    // Update map
    updateMap(snap);
}

function updateStatBar(statName, value) {
    const bar = document.getElementById(`bar-${statName}`);
    const val = document.getElementById(`val-${statName}`);

    if (bar) {
        bar.style.width = `${Math.min(100, Math.max(0, value))}%`;

        // Color coding
        bar.classList.remove('critical', 'warning');
        if (statName === 'hunger' || statName === 'energy') {
            if (value < 20) bar.classList.add('critical');
            else if (value < 40) bar.classList.add('warning');
        }
    }
    if (val) val.textContent = Math.round(value);
}

function updateNearbyNPCs(npcs) {
    const container = document.getElementById('npcs-list');
    if (!container) return;

    if (!npcs || npcs.length === 0) {
        container.innerHTML = '<span class="text-muted">No one nearby</span>';
        return;
    }

    container.innerHTML = npcs.map(npc => `
        <div class="npc-entry" onclick="openNPCDrawer('${npc.name}')">
            <span class="npc-name">${npc.name}</span>
            <div class="npc-info">${npc.age}yo, ${npc.occupation} — ${npc.mood}</div>
        </div>
    `).join('');
}

function updateEventsTab(events) {
    const container = document.getElementById('events-list');
    if (!container) return;

    if (!events || events.length === 0) {
        container.innerHTML = '<span class="text-muted">No events yet</span>';
        return;
    }

    container.innerHTML = events.slice(-5).map(e => `
        <div class="event-item">${e}</div>
    `).join('');
}

// ==================== MAP ====================

function updateMap(snap) {
    if (!snap || !snap.malcolm) return;

    const malcolmLoc = snap.malcolm.location;

    // Update Malcolm indicator
    document.querySelectorAll('.map-location').forEach(loc => {
        loc.classList.remove('malcolm', 'has-npcs');

        const locName = loc.dataset.location;
        if (locName === malcolmLoc) {
            loc.classList.add('malcolm');
        }
    });

    // TODO: Update NPC counts per location from full NPC data
}

// ==================== NPC EXPLORER ====================

async function loadNPCExplorer() {
    // For now, use snapshot data - could add API endpoint later
    const grid = document.getElementById('npc-grid');
    if (!grid) return;

    // This would ideally come from an API
    grid.innerHTML = '<div class="npc-card" onclick="openNPCDrawer(\'Example NPC\')"><div class="npc-card-name">Start simulation to see NPCs</div></div>';
}

document.getElementById('npc-search')?.addEventListener('input', filterNPCs);
document.getElementById('npc-filter-location')?.addEventListener('change', filterNPCs);

function filterNPCs() {
    const search = document.getElementById('npc-search')?.value.toLowerCase() || '';
    const location = document.getElementById('npc-filter-location')?.value || '';

    // Filter logic would go here with full NPC data
}

// ==================== NPC DRAWER ====================

function openNPCDrawer(npcName) {
    const drawer = document.getElementById('npc-drawer');
    if (!drawer) return;

    // Set NPC data
    document.getElementById('drawer-npc-name').textContent = npcName;

    // Find NPC in current snapshot
    if (currentSnapshot?.npcs_here) {
        const npc = currentSnapshot.npcs_here.find(n => n.name === npcName);
        if (npc) {
            document.getElementById('drawer-age').textContent = npc.age;
            document.getElementById('drawer-occupation').textContent = npc.occupation;
            document.getElementById('drawer-location').textContent = currentSnapshot.malcolm?.location || '---';
            document.getElementById('drawer-mood').textContent = npc.mood;
        }
    }

    drawer.classList.add('open');
}

document.getElementById('close-drawer')?.addEventListener('click', () => {
    document.getElementById('npc-drawer')?.classList.remove('open');
});

// Generate portrait for NPC
document.getElementById('generate-portrait-btn')?.addEventListener('click', async () => {
    const npcName = document.getElementById('drawer-npc-name').textContent;
    if (!npcName || !comfyAvailable) return;

    const btn = document.getElementById('generate-portrait-btn');
    btn.disabled = true;
    btn.textContent = 'Generating...';

    try {
        const res = await fetch('/api/comfyui/portrait', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: npcName,
                description: '',
                scene: currentSnapshot?.malcolm?.location || ''
            })
        });
        const data = await res.json();

        if (data.success && data.image) {
            const portrait = document.getElementById('drawer-portrait');
            portrait.innerHTML = `<img src="data:image/png;base64,${data.image}" alt="${npcName}">`;
        }
    } catch (e) {
        console.error('Portrait generation failed:', e);
    }

    btn.disabled = false;
    btn.textContent = 'Generate Portrait';
});

// ==================== EVENTS LOG ====================

function addEvent(text, type = 'system') {
    const feed = document.getElementById('events-feed');
    if (!feed) return;

    // Remove placeholder
    const placeholder = feed.querySelector('.event-placeholder');
    if (placeholder) placeholder.remove();

    const time = new Date().toLocaleTimeString();
    const event = document.createElement('div');
    event.className = `event-item ${type}`;
    event.innerHTML = `
        <div class="event-time">${time}</div>
        <div class="event-text">${text}</div>
    `;

    feed.insertBefore(event, feed.firstChild);
    allEvents.push({ text, type, time });
}

// Event filters
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const filter = btn.dataset.filter;
        filterEvents(filter);
    });
});

function filterEvents(type) {
    const items = document.querySelectorAll('#events-feed .event-item');
    items.forEach(item => {
        if (type === 'all' || item.classList.contains(type)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// ==================== COMFYUI IMAGE GENERATION ====================

let comfyAvailable = false;
let currentWorkflow = '';

async function checkComfyUIStatus() {
    const statusEl = document.getElementById('comfyui-status');
    try {
        const res = await fetch('/api/comfyui/status');
        const data = await res.json();

        comfyAvailable = data.available;
        currentWorkflow = data.current_workflow || '';

        if (comfyAvailable) {
            statusEl.className = 'comfy-status online';
            statusEl.textContent = `ComfyUI: Online (${data.address})`;
            loadWorkflows();
        } else {
            statusEl.className = 'comfy-status offline';
            statusEl.textContent = 'ComfyUI: Offline';
        }
    } catch (e) {
        statusEl.className = 'comfy-status offline';
        statusEl.textContent = 'ComfyUI: Error';
    }
}

async function loadWorkflows() {
    const select = document.getElementById('workflow-select');
    if (!select) return;

    try {
        const res = await fetch('/api/comfyui/workflows');
        const data = await res.json();

        select.innerHTML = '<option value="">-- Select Workflow --</option>';
        data.workflows.forEach(wf => {
            const opt = document.createElement('option');
            opt.value = wf;
            opt.textContent = wf;
            if (wf === data.current) opt.selected = true;
            select.appendChild(opt);
        });
    } catch (e) {
        console.error('Failed to load workflows:', e);
    }
}

document.getElementById('workflow-select')?.addEventListener('change', async (e) => {
    const workflow = e.target.value;
    if (!workflow) return;

    try {
        await fetch('/api/comfyui/load', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ workflow })
        });
        currentWorkflow = workflow;
        addEvent(`Loaded workflow: ${workflow}`, 'system');
    } catch (e) {
        console.error('Failed to load workflow:', e);
    }
});

document.getElementById('refresh-workflows-btn')?.addEventListener('click', checkComfyUIStatus);

document.getElementById('generate-btn')?.addEventListener('click', async () => {
    const prompt = document.getElementById('image-prompt')?.value.trim();
    const negative = document.getElementById('negative-prompt')?.value.trim();

    if (!prompt || !comfyAvailable) return;

    const btn = document.getElementById('generate-btn');
    const placeholder = document.getElementById('image-placeholder');
    const image = document.getElementById('generated-image');

    btn.disabled = true;
    btn.textContent = 'Generating...';
    placeholder.textContent = 'Generating image...';
    placeholder.style.display = 'block';
    image.style.display = 'none';

    try {
        const res = await fetch('/api/comfyui/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, negative_prompt: negative, seed: -1 })
        });
        const data = await res.json();

        if (data.success && data.image) {
            image.src = `data:image/png;base64,${data.image}`;
            image.style.display = 'block';
            placeholder.style.display = 'none';
            addEvent(`Generated image: ${prompt.substring(0, 50)}...`, 'system');
        } else {
            placeholder.textContent = data.error || 'Generation failed';
        }
    } catch (e) {
        placeholder.textContent = 'Connection error';
    }

    btn.disabled = false;
    btn.textContent = 'Generate Image';
});

// Upload workflow
document.getElementById('upload-workflow-btn')?.addEventListener('click', () => {
    document.getElementById('workflow-upload')?.click();
});

document.getElementById('workflow-upload')?.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (ev) => {
        try {
            const workflow = JSON.parse(ev.target.result);
            const name = file.name.replace('.json', '');

            const res = await fetch('/api/comfyui/upload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, workflow })
            });
            const data = await res.json();

            if (data.success) {
                addEvent(`Uploaded workflow: ${data.name}`, 'system');
                loadWorkflows();
            }
        } catch (err) {
            console.error('Invalid workflow JSON:', err);
        }
    };
    reader.readAsText(file);
    e.target.value = '';
});

// ==================== SETTINGS ====================

document.getElementById('settings-temp')?.addEventListener('input', (e) => {
    document.getElementById('temp-value').textContent = e.target.value;
});

// ==================== INIT ====================

// Check ComfyUI on load
checkComfyUIStatus();

// Make openNPCDrawer global
window.openNPCDrawer = openNPCDrawer;
