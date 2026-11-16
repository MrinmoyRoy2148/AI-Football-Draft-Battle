/**
 * AI Football Battle - API Client
 * Clean reusable fetch interface communicating with FastAPI endpoints.
 */

const API_BASE = "/api";

async function apiRequest(endpoint, method = "GET", data = null) {
    const options = {
        method: method,
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    };

    if (data && (method === "POST" || method === "PUT")) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const result = await response.json();

        if (!response.ok) {
            const errorMsg = result.detail || result.message || "An error occurred during request";
            throw new Error(errorMsg);
        }

        return result;
    } catch (err) {
        console.error(`API Error on [${method} ${endpoint}]:`, err);
        throw err;
    }
}

// Player catalog
async function fetchAllPlayers() {
    return await apiRequest("/players", "GET");
}

// Game session management
async function createGameSession(teamAName = "Team Alpha", teamBName = "Team Beta", formationA = "1-1-1-2", formationB = "1-1-1-2", firstTurn = "A", draftMode = "snake") {
    return await apiRequest("/game/create", "POST", {
        team_a_name: teamAName,
        team_b_name: teamBName,
        formation_a: formationA,
        formation_b: formationB,
        first_turn: firstTurn,
        draft_mode: draftMode
    });
}

async function updateGameFormations(gameId, formationA, formationB) {
    return await apiRequest(`/game/${gameId}/formation`, "POST", {
        formation_a: formationA,
        formation_b: formationB
    });
}

async function fetchGameState(gameId) {
    return await apiRequest(`/game/${gameId}`, "GET");
}

async function resetGameSession(gameId) {
    return await apiRequest(`/game/${gameId}/reset`, "POST");
}

// Drafting
async function draftPlayerPick(gameId, playerId) {
    return await apiRequest("/draft", "POST", {
        game_id: gameId,
        player_id: playerId
    });
}

// Match Analysis
async function analyzeMatch(gameId) {
    return await apiRequest("/analyze", "POST", {
        game_id: gameId
    });
}

// What-If Strategy
async function simulateWhatIfStrategy(gameId, teamId, playerOutId, playerInId, formation = null) {
    return await apiRequest("/what-if", "POST", {
        game_id: gameId,
        team_id: teamId,
        player_out: playerOutId,
        player_in: playerInId,
        formation: formation
    });
}
