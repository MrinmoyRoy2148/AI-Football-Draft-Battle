/**
 * AI Football Battle - What-If Strategy Lab Module
 * Simulates tactical swaps and formation changes without altering actual game state.
 */

document.addEventListener("DOMContentLoaded", () => {
    initWhatIfUI();
});

function initWhatIfUI() {
    const teamSelect = document.getElementById("whatif-select-team");
    teamSelect?.addEventListener("change", populateWhatIfPlayerSelectors);

    document.getElementById("btn-run-whatif")?.addEventListener("click", handleExecuteWhatIf);
    document.getElementById("btn-reset-whatif")?.addEventListener("click", resetWhatIfResults);
    document.getElementById("btn-back-to-analysis")?.addEventListener("click", () => switchTab("analysis"));
}

function prepareWhatIfLab() {
    if (!currentGameData) return;
    populateWhatIfPlayerSelectors();
}

function populateWhatIfPlayerSelectors() {
    if (!currentGameData) return;

    const teamKey = document.getElementById("whatif-select-team")?.value || "A";
    const targetTeam = currentGameData.teams[teamKey];

    const outSelect = document.getElementById("whatif-select-out");
    const inSelect = document.getElementById("whatif-select-in");

    if (!outSelect || !inSelect) return;

    outSelect.innerHTML = "";
    inSelect.innerHTML = "";

    const playerMap = new Map(allPlayersList.map(p => [p.id, p]));

    // Populate Outgoing Players (players in targetTeam)
    targetTeam.player_ids.forEach(pid => {
        const p = playerMap.get(pid);
        if (p) {
            const opt = document.createElement("option");
            opt.value = p.id;
            opt.textContent = `${p.name} (${p.position}) - OVR: ${p.overall}`;
            outSelect.appendChild(opt);
        }
    });

    // Populate Incoming Players (any player NOT in Team A or Team B)
    const takenIds = new Set([
        ...currentGameData.teams.A.player_ids,
        ...currentGameData.teams.B.player_ids
    ]);

    allPlayersList.forEach(p => {
        if (!takenIds.has(p.id)) {
            const opt = document.createElement("option");
            opt.value = p.id;
            opt.textContent = `${p.name} (${p.position}) - OVR: ${p.overall}`;
            inSelect.appendChild(opt);
        }
    });

    // If no undrafted players available (rare edge case), inform user
    if (inSelect.children.length === 0) {
        const opt = document.createElement("option");
        opt.value = "";
        opt.textContent = "No undrafted players available";
        inSelect.appendChild(opt);
    }
}

async function handleExecuteWhatIf() {
    if (!currentGameData) return;

    const teamId = document.getElementById("whatif-select-team")?.value;
    const playerOut = document.getElementById("whatif-select-out")?.value;
    const playerIn = document.getElementById("whatif-select-in")?.value;
    const formation = document.getElementById("whatif-select-form")?.value;

    if (!playerOut || !playerIn) {
        showToast("Please select both an outgoing and replacement footballer.");
        return;
    }

    const loader = document.getElementById("whatif-loading-state");
    const resultsContainer = document.getElementById("whatif-results-container");

    if (loader) loader.style.display = "block";
    if (resultsContainer) resultsContainer.style.display = "none";

    try {
        const response = await simulateWhatIfStrategy(
            currentGameData.game_id,
            teamId,
            playerOut,
            playerIn,
            formation
        );

        renderWhatIfResults(response);
        if (loader) loader.style.display = "none";
        if (resultsContainer) resultsContainer.style.display = "block";
    } catch (err) {
        if (loader) loader.style.display = "none";
        showToast("What-If Simulation Failed: " + err.message);
    }
}

function renderWhatIfResults(data) {
    const { results, ai_analysis } = data;
    const origStats = results.original_stats;
    const hypoStats = results.hypothetical_stats;
    const targetTeamId = results.target_team_id;

    const tKey = `team_${targetTeamId.toLowerCase()}_win`;
    const origProb = results.original_probabilities[tKey];
    const hypoProb = results.hypothetical_probabilities[tKey];

    // Probability delta
    const probDelta = results.probability_delta;
    const strDelta = results.strength_delta;

    // Delta Pill Element
    const deltaPill = document.getElementById("whatif-delta-pill");
    if (deltaPill) {
        const isPos = probDelta > 0;
        const isNeg = probDelta < 0;
        deltaPill.className = `delta-badge ${isPos ? 'delta-positive' : isNeg ? 'delta-negative' : 'delta-neutral'}`;
        deltaPill.textContent = `${probDelta >= 0 ? '+' : ''}${probDelta.toFixed(2)}% Win Chance (${strDelta >= 0 ? '+' : ''}${strDelta.toFixed(2)} Strength)`;
    }

    // Original Stats Card
    document.getElementById("whatif-orig-name").textContent = origStats.team_name;
    document.getElementById("whatif-orig-prob").textContent = `${origProb}%`;
    document.getElementById("whatif-orig-str").textContent = origStats.strength.toFixed(1);
    document.getElementById("whatif-orig-att").textContent = origStats.attack.toFixed(1);
    document.getElementById("whatif-orig-mid").textContent = origStats.midfield.toFixed(1);
    document.getElementById("whatif-orig-def").textContent = origStats.defense.toFixed(1);
    document.getElementById("whatif-orig-bal").textContent = origStats.balance.toFixed(1);

    // Hypothetical Stats Card
    document.getElementById("whatif-hypo-name").textContent = `${hypoStats.team_name} (Simulated)`;
    document.getElementById("whatif-hypo-prob").textContent = `${hypoProb}%`;
    document.getElementById("whatif-hypo-str").textContent = hypoStats.strength.toFixed(1);
    document.getElementById("whatif-hypo-att").textContent = hypoStats.attack.toFixed(1);
    document.getElementById("whatif-hypo-mid").textContent = hypoStats.midfield.toFixed(1);
    document.getElementById("whatif-hypo-def").textContent = hypoStats.defense.toFixed(1);
    document.getElementById("whatif-hypo-bal").textContent = hypoStats.balance.toFixed(1);

    // AI Analysis Commentary
    const explanationBox = document.getElementById("whatif-ai-explanation");
    if (explanationBox) {
        explanationBox.textContent = ai_analysis;
    }
}

function resetWhatIfResults() {
    const resultsContainer = document.getElementById("whatif-results-container");
    if (resultsContainer) resultsContainer.style.display = "none";
    populateWhatIfPlayerSelectors();
    showToast("What-If parameters reset.");
}
