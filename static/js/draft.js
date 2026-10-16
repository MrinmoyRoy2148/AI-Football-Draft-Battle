/**
 * AI Football Battle - Draft Module
 * Handles alternating draft interactions, player filtering, and team roster updates.
 */

let allPlayersList = [];
let currentGameData = null;
let currentPosFilter = "ALL";
let currentSearchTerm = "";

// Initialize Draft Screen on DOM Ready
document.addEventListener("DOMContentLoaded", async () => {
    initDraftUI();
    await loadInitialData();
});

function initDraftUI() {
    // New Match button
    document.getElementById("btn-start-game")?.addEventListener("click", handleStartNewMatch);
    document.getElementById("btn-reset-draft")?.addEventListener("click", handleResetDraft);

    // Filter buttons
    const filterButtons = document.querySelectorAll(".filter-btn");
    filterButtons.forEach(btn => {
        btn.addEventListener("click", (e) => {
            filterButtons.forEach(b => b.classList.remove("active"));
            e.target.classList.add("active");
            currentPosFilter = e.target.getAttribute("data-pos") || "ALL";
            renderPlayerCatalog();
        });
    });

    // Search bar
    const searchInput = document.getElementById("player-search-input");
    searchInput?.addEventListener("input", (e) => {
        currentSearchTerm = e.target.value.toLowerCase().trim();
        renderPlayerCatalog();
    });

    // Analyze Match button
    document.getElementById("btn-proceed-analyze")?.addEventListener("click", () => {
        switchTab("analysis");
        triggerMatchAnalysis();
    });
}

async function loadInitialData() {
    try {
        allPlayersList = await fetchAllPlayers();
        await handleStartNewMatch();
    } catch (err) {
        showToast("Error loading catalog: " + err.message);
    }
}

async function handleStartNewMatch() {
    const teamAName = document.getElementById("input-team-a-name")?.value || "Team Alpha";
    const teamBName = document.getElementById("input-team-b-name")?.value || "Team Beta";
    const formA = document.getElementById("select-form-a")?.value || "1-1-1-2";
    const formB = document.getElementById("select-form-b")?.value || "1-1-1-2";

    try {
        currentGameData = await createGameSession(teamAName, teamBName, formA, formB);
        renderFullDraftView();
        showToast("New Match session started! Team A drafts first.");
    } catch (err) {
        showToast("Failed to start match: " + err.message);
    }
}

async function handleResetDraft() {
    if (!currentGameData) return;
    try {
        currentGameData = await resetGameSession(currentGameData.game_id);
        renderFullDraftView();
        showToast("Draft session reset.");
    } catch (err) {
        showToast("Reset failed: " + err.message);
    }
}

async function handleSelectPlayer(playerId) {
    if (!currentGameData || currentGameData.status !== "drafting") {
        return;
    }

    try {
        currentGameData = await draftPlayerPick(currentGameData.game_id, playerId);
        renderFullDraftView();

        if (currentGameData.status === "completed") {
            showToast("Draft Complete! Click 'Analyze Match' to evaluate rosters.", 4000);
            enableAnalysisButton();
        }
    } catch (err) {
        showToast(err.message);
    }
}

function renderFullDraftView() {
    if (!currentGameData) return;

    renderTurnStatus();
    renderTeamPanels();
    renderPlayerCatalog();

    if (currentGameData.status === "completed") {
        enableAnalysisButton();
    } else {
        disableAnalysisButton();
    }
}

function renderTurnStatus() {
    const turnEl = document.getElementById("turn-status-text");
    const dotEl = document.getElementById("turn-pulse-dot");
    const progressFill = document.getElementById("draft-progress-bar");
    const progressText = document.getElementById("draft-progress-text");

    const draftedCount = (currentGameData.teams.A.player_ids.length) + (currentGameData.teams.B.player_ids.length);
    const progressPct = (draftedCount / 10) * 100;

    if (progressFill) progressFill.style.width = `${progressPct}%`;
    if (progressText) progressText.textContent = `${draftedCount} / 10 Drafted`;

    if (currentGameData.status === "completed") {
        if (turnEl) turnEl.textContent = "Draft Complete - Ready for Tactical Analysis";
        if (dotEl) {
            dotEl.className = "turn-pulse-dot";
            dotEl.style.background = "#10b981";
            dotEl.style.boxShadow = "0 0 15px #10b981";
        }
        return;
    }

    const currentTurn = currentGameData.current_turn;
    const teamName = currentGameData.teams[currentTurn].name || `Team ${currentTurn}`;

    if (turnEl) turnEl.textContent = `${teamName}'s Pick (Turn ${currentTurn})`;
    if (dotEl) {
        dotEl.className = `turn-pulse-dot ${currentTurn === "A" ? "turn-pulse-a" : "turn-pulse-b"}`;
    }

    // Active panel borders
    const panelA = document.getElementById("panel-team-a");
    const panelB = document.getElementById("panel-team-b");
    if (panelA && panelB) {
        panelA.classList.toggle("active-turn", currentTurn === "A");
        panelB.classList.toggle("active-turn", currentTurn === "B");
    }
}

function renderTeamPanels() {
    renderSingleTeamPanel("A", currentGameData.teams.A);
    renderSingleTeamPanel("B", currentGameData.teams.B);
}

function renderSingleTeamPanel(teamKey, teamObj) {
    const titleEl = document.getElementById(`team-title-${teamKey.toLowerCase()}`);
    const formEl = document.getElementById(`team-form-badge-${teamKey.toLowerCase()}`);
    const rosterListEl = document.getElementById(`roster-list-${teamKey.toLowerCase()}`);

    if (titleEl) titleEl.textContent = teamObj.name || `Team ${teamKey}`;
    if (formEl) formEl.textContent = teamObj.formation;

    if (!rosterListEl) return;
    rosterListEl.innerHTML = "";

    const playerMap = new Map(allPlayersList.map(p => [p.id, p]));

    for (let slot = 0; slot < 5; slot++) {
        const playerId = teamObj.player_ids[slot];
        const slotCard = document.createElement("div");
        slotCard.className = "roster-slot-card" + (playerId ? " filled" : "");

        if (playerId && playerMap.has(playerId)) {
            const player = playerMap.get(playerId);
            const posClass = `pos-${player.position.toLowerCase()}`;
            slotCard.innerHTML = `
                <div class="roster-player-info">
                    <span class="pos-tag ${posClass}">${player.position}</span>
                    <span class="roster-player-name">${player.name}</span>
                </div>
                <span class="roster-player-overall">${player.overall}</span>
            `;
        } else {
            slotCard.innerHTML = `
                <div class="roster-player-info">
                    <span class="pos-tag" style="background:rgba(255,255,255,0.1);color:#64748b;">Slot ${slot + 1}</span>
                    <span class="roster-slot-empty">Awaiting draft...</span>
                </div>
                <span class="roster-slot-empty">-</span>
            `;
        }

        rosterListEl.appendChild(slotCard);
    }
}

function renderPlayerCatalog() {
    const catalogContainer = document.getElementById("players-catalog-grid");
    if (!catalogContainer) return;

    catalogContainer.innerHTML = "";
    const draftedSet = new Set([
        ...(currentGameData?.teams.A.player_ids || []),
        ...(currentGameData?.teams.B.player_ids || [])
    ]);

    const filtered = allPlayersList.filter(player => {
        const matchesPos = (currentPosFilter === "ALL" || player.position === currentPosFilter);
        const matchesSearch = player.name.toLowerCase().includes(currentSearchTerm);
        return matchesPos && matchesSearch;
    });

    const isDraftFinished = currentGameData?.status === "completed";
    const activeTeamKey = currentGameData?.current_turn || "A";

    filtered.forEach(player => {
        const isDrafted = draftedSet.has(player.id);
        const card = document.createElement("div");
        card.className = `player-card ${isDrafted ? "drafted" : ""}`;

        const posClass = `pos-${player.position.toLowerCase()}`;

        card.innerHTML = `
            <div class="card-top">
                <span class="pos-tag ${posClass}">${player.position}</span>
                <span class="roster-player-overall">${player.overall}</span>
            </div>
            <div class="card-name" title="${player.name}">${player.name}</div>
            <div class="card-stats-row">
                <div class="stat-item">
                    <div class="stat-label">ATT</div>
                    <div class="stat-val">${player.attack}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">MID</div>
                    <div class="stat-val">${player.midfield}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">DEF</div>
                    <div class="stat-val">${player.defense}</div>
                </div>
            </div>
            <button class="card-action-btn ${activeTeamKey === 'A' ? 'btn-draft-a' : 'btn-draft-b'}" 
                    ${isDrafted || isDraftFinished ? 'disabled' : ''} 
                    id="btn-draft-${player.id}">
                ${isDrafted ? 'Drafted' : `Draft for Team ${activeTeamKey}`}
            </button>
        `;

        if (!isDrafted && !isDraftFinished) {
            card.addEventListener("click", () => handleSelectPlayer(player.id));
        }

        catalogContainer.appendChild(card);
    });
}

function enableAnalysisButton() {
    const btn = document.getElementById("btn-proceed-analyze");
    if (btn) {
        btn.disabled = false;
        btn.classList.add("pulse-glow");
    }
}

function disableAnalysisButton() {
    const btn = document.getElementById("btn-proceed-analyze");
    if (btn) {
        btn.disabled = true;
        btn.classList.remove("pulse-glow");
    }
}

function showToast(message, duration = 3000) {
    const existing = document.querySelector(".toast-msg");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.className = "toast-msg";
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 400);
    }, duration);
}
