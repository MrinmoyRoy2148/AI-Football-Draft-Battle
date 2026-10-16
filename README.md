# AI Football Battle: Two-Player Draft & AI Game Analyst

**Course:** Artificial Intelligence Sessional — CSE 3202  
**Project Type:** AI-Enhanced Full-Stack Web Application  
**Technology Stack:** Python • FastAPI • HTML • CSS • JavaScript • JSON • LLM API  

---

## 1. Project Overview & Abstract

**AI Football Battle** is an interactive, browser-based two-player football team-building game. Two human players alternately draft five-player squads from a static dataset of 32 world-class footballers. 

The application strictly separates **numerical calculation** from **natural-language explanation**:
1. **Deterministic Python Engine**: Authoritatively calculates position-weighted category ratings (Attack, Midfield, Defense), average overall, tactical team balance, composite team strength, and win probability using a logistic sigmoid model ($k = 12.0$).
2. **AI Football Game Analyst Agent**: A goal-based agent providing decision-oriented tactical commentary. It interprets structured game states, explains strengths and vulnerabilities, pinpoints key midfield and defensive matchups, and evaluates hypothetical substitutions in the **What-If Strategy Lab**.
3. **Resilient Fallback Mode**: If an LLM API key (`OPENAI_API_KEY`) is absent or offline, an intelligent deterministic heuristic analyst seamlessly generates structured tactical commentary without interrupting the user experience.

---

## 2. PEAS Specification

| Element | Specification |
| :--- | :--- |
| **Performance Measure** | Enforce drafting rules (alternating turns, exactly 5 players per team, no duplicates), calculate deterministic statistics, produce mathematically consistent win probabilities (summing to 100%), and generate AI commentary consistent with the mathematical ground truth. |
| **Environment** | A browser-based football drafting game played by two players on the same machine. Includes 32 curated players, rosters, formations, live team statistics, winning probabilities, and hypothetical What-If game states. Partially observable to the AI agent (only accesses structured game states via analytical tools); discrete, multi-agent, sequential, and mostly deterministic. |
| **Actuators** | Web browser UI displaying available footballer pool, live team rosters, turn status banner, comparative radar/bar metrics, win probability meter, AI analyst commentary, and What-If comparison diffs. |
| **Sensors** | Human player draft clicks, team name inputs, formation choices, JSON dataset, calculated team metrics, and user What-If requests. |

---

## 3. Mathematical & Deterministic Formulations

### Category Normalized Ratings
Each position has dedicated category weights for **Attack**, **Midfield**, and **Defense**:
- **GK**: $(0.10, 0.10, 0.80)$
- **DEF**: $(0.20, 0.25, 0.55)$
- **MID**: $(0.30, 0.50, 0.20)$
- **FWD**: $(0.65, 0.25, 0.10)$

$$A_{\text{team}} = \frac{\sum_{i=1}^{n} (\text{Attack}_i \times w_{\text{att}, i})}{\sum w_{\text{att}}}, \quad M_{\text{team}} = \frac{\sum_{i=1}^{n} (\text{Midfield}_i \times w_{\text{mid}, i})}{\sum w_{\text{mid}}}, \quad D_{\text{team}} = \frac{\sum_{i=1}^{n} (\text{Defense}_i \times w_{\text{def}, i})}{\sum w_{\text{def}}}$$

$$\text{Overall}_{\text{team}} = \frac{1}{n} \sum_{i=1}^{n} \text{Overall}_i$$

### Team Balance Formula
Clamped to the interval $[0, 100]$:
$$\text{Balance} = 100 - \frac{|A - M| + |M - D| + |D - A|}{3}$$

### Composite Team Strength Formula
$$\text{Strength} = 0.35 \times A_{\text{team}} + 0.30 \times M_{\text{team}} + 0.25 \times D_{\text{team}} + 0.10 \times \text{Balance}$$

### Logistic Win Probability
$$\Delta \text{Strength} = \text{Strength}_A - \text{Strength}_B, \quad k = 12.0$$
$$P(A) = \frac{1}{1 + e^{-\frac{\Delta \text{Strength}}{k}}}, \quad P(B) = 1 - P(A)$$

---

## 4. System Architecture & Folder Structure

```text
ai-football-battle/
├── app/
│   ├── main.py                  # FastAPI server, static/template mounting, CORS
│   ├── config.py                # App configuration, weights, constants
│   ├── api/
│   │   ├── draft.py             # /api/players, /api/game/create, /api/draft
│   │   ├── analysis.py          # /api/analyze
│   │   └── what_if.py           # /api/what-if
│   ├── models/
│   │   ├── player.py            # Player Pydantic model
│   │   ├── game.py              # Team, GameState, DraftRequest models
│   │   └── analysis.py          # TeamStats, TeamComparison, AIAnalysis models
│   ├── services/
│   │   ├── game_state.py        # In-memory session store & life-cycle
│   │   ├── draft_service.py     # Authoritative turn switching & rules enforcement
│   │   └── analyst_service.py   # Analytical orchestration & agent query
│   ├── engine/
│   │   ├── player_tools.py      # Player catalog lookup
│   │   ├── team_analyzer.py     # Deterministic stat calculations
│   │   ├── team_comparator.py   # Head-to-head delta comparisons
│   │   ├── probability.py       # Logistic win probability
│   │   └── what_if_engine.py    # Isolated copy simulation
│   └── agent/
│       ├── prompts.py           # System prompt & structured JSON templates
│       ├── tools.py             # Allowlisted tool definitions
│       └── llm_client.py        # LLM dispatcher + intelligent fallback engine
├── data/
│   └── players.json             # Static dataset of 32 footballers (GK, DEF, MID, FWD)
├── static/
│   ├── css/
│   │   └── style.css            # Dark arena glassmorphism design system
│   └── js/
│       ├── api.js               # Reusable Fetch API abstraction
│       ├── draft.js             # Drafting board & turn manager
│       ├── dashboard.js         # Match analysis visualizer
│       └── what_if.js           # What-If simulator UI
├── templates/
│   └── index.html               # Semantic single-page HTML interface
├── tests/
│   ├── test_engine.py           # Engine & mathematical validation tests
│   ├── test_draft.py            # Alternating draft mechanics tests
│   ├── test_what_if.py          # What-If isolation & non-mutation tests
│   └── test_api.py              # Full FastAPI HTTP integration tests
├── .env.example                 # Environment variables template
├── .gitignore                   # Excludes venv, pycache, .env
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

---

## 5. Setup & Execution Instructions

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Modern web browser (Chrome, Edge, Firefox)

### 1. Installation
Clone or navigate to the repository directory and install the requirements:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional for Live LLM)
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
To enable live OpenAI commentary, edit `.env`:
```ini
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```
> *Note: If no API key is specified, the application automatically uses the built-in Intelligent Heuristic Analyst Engine, ensuring 100% functionality without paid credentials.*

### 3. Run Automated Tests
```bash
python -m pytest
```
*Expected: 13 passed tests verifying engine bounds, draft rules, What-If isolation, and API routes.*

### 4. Start the Application
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open your browser and navigate to:
**`http://127.0.0.1:8000`**

Interactive API documentation (Swagger UI) is available at:
**`http://127.0.0.1:8000/docs`**

---

## 6. Lab Defense & Viva Q&A

### Q1: What is the PEAS specification in your project?
- **Performance Measure**: Correct draft rule enforcement, deterministic stat calculations, mathematically consistent win probabilities, and ground-truth-aligned AI explanations.
- **Environment**: Two-player browser game on a single machine, static dataset of 32 players, active rosters, and What-If states.
- **Actuators**: UI displays for draft rosters, turn indicators, stat bars, win probability gauge, and AI commentary.
- **Sensors**: Human click selections, team configurations, player JSON dataset, calculated metrics, and What-If requests.

### Q2: Why is the AI Game Analyst modeled as a goal-based agent rather than a simple reflex agent?
A simple reflex agent acts solely on immediate condition-action rules without evaluating team composition or consequences. In football team drafting, a player substitution cannot be evaluated in isolation: introducing a world-class striker might improve attack but undermine midfield balance and lower winning probability. The goal-based agent considers the full game state, runs analytical comparisons, and reasons toward evaluating strategic utility.

### Q3: Why is a deterministic engine used for math instead of the LLM?
LLMs are probabilistic language models that can hallucinate numbers, miscalculate formulas, or produce non-reproducible probabilities. Python provides authoritative numerical ground truth, ensuring that identical squad inputs always yield exact, mathematically valid statistics. The LLM's role is strictly confined to natural-language reasoning and strategic explanation.

### Q4: How does tool calling work in the architecture?
The agent architecture includes an allowlist of deterministic analytical functions (`get_player_stats`, `analyze_team`, `compare_teams`, `calculate_win_probability`). The model requests an allowed tool by name with arguments, the backend securely executes the corresponding Python function, and returns structured JSON back to the agent. The LLM cannot execute arbitrary code or alter game state.

### Q5: How does What-If Strategy demonstrate decision support?
The What-If engine clones the active roster into an isolated temporary copy, executes a hypothetical substitution or tactical formation switch, recalculates original and hypothetical statistics side-by-side, and generates an AI comparative breakdown. This empowers users to evaluate risk versus reward before committing decisions, proving that the real match state remains completely unmutated.
