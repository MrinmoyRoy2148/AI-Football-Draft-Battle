/**
 * AI Football Battle - Draft Module
 * Step-by-Step Experience:
 * 1. Team Names Setup
 * 2. Animated 3D Coin Toss (Determines 1st Pick)
 * 3. Snake Draft with 3-Card Random Packs
 * 4. Formation Selection & Match Result Verification
 */

let allPlayersList = [];
let currentGameData = null;
let currentPosFilter = "ALL";
let currentSearchTerm = "";
let tossWinner = "A";
let activeRandomCandidates = [];
let isFullCatalogVisible = false;

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", async () => {
    initDraftUI();
    await loadInitialData();
});

function initDraftUI() {
    // Filter buttons for full catalog
    const filterButtons = document.querySelectorAll(".filter-btn");
    filterButtons.forEach(btn => {
        btn.addEventListener("click", (e) => {
            filterButtons.forEach(b => b.classList.remove("active"));
            e.target.classList.add("active");
            currentPosFilter = e.target.getAttribute("data-pos") || "ALL";
            renderPlayerCatalog();
        });
    });

    // Search bar for full catalog
    const searchInput = document.getElementById("player-search-input");
    searchInput?.addEventListener("input", (e) => {
        currentSearchTerm = e.target.value.toLowerCase().trim();
        renderPlayerCatalog();
    });
}

async function loadInitialData() {
    try {
        allPlayersList = await fetchAllPlayers();
    } catch (err) {
        showToast("Error loading catalog: " + err.message);
    }
}

/**
 * STEP 1: Proceed from Team Names to Coin Toss
 */
function proceedToTossStage() {
    const teamAName = document.getElementById("input-team-a-name")?.value.trim() || "Team Alpha";
    const teamBName = document.getElementById("input-team-b-name")?.value.trim() || "Team Beta";

    // Update labels on the coin and toss stage
    const coinLabelA = document.getElementById("coin-label-a");
    const coinLabelB = document.getElementById("coin-label-b");
    if (coinLabelA) coinLabelA.textContent = teamAName.toUpperCase();
    if (coinLabelB) coinLabelB.textContent = teamBName.toUpperCase();

    // Reset toss elements
    const flipper = document.getElementById("coin-flipper");
    if (flipper) {
        flipper.className = "coin-disc";
        flipper.style.transform = "rotateY(0deg)";
    }
    const resultBox = document.getElementById("toss-result-box");
    if (resultBox) resultBox.style.display = "none";
    const flipBtn = document.getElementById("btn-flip-coin");
    if (flipBtn) {
        flipBtn.disabled = false;
        flipBtn.style.display = "inline-flex";
    }

    // Switch view
    document.getElementById("draft-stage-setup").style.display = "none";
    document.getElementById("draft-stage-toss").style.display = "block";
    document.getElementById("draft-stage-arena").style.display = "none";

    window.scrollTo({ top: 0, behavior: "smooth" });
}

/**
 * STEP 2: Execute Animated 3D Coin Toss
 */
function executeCoinToss() {
    const flipBtn = document.getElementById("btn-flip-coin");
    if (flipBtn) flipBtn.disabled = true;

    const teamAName = document.getElementById("input-team-a-name")?.value.trim() || "Team Alpha";
    const teamBName = document.getElementById("input-team-b-name")?.value.trim() || "Team Beta";

    // Random winner: 50% chance
    tossWinner = Math.random() < 0.5 ? "A" : "B";
    const winningTeamName = tossWinner === "A" ? teamAName : teamBName;
    const losingTeamName = tossWinner === "A" ? teamBName : teamAName;

    const flipper = document.getElementById("coin-flipper");
    if (flipper) {
        flipper.classList.remove("coin-spinning-a", "coin-spinning-b");
        // Trigger CSS reflow
        void flipper.offsetWidth;
        flipper.classList.add(tossWinner === "A" ? "coin-spinning-a" : "coin-spinning-b");
    }

    // Display winner after 1.8s spin
    setTimeout(() => {
        if (flipBtn) flipBtn.style.display = "none";

        const resultBox = document.getElementById("toss-result-box");
        const heading = document.getElementById("toss-winner-heading");
        const desc = document.getElementById("toss-winner-desc");

        if (heading) heading.textContent = `🎉 ${winningTeamName} Won the Toss!`;
        if (desc) {
            desc.innerHTML = `<strong>${winningTeamName}</strong> earns the 1st pick in the draft.<br>` +
                             `<strong>${losingTeamName}</strong> will get 2 consecutive picks in round 2 (Snake Draft: 1-2-2-2-2-1).`;
        }

        if (resultBox) {
            resultBox.style.display = "block";
            resultBox.classList.add("fade-in");
        }
    }, 1800);
}

/**
 * STEP 3: Start Snake Draft Arena
 */
async function startDraftAfterToss() {
    const teamAName = document.getElementById("input-team-a-name")?.value.trim() || "Team Alpha";
    const teamBName = document.getElementById("input-team-b-name")?.value.trim() || "Team Beta";

    try {
        currentGameData = await createGameSession(
            teamAName,
            teamBName,
            "1-1-1-2",
            "1-1-1-2",
            tossWinner,
            "snake"
        );

        // Hide toss, reveal draft arena
        document.getElementById("draft-stage-toss").style.display = "none";
        document.getElementById("draft-stage-arena").style.display = "block";
        document.getElementById("draft-stage-formation-finish").style.display = "none";

        // Generate 3 random candidates
        generateNewRandomCandidates();
        renderFullDraftView();

        const firstTeamName = currentGameData.teams[tossWinner].name || `Team ${tossWinner}`;
        showToast(`⚔️ Draft Started! ${firstTeamName} makes the opening pick.`);
        window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
        showToast("Error creating game session: " + err.message);
    }
}

/**
 * Reset back to Stage 1 (Team Setup)
 */
function resetToTeamSetup() {
    currentGameData = null;
    tossWinner = "A";
    activeRandomCandidates = [];
    isFullCatalogVisible = false;

    document.getElementById("draft-stage-setup").style.display = "block";
    document.getElementById("draft-stage-toss").style.display = "none";
    document.getElementById("draft-stage-arena").style.display = "none";
    document.getElementById("draft-stage-formation-finish").style.display = "none";
    window.scrollTo({ top: 0, behavior: "smooth" });
}

/**
 * Deal 3 Random Undrafted Footballers
 */
function generateNewRandomCandidates() {
    if (!currentGameData || !allPlayersList || allPlayersList.length === 0) return;

    const draftedSet = new Set([
        ...currentGameData.teams.A.player_ids,
        ...currentGameData.teams.B.player_ids
    ]);

    const undrafted = allPlayersList.filter(p => !draftedSet.has(p.id));

    if (undrafted.length === 0) {
        activeRandomCandidates = [];
        renderRandomCandidates();
        return;
    }

    // Shuffle undrafted pool
    const shuffled = [...undrafted].sort(() => 0.5 - Math.random());
    activeRandomCandidates = shuffled.slice(0, Math.min(3, shuffled.length));

    renderRandomCandidates();
}

function shuffleRandomCandidates() {
    generateNewRandomCandidates();
    showToast("🔀 New 3 candidate footballers drawn!");
}

function toggleFullCatalogView() {
    const fullSec = document.getElementById("full-catalog-section");
    const toggleText = document.getElementById("toggle-catalog-text");
    if (!fullSec) return;

    isFullCatalogVisible = !isFullCatalogVisible;
    fullSec.style.display = isFullCatalogVisible ? "block" : "none";
    if (toggleText) {
        toggleText.textContent = isFullCatalogVisible ? "Hide Full Pool" : "Browse Full Pool";
    }

    if (isFullCatalogVisible) {
        renderPlayerCatalog();
    }
}

/**
 * Render 3 Random Candidate Cards
 */
function renderRandomCandidates() {
    const container = document.getElementById("random-candidates-grid");
    if (!container) return;

    container.innerHTML = "";

    if (currentGameData?.status === "completed") {
        container.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 24px; color: var(--accent-emerald);">
                <div style="font-size: 2rem;">✅</div>
                <div style="font-weight: 800; font-size: 1.1rem; margin-top: 6px;">Draft Phase Complete!</div>
                <p style="color: var(--text-muted); font-size: 0.9rem;">Both teams have drafted 5 superstars. Choose formations below to proceed.</p>
            </div>
        `;
        return;
    }

    const currentTurn = currentGameData?.current_turn || "A";
    const teamName = currentGameData?.teams[currentTurn]?.name || `Team ${currentTurn}`;
    const btnClass = currentTurn === "A" ? "btn-draft-a" : "btn-draft-b";

    // Update pack turn title
    const packTitle = document.getElementById("pack-turn-title");
    if (packTitle) {
        packTitle.innerHTML = `<span style="color: ${currentTurn === 'A' ? 'var(--team-a-accent)' : 'var(--team-b-accent)'}">${teamName}'s Pick</span>: Select 1 of 3 Footballers`;
    }

    activeRandomCandidates.forEach(player => {
        const card = document.createElement("div");
        card.className = "candidate-card";

        const posClass = `pos-${player.position.toLowerCase()}`;

        card.innerHTML = `
            <div class="candidate-header">
                <span class="pos-tag ${posClass}">${player.position}</span>
                <span class="candidate-ovr">${player.overall}</span>
            </div>
            <div class="candidate-name">${player.name}</div>
            <div class="candidate-bars-list">
                <div class="candidate-bar-item">
                    <span class="bar-lbl">ATT</span>
                    <div class="bar-track"><div class="bar-fill" style="width: ${player.attack}%; background: var(--accent-rose);"></div></div>
                    <span class="bar-num">${player.attack}</span>
                </div>
                <div class="candidate-bar-item">
                    <span class="bar-lbl">MID</span>
                    <div class="bar-track"><div class="bar-fill" style="width: ${player.midfield}%; background: var(--accent-emerald);"></div></div>
                    <span class="bar-num">${player.midfield}</span>
                </div>
                <div class="candidate-bar-item">
                    <span class="bar-lbl">DEF</span>
                    <div class="bar-track"><div class="bar-fill" style="width: ${player.defense}%; background: var(--accent-blue);"></div></div>
                    <span class="bar-num">${player.defense}</span>
                </div>
            </div>
            <button class="candidate-draft-btn ${btnClass}" onclick="handleSelectPlayer('${player.id}')" title="Draft ${player.name} for ${teamName}">
                <span>➕</span> Draft Player
            </button>
        `;

        container.appendChild(card);
    });
}

/**
 * Handle Drafting a Player
 */
async function handleSelectPlayer(playerId) {
    if (!currentGameData || currentGameData.status !== "drafting") {
        return;
    }

    try {
        currentGameData = await draftPlayerPick(currentGameData.game_id, playerId);

        if (currentGameData.status === "completed") {
            // Reveal formation selection and check result stage
            renderFullDraftView();
            showFormationFinishStage();
            showToast("🎉 Draft Complete! Both squads have 5 superstars. Set your formations below!", 4000);
        } else {
            // Deal 3 new candidate cards for next turn
            generateNewRandomCandidates();
            renderFullDraftView();
        }
    } catch (err) {
        showToast(err.message);
    }
}

/**
 * Reveal Step 4: Formation Selection
 */
function showFormationFinishStage() {
    const finishSec = document.getElementById("draft-stage-formation-finish");
    if (!finishSec) return;

    finishSec.style.display = "block";
    finishSec.classList.add("fade-in");

    const labelA = document.getElementById("form-label-a");
    const labelB = document.getElementById("form-label-b");
    if (labelA) labelA.textContent = `${currentGameData.teams.A.name || "Team Alpha"} Tactical Formation`;
    if (labelB) labelB.textContent = `${currentGameData.teams.B.name || "Team Beta"} Tactical Formation`;

    finishSec.scrollIntoView({ behavior: "smooth" });
}

/**
 * Check Match Winner & AI Analysis Action
 */
async function handleCheckMatchWinner() {
    if (!currentGameData) return;

    const formA = document.getElementById("select-form-a")?.value || "1-1-1-2";
    const formB = document.getElementById("select-form-b")?.value || "1-1-1-2";

    try {
        showToast("⚙️ Locking tactical formations...", 1500);
        await updateGameFormations(currentGameData.game_id, formA, formB);

        // Switch to Match Analysis screen and execute analysis
        switchTab("analysis");
        await triggerMatchAnalysis();

        showToast("🏆 Match Analyzed! Win probabilities and tactical AI report live.", 4000);
    } catch (err) {
        showToast("Error evaluating match: " + err.message);
    }
}

function renderFullDraftView() {
    if (!currentGameData) return;

    renderTurnStatus();
    renderTeamPanels();
    renderRandomCandidates();

    if (isFullCatalogVisible) {
        renderPlayerCatalog();
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

    const countA = document.getElementById("team-picks-count-a");
    const countB = document.getElementById("team-picks-count-b");
    if (countA) countA.textContent = `${currentGameData.teams.A.player_ids.length} / 5`;
    if (countB) countB.textContent = `${currentGameData.teams.B.player_ids.length} / 5`;

    if (currentGameData.status === "completed") {
        if (turnEl) turnEl.textContent = "Draft Complete - Ready for Tactical Formations & Analysis";
        if (dotEl) {
            dotEl.className = "turn-pulse-dot";
            dotEl.style.background = "#10b981";
            dotEl.style.boxShadow = "0 0 15px #10b981";
        }
        return;
    }

    const currentTurn = currentGameData.current_turn;
    const teamName = currentGameData.teams[currentTurn].name || `Team ${currentTurn}`;

    // Calculate snake round status (e.g. pick 1 of 2 in a row)
    const turnNumber = draftedCount + 1;
    let turnDetail = "";
    if (currentGameData.draft_mode === "snake" && currentGameData.draft_order) {
        const order = currentGameData.draft_order;
        const currentInOrder = order[draftedCount];
        const nextInOrder = draftedCount + 1 < order.length ? order[draftedCount + 1] : null;
        const prevInOrder = draftedCount > 0 ? order[draftedCount - 1] : null;

        if (currentInOrder === nextInOrder) {
            turnDetail = " (Pick 1 of 2 consecutive)";
        } else if (currentInOrder === prevInOrder) {
            turnDetail = " (Pick 2 of 2 consecutive)";
        }
    }

    if (turnEl) turnEl.textContent = `Turn ${turnNumber}/10: ${teamName}'s Pick${turnDetail}`;
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
    const rosterListEl = document.getElementById(`roster-list-${teamKey.toLowerCase()}`);

    if (titleEl) titleEl.textContent = teamObj.name || `Team ${teamKey}`;

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
                    <span class="roster-slot-empty">Awaiting pick...</span>
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

// Instant Quick Match Demo triggered from Landing Page
async function quickStartDemoMatch() {
    showToast("⚡ Initializing Instant Match Demo...", 2500);

    try {
        if (!allPlayersList || allPlayersList.length === 0) {
            allPlayersList = await fetchAllPlayers();
        }

        currentGameData = await createGameSession(
            "Galácticos Alpha",
            "Legends Beta",
            "1-1-1-2",
            "1-1-1-2",
            "A",
            "alternating"
        );

        const demoDraftPicks = [
            "P001", "P002",
            "P006", "P007",
            "P014", "P015",
            "P023", "P024",
            "P025", "P026"
        ];

        for (const pid of demoDraftPicks) {
            currentGameData = await draftPlayerPick(currentGameData.game_id, pid);
        }

        renderFullDraftView();

        switchTab("analysis");
        await triggerMatchAnalysis();

        showToast("🌟 Instant Match Demo Active! AI Tactical Breakdown is live.", 4000);
    } catch (err) {
        showToast("Quick Match Demo Error: " + err.message);
    }
}
