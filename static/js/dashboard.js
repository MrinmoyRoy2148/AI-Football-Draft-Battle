/**
 * AI Football Battle - Match Analysis Dashboard Module
 * Visualizes deterministic comparisons, win probabilities, and AI Analyst commentary.
 */

let currentAnalysisData = null;

async function triggerMatchAnalysis() {
    if (!currentGameData) return;

    const loader = document.getElementById("analysis-loading-state");
    const content = document.getElementById("analysis-content-state");
    if (loader) loader.style.display = "block";
    if (content) content.style.display = "none";

    try {
        currentAnalysisData = await analyzeMatch(currentGameData.game_id);
        renderAnalysisDashboard(currentAnalysisData);
        if (loader) loader.style.display = "none";
        if (content) content.style.display = "block";
    } catch (err) {
        if (loader) loader.style.display = "none";
        showToast("Analysis Error: " + err.message);
    }
}

function renderAnalysisDashboard(data) {
    const { comparison, probabilities, ai_analysis } = data;
    const statsA = comparison.team_a_stats;
    const statsB = comparison.team_b_stats;

    // 1. Win Probability Bar
    const probPctA = probabilities.team_a_win;
    const probPctB = probabilities.team_b_win;

    const probElA = document.getElementById("prob-val-a");
    const probElB = document.getElementById("prob-val-b");
    const nameElA = document.getElementById("prob-name-a");
    const nameElB = document.getElementById("prob-name-b");
    const barFillA = document.getElementById("prob-bar-fill-a");

    if (probElA) probElA.textContent = `${probPctA}%`;
    if (probElB) probElB.textContent = `${probPctB}%`;
    if (nameElA) nameElA.textContent = statsA.team_name;
    if (nameElB) nameElB.textContent = statsB.team_name;
    if (barFillA) barFillA.style.width = `${probPctA}%`;

    // 2. Metrics Rows
    renderMetricRow("att", statsA.attack, statsB.attack);
    renderMetricRow("mid", statsA.midfield, statsB.midfield);
    renderMetricRow("def", statsA.defense, statsB.defense);
    renderMetricRow("ovr", statsA.overall, statsB.overall);
    renderMetricRow("bal", statsA.balance, statsB.balance);
    renderMetricRow("str", statsA.strength, statsB.strength);

    // 3. AI Game Analyst Commentary
    const sourceBadge = document.getElementById("ai-analyst-source-badge");
    const summaryBox = document.getElementById("ai-analyst-summary");
    const boxTeamA = document.getElementById("ai-analyst-team-a");
    const boxTeamB = document.getElementById("ai-analyst-team-b");
    const matchupsBox = document.getElementById("ai-analyst-matchups");
    const verdictBox = document.getElementById("ai-analyst-verdict");

    const titleTeamA = document.getElementById("ai-title-team-a");
    const titleTeamB = document.getElementById("ai-title-team-b");
    if (titleTeamA) titleTeamA.textContent = `${statsA.team_name} Tactical Assessment`;
    if (titleTeamB) titleTeamB.textContent = `${statsB.team_name} Tactical Assessment`;

    if (sourceBadge) {
        if (ai_analysis.source === "llm") {
            sourceBadge.className = "ai-source-badge ai-source-llm";
            sourceBadge.innerHTML = "<span>🤖</span> Live LLM Agent";
        } else {
            sourceBadge.className = "ai-source-badge ai-source-fallback";
            sourceBadge.innerHTML = "<span>⚡</span> Heuristic Tactical Engine";
        }
    }

    // Always use textContent for AI text as specified in blueprint
    if (summaryBox) summaryBox.textContent = ai_analysis.summary;
    if (boxTeamA) boxTeamA.textContent = ai_analysis.team_a_assessment;
    if (boxTeamB) boxTeamB.textContent = ai_analysis.team_b_assessment;
    if (matchupsBox) matchupsBox.textContent = ai_analysis.key_matchups;
    if (verdictBox) verdictBox.textContent = ai_analysis.tactical_verdict;
}

function renderMetricRow(prefix, valA, valB) {
    const valElA = document.getElementById(`metric-val-a-${prefix}`);
    const valElB = document.getElementById(`metric-val-b-${prefix}`);
    const fillElA = document.getElementById(`metric-fill-a-${prefix}`);
    const fillElB = document.getElementById(`metric-fill-b-${prefix}`);

    if (valElA) valElA.textContent = valA.toFixed(1);
    if (valElB) valElB.textContent = valB.toFixed(1);

    // Values are 0-100 normalized
    if (fillElA) fillElA.style.width = `${Math.min(100, Math.max(0, valA))}%`;
    if (fillElB) fillElB.style.width = `${Math.min(100, Math.max(0, valB))}%`;
}
