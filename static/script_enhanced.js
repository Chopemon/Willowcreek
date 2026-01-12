// ===== WILLOW CREEK ENHANCED DASHBOARD SCRIPT =====

class WillowCreekDashboard {
    constructor() {
        this.currentTab = 'stats';
        this.timelineFilters = new Set(['all']);
        this.npcSearchTerm = '';
        this.debugExpanded = false;
        this.latestSnapshot = null;
        this.simulationMode = 'openrouter';

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupTabSwitching();
        this.applyModeDefaults();
        this.refreshLocalModelList();
        this.switchTab('stats'); // Default to stats tab
    }

    // ===== EVENT LISTENERS =====
    setupEventListeners() {
        // Mode selection buttons
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleModeSwitch(e));
        });

        // Action buttons
        document.getElementById('init-sim-btn')?.addEventListener('click', () => this.initSimulation());
        document.getElementById('send-action-btn')?.addEventListener('click', () => this.sendAction());
        document.getElementById('wait-1h-btn')?.addEventListener('click', () => this.wait1Hour());
        document.getElementById('generate-image-btn')?.addEventListener('click', () => this.generateImage());

        // Quick actions
        document.getElementById('save-btn')?.addEventListener('click', () => this.saveCheckpoint());
        document.getElementById('load-btn')?.addEventListener('click', () => this.loadCheckpoint());
        document.getElementById('reset-btn')?.addEventListener('click', () => this.resetSimulation());

        // Enter key in action input
        document.getElementById('action-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendAction();
        });

        // NPC search
        document.getElementById('npc-search')?.addEventListener('input', (e) => {
            this.npcSearchTerm = e.target.value.toLowerCase();
            this.updateNPCProfiles();
        });

        // Timeline filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleTimelineFilter(e));
        });

        // Debug toggle
        document.getElementById('debug-toggle')?.addEventListener('click', () => {
            this.debugExpanded = !this.debugExpanded;
            const content = document.getElementById('debug-content');
            if (content) {
                content.style.display = this.debugExpanded ? 'block' : 'none';
            }
        });
    }

    setupTabSwitching() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    handleModeSwitch(e) {
        document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');

        this.simulationMode = e.target.dataset.mode || 'local';
        console.log(`[Dashboard] Mode switched to: ${this.simulationMode}`);

        this.applyModeDefaults();
        this.refreshLocalModelList();
        this.updateNarrative(`Mode set to: ${this.simulationMode === 'local' ? 'Local Model' : 'OpenRouter'}. Click 'Start Simulation'.`);
    }

    applyModeDefaults() {
        const modelInput = document.getElementById('model-name');
        const memoryInput = document.getElementById('memory-model-name');

        if (!modelInput || !memoryInput) return;

        if (this.simulationMode === 'openrouter') {
            modelInput.setAttribute('list', 'model-options');
            memoryInput.setAttribute('list', 'model-options');
            if (!modelInput.value) {
                modelInput.value = 'tngtech/deepseek-r1t2-chimera:free';
            }
            if (!memoryInput.value) {
                memoryInput.value = 'openai/gpt-4o-mini';
            }
        } else {
            modelInput.setAttribute('list', 'local-model-options');
            memoryInput.setAttribute('list', 'local-model-options');
            const isRemoteModel = (value) => value && value.includes('/');
            if (isRemoteModel(modelInput.value)) {
                modelInput.value = '';
            }
            if (isRemoteModel(memoryInput.value)) {
                memoryInput.value = '';
            }
        }
    }

    async refreshLocalModelList() {
        const modelInput = document.getElementById('model-name');
        const datalist = document.getElementById('local-model-options');

        if (!modelInput || !datalist) return;
        if (this.simulationMode !== 'local') return;

        try {
            const response = await fetch('/api/local-models');
            if (!response.ok) return;
            const data = await response.json();
            const models = Array.isArray(data.models) ? data.models : [];

            datalist.innerHTML = '';
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                datalist.appendChild(option);
            });

            if (models.length > 0) {
                if (!modelInput.value) {
                    modelInput.value = models[0];
                }
                const memoryInput = document.getElementById('memory-model-name');
                if (memoryInput && !memoryInput.value) {
                    memoryInput.value = models[0];
                }
            }
        } catch (error) {
            console.warn('[Dashboard] Failed to load local model list:', error);
        }
    }

    switchTab(tabName) {
        this.currentTab = tabName;

        // Update button states
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update panel visibility
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.toggle('active', panel.id === `${tabName}-tab`);
        });

        // Refresh data for the active tab
        this.refreshTabData(tabName);
    }

    handleTimelineFilter(e) {
        const filterType = e.target.dataset.filter;

        if (filterType === 'all') {
            this.timelineFilters = new Set(['all']);
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.filter === 'all');
            });
        } else {
            this.timelineFilters.delete('all');
            document.querySelector('.filter-btn[data-filter="all"]')?.classList.remove('active');

            if (this.timelineFilters.has(filterType)) {
                this.timelineFilters.delete(filterType);
                e.target.classList.remove('active');
            } else {
                this.timelineFilters.add(filterType);
                e.target.classList.add('active');
            }

            if (this.timelineFilters.size === 0) {
                this.timelineFilters.add('all');
                document.querySelector('.filter-btn[data-filter="all"]')?.classList.add('active');
            }
        }

        this.updateTimeline();
    }

    // ===== API CALLS =====
    async initSimulation() {
        const btn = document.getElementById('init-sim-btn');
        btn.disabled = true;
        btn.textContent = 'Initializing...';

        console.log(`[Dashboard] Initializing with mode: ${this.simulationMode}`);

        try {
            const modelInput = document.getElementById('model-name');
            const memoryInput = document.getElementById('memory-model-name');

            const response = await fetch('/api/init', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mode: this.simulationMode,
                    model_name: modelInput?.value?.trim() || null,
                    memory_model_name: memoryInput?.value?.trim() || null
                })
            });
            const data = await response.json();

            this.updateNarrative(data.narration);
            this.updateSnapshot(data.snapshot);
            this.displayImages(data.images);
            this.displayPortraits(data.portraits || []);

            btn.textContent = 'Initialize Simulation';
        } catch (error) {
            console.error('Init failed:', error);
            this.updateNarrative(`Error: ${error.message}`);
        } finally {
            btn.disabled = false;
        }
    }

    async sendAction() {
        const input = document.getElementById('action-input');
        const action = input.value.trim();
        if (!action) return;

        const btn = document.getElementById('send-action-btn');
        btn.disabled = true;
        btn.textContent = 'Processing...';

        try {
            const response = await fetch('/api/act', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action })
            });
            const data = await response.json();

            this.updateNarrative(data.narration);
            this.updateSnapshot(data.snapshot);
            this.displayImages(data.images);
            this.displayPortraits(data.portraits || []);

            input.value = '';
        } catch (error) {
            console.error('Action failed:', error);
            this.updateNarrative(`Error: ${error.message}`);
        } finally {
            btn.disabled = false;
            btn.textContent = 'Send Action';
        }
    }

    async wait1Hour() {
        const btn = document.getElementById('wait-1h-btn');
        btn.disabled = true;
        btn.textContent = 'Waiting...';

        try {
            const response = await fetch('/api/wait', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hours: 1 })
            });
            const data = await response.json();

            this.updateNarrative(data.narration);
            this.updateSnapshot(data.snapshot);
            this.displayImages(data.images);
        } catch (error) {
            console.error('Wait failed:', error);
            this.updateNarrative(`Error: ${error.message}`);
        } finally {
            btn.disabled = false;
            btn.textContent = 'Wait 1 Hour';
        }
    }

    async generateImage() {
        const btn = document.getElementById('generate-image-btn');
        btn.disabled = true;
        btn.textContent = '🎨 Generating...';

        try {
            const response = await fetch('/api/generate-image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (data.success) {
                this.showNotification('Image generation started! Check the gallery in a moment.', 'success');
                this.displayImages(data.images);
            } else {
                this.showNotification('Image generation failed: ' + (data.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('Image generation failed:', error);
            this.showNotification('Image generation failed: ' + error.message, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = '🎨 Generate Image';
        }
    }

    async saveCheckpoint() {
        const btn = document.getElementById('save-btn');
        btn.disabled = true;
        btn.textContent = 'Saving...';

        try {
            const response = await fetch('/api/save', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                this.showNotification('Checkpoint saved successfully!', 'success');
            } else {
                this.showNotification('Save failed: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Save failed:', error);
            this.showNotification('Save failed: ' + error.message, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = '💾 Save';
        }
    }

    async loadCheckpoint() {
        const btn = document.getElementById('load-btn');
        btn.disabled = true;
        btn.textContent = 'Loading...';

        try {
            const response = await fetch('/api/load', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                this.showNotification('Checkpoint loaded successfully!', 'success');
                this.updateSnapshot(data.snapshot);
            } else {
                this.showNotification('Load failed: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Load failed:', error);
            this.showNotification('Load failed: ' + error.message, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = '📁 Load';
        }
    }

    async resetSimulation() {
        if (!confirm('Are you sure you want to reset the simulation? All progress will be lost.')) {
            return;
        }

        const btn = document.getElementById('reset-btn');
        btn.disabled = true;
        btn.textContent = 'Resetting...';

        try {
            const response = await fetch('/api/reset', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                this.showNotification('Simulation reset!', 'success');
                location.reload();
            }
        } catch (error) {
            console.error('Reset failed:', error);
            this.showNotification('Reset failed: ' + error.message, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = '🔄 Reset';
        }
    }

    // ===== UI UPDATES =====
    updateNarrative(text) {
        const output = document.getElementById('narrative-output');
        if (output) {
            output.innerHTML += `<p>${text}</p>`;
            output.scrollTop = output.scrollHeight;
        }
    }

    updateSnapshot(snapshot) {
        if (!snapshot) return;

        // Store snapshot for use by tabs
        this.latestSnapshot = snapshot;

        // Update time display
        this.updateTimeDisplay(snapshot);

        // Update Malcolm's location
        this.updateMalcolmLocation(snapshot);

        // Update debug info
        this.updateDebugInfo(snapshot);

        // Refresh active tab data
        this.refreshTabData(this.currentTab);
    }

    updateTimeDisplay(snapshot) {
        const timeElement = document.getElementById('current-time');
        const dateElement = document.getElementById('current-date');

        if (snapshot.time && timeElement) {
            const [hour, minute] = snapshot.time.split(':');
            timeElement.textContent = `${hour.padStart(2, '0')}:${minute.padStart(2, '0')}`;
        }

        if (snapshot.date && dateElement) {
            dateElement.textContent = snapshot.date;
        }
    }

    updateMalcolmLocation(snapshot) {
        const locElement = document.getElementById('malcolm-current-loc');
        if (locElement && snapshot.location) {
            locElement.textContent = snapshot.location;
        }
    }

    updateDebugInfo(snapshot) {
        const debugText = document.getElementById('debug-text');
        if (debugText) {
            debugText.textContent = JSON.stringify(snapshot, null, 2);
        }
    }

    displayImages(images) {
        const gallery = document.getElementById('image-gallery');
        if (!gallery) return;

        gallery.innerHTML = '';
        if (!images || images.length === 0) {
            gallery.style.display = 'none';
            return;
        }

        gallery.style.display = 'flex';
        images.forEach(imgData => {
            const container = document.createElement('div');
            container.className = 'scene-image-container';

            const img = document.createElement('img');
            img.src = imgData.url;
            img.alt = imgData.caption || 'Scene image';
            img.className = 'scene-image';
            img.onclick = () => window.open(imgData.url, '_blank');

            const caption = document.createElement('div');
            caption.className = 'scene-image-caption';
            caption.textContent = imgData.caption || 'Scene';

            const badge = document.createElement('span');
            badge.className = `scene-type-badge ${imgData.scene_type}`;
            badge.textContent = imgData.scene_type || 'scene';

            container.appendChild(img);
            container.appendChild(caption);
            container.appendChild(badge);
            gallery.appendChild(container);
        });

        gallery.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    displayPortraits(portraits) {
        const container = document.getElementById('npc-portraits');
        if (!container) {
            // Create portrait container if it doesn't exist
            const narrativeOutput = document.getElementById('narrative-output');
            if (!narrativeOutput) return;

            const portraitsDiv = document.createElement('div');
            portraitsDiv.id = 'npc-portraits';
            portraitsDiv.className = 'npc-portraits-container';
            narrativeOutput.parentNode.insertBefore(portraitsDiv, narrativeOutput);
        }

        const portraitContainer = document.getElementById('npc-portraits');

        if (!portraits || portraits.length === 0) {
            portraitContainer.style.display = 'none';
            return;
        }

        portraitContainer.style.display = 'flex';
        portraitContainer.innerHTML = '';

        portraits.forEach(portrait => {
            const card = document.createElement('div');
            card.className = 'npc-portrait-card';

            const img = document.createElement('img');
            img.src = portrait.url;
            img.alt = portrait.name;
            img.className = 'npc-portrait-image';
            img.onclick = () => window.open(portrait.url, '_blank');

            const name = document.createElement('div');
            name.className = 'npc-portrait-name';
            name.textContent = portrait.name;

            card.appendChild(img);
            card.appendChild(name);
            portraitContainer.appendChild(card);
        });

        console.log(`[Dashboard] Displayed ${portraits.length} NPC portrait(s)`);
    }

    showNotification(message, type = 'info') {
        // Simple notification (could be enhanced with a toast library)
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            z-index: 10000;
            font-weight: bold;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.3s';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // ===== TAB-SPECIFIC UPDATES =====
    refreshTabData(tabName) {
        switch(tabName) {
            case 'stats':
                this.updateStatsPanel();
                break;
            case 'map':
                this.updateLocationMap();
                break;
            case 'npcs':
                this.updateNPCProfiles();
                break;
            case 'timeline':
                this.updateTimeline();
                break;
            case 'analysis':
                this.updateAnalysis();
                break;
        }
    }

    async updateStatsPanel() {
        // Use cached snapshot if available, otherwise fetch
        let data = this.latestSnapshot;

        if (!data) {
            try {
                const response = await fetch('/api/snapshot');
                if (!response.ok) {
                    // Simulation not started yet, ignore silently
                    return;
                }
                data = await response.json();
            } catch (error) {
                console.error('Failed to update stats:', error);
                return;
            }
        }

        if (data.needs) {
            this.renderNeedsStats(data.needs);
        }

        if (data.psychological) {
            this.renderPsychologicalStats(data.psychological);
        }

        // Render quick info (location, time, age, etc)
        this.renderQuickInfo(data);
    }

    renderNeedsStats(needs) {
        const container = document.getElementById('needs-stats');
        if (!container) return;

        const needsData = [
            { label: 'Hunger', value: needs.hunger || 50, key: 'hunger' },
            { label: 'Energy', value: needs.energy || 80, key: 'energy' },
            { label: 'Hygiene', value: needs.hygiene || 60, key: 'hygiene' },
            { label: 'Bladder', value: needs.bladder || 60, key: 'bladder' },
            { label: 'Fun', value: needs.fun || 50, key: 'fun' },
            { label: 'Social', value: needs.social || 50, key: 'social' },
            { label: 'Horny', value: needs.horny || 30, key: 'horny' }
        ];

        container.innerHTML = needsData.map(need => {
            const level = need.value >= 60 ? 'high' : need.value >= 30 ? 'medium' : 'low';
            const inverted = ['hunger', 'bladder', 'horny'].includes(need.key);
            const displayLevel = inverted ? (need.value >= 60 ? 'low' : need.value >= 30 ? 'medium' : 'high') : level;

            return `
                <div class="stat-bar">
                    <div class="stat-label">
                        <span>${need.label}</span>
                        <span class="stat-value">${Math.round(need.value)}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill ${displayLevel}" style="width: ${need.value}%"></div>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderPsychologicalStats(psych) {
        const container = document.getElementById('psychological-stats');
        if (!container) return;

        container.innerHTML = `
            <div class="stat-bar">
                <div class="stat-label">
                    <span>Mood</span>
                    <span class="stat-value">${psych.mood || 'Neutral'}</span>
                </div>
            </div>
            <div class="stat-bar">
                <div class="stat-label">
                    <span>Lonely</span>
                    <span class="stat-value">${Math.round(psych.lonely || 0)}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${psych.lonely >= 60 ? 'low' : psych.lonely >= 30 ? 'medium' : 'high'}"
                         style="width: ${psych.lonely || 0}%"></div>
                </div>
            </div>
            <div class="stat-bar">
                <div class="stat-label">
                    <span>Stress</span>
                    <span class="stat-value">${Math.round(psych.stress || 0)}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${psych.stress >= 60 ? 'low' : psych.stress >= 30 ? 'medium' : 'high'}"
                         style="width: ${psych.stress || 0}%"></div>
                </div>
            </div>
        `;
    }

    renderQuickInfo(data) {
        const container = document.getElementById('quick-info');
        if (!container) return;

        container.innerHTML = `
            <div class="info-row">
                <span class="info-label">Location:</span>
                <span class="info-value">${data.location || 'Unknown'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Time:</span>
                <span class="info-value">${data.time || 'N/A'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Date:</span>
                <span class="info-value">${data.date || 'N/A'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Age:</span>
                <span class="info-value">${data.age || 'N/A'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Occupation:</span>
                <span class="info-value">${data.occupation || 'N/A'}</span>
            </div>
        `;
    }

    async updateLocationMap() {
        try {
            const response = await fetch('/api/locations');
            const data = await response.json();

            this.renderLocationMap(data.locations, data.malcolm_location);
        } catch (error) {
            console.error('Failed to update location map:', error);
        }
    }

    renderLocationMap(locations, malcolmLoc) {
        const container = document.getElementById('location-list');
        if (!container) return;

        if (!locations || Object.keys(locations).length === 0) {
            container.innerHTML = '<p style="color: #666;">No location data available</p>';
            return;
        }

        container.innerHTML = Object.entries(locations).map(([location, npcs]) => {
            const npcTags = npcs.map(npc => {
                const isMalcolm = npc === 'Malcolm Newt';
                return `<span class="npc-tag ${isMalcolm ? 'malcolm' : ''}">${npc}</span>`;
            }).join('');

            return `
                <div class="location-item">
                    <div class="location-name">${location === malcolmLoc ? '📍 ' : ''}${location}</div>
                    <div class="location-npcs">${npcTags}</div>
                </div>
            `;
        }).join('');
    }

    async updateNPCProfiles() {
        try {
            const response = await fetch('/api/npcs');
            const data = await response.json();

            this.renderNPCProfiles(data.npcs);
        } catch (error) {
            console.error('Failed to update NPC profiles:', error);
        }
    }

    renderNPCProfiles(npcs) {
        const container = document.getElementById('npc-profiles-list');
        if (!container) return;

        if (!npcs || npcs.length === 0) {
            container.innerHTML = '<p style="color: #666;">No NPC data available</p>';
            return;
        }

        const filtered = npcs.filter(npc =>
            !this.npcSearchTerm ||
            npc.name.toLowerCase().includes(this.npcSearchTerm) ||
            (npc.occupation && npc.occupation.toLowerCase().includes(this.npcSearchTerm))
        );

        container.innerHTML = filtered.map(npc => `
            <div class="npc-profile">
                <div class="npc-name">${npc.name}</div>
                <div class="npc-info">
                    ${npc.age ? `Age: ${npc.age} | ` : ''}
                    ${npc.occupation || 'Unknown occupation'}<br>
                    ${npc.location ? `📍 ${npc.location}` : ''}
                </div>
            </div>
        `).join('');
    }

    async updateTimeline() {
        try {
            const response = await fetch('/api/timeline');
            const data = await response.json();

            this.renderTimeline(data.events);
        } catch (error) {
            console.error('Failed to update timeline:', error);
        }
    }

    renderTimeline(events) {
        const container = document.getElementById('timeline-events');
        if (!container) return;

        if (!events || events.length === 0) {
            container.innerHTML = '<p style="color: #666;">No events yet</p>';
            return;
        }

        const filtered = events.filter(event =>
            this.timelineFilters.has('all') || this.timelineFilters.has(event.type)
        );

        container.innerHTML = filtered.map(event => `
            <div class="timeline-event">
                <div class="event-time">${event.time}</div>
                <div class="event-description">${event.description}</div>
                <span class="event-type ${event.type}">${event.type}</span>
            </div>
        `).join('');
    }

    async updateAnalysis() {
        try {
            const response = await fetch('/api/analysis');
            const data = await response.json();

            this.renderAnalysis(data);
        } catch (error) {
            console.error('Failed to update analysis:', error);
        }
    }

    renderAnalysis(data) {
        const container = document.getElementById('analysis-content');
        if (!container) return;

        container.innerHTML = `
            <div class="analysis-section">
                <h4>Relationship Network</h4>
                <div class="metric-row">
                    <span class="metric-label">Total Relationships</span>
                    <span class="metric-value">${data.total_relationships || 0}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Average Affinity</span>
                    <span class="metric-value">${data.avg_affinity ? data.avg_affinity.toFixed(1) : 'N/A'}</span>
                </div>
            </div>

            <div class="analysis-section">
                <h4>Activity Patterns</h4>
                <div class="metric-row">
                    <span class="metric-label">Total Actions</span>
                    <span class="metric-value">${data.total_actions || 0}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Most Common Activity</span>
                    <span class="metric-value">${data.top_activity || 'N/A'}</span>
                </div>
            </div>

            <div class="analysis-section">
                <h4>Simulation Stats</h4>
                <div class="metric-row">
                    <span class="metric-label">Time Elapsed</span>
                    <span class="metric-value">${data.time_elapsed || 'N/A'}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Total NPCs</span>
                    <span class="metric-value">${data.total_npcs || 0}</span>
                </div>
            </div>
        `;
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new WillowCreekDashboard();
    console.log('[WillowCreek] Enhanced dashboard initialized');
});
