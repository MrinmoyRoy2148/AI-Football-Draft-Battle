import json
from app.engine.player_tools import get_player_stats
from app.engine.team_analyzer import analyze_team
from app.engine.team_comparator import compare_teams
from app.engine.probability import calculate_win_probability

# Allowlisted tool schemas for OpenAI function-calling
AGENT_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_player_stats",
            "description": "Retrieves the exact numerical ratings (attack, midfield, defense, overall, position) for a player ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "player_id": {"type": "string", "description": "Unique identifier of the player (e.g. 'P001')"}
                },
                "required": ["player_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_team",
            "description": "Computes normalized attack, midfield, defense, balance, and composite strength for a 5-player roster.",
            "parameters": {
                "type": "object",
                "properties": {
                    "player_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of exactly five unique player IDs"
                    },
                    "formation": {
                        "type": "string",
                        "description": "Tactical formation string, e.g. '1-1-1-2'"
                    }
                },
                "required": ["player_ids"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_teams",
            "description": "Compares two complete 5-player teams across all deterministic dimensions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_a_ids": {"type": "array", "items": {"type": "string"}},
                    "team_b_ids": {"type": "array", "items": {"type": "string"}},
                    "formation_a": {"type": "string"},
                    "formation_b": {"type": "string"}
                },
                "required": ["team_a_ids", "team_b_ids"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_win_probability",
            "description": "Calculates winning probabilities based on the deterministic team strength values using the logistic model.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_a_strength": {"type": "number"},
                    "team_b_strength": {"type": "number"}
                },
                "required": ["team_a_strength", "team_b_strength"]
            }
        }
    }
]

def execute_tool_call(tool_name: str, arguments_json: str) -> str:
    """Safely executes an allowlisted analytical tool and returns JSON string."""
    try:
        args = json.loads(arguments_json) if arguments_json else {}
        if tool_name == "get_player_stats":
            return json.dumps(get_player_stats(args.get("player_id", "")))
        elif tool_name == "analyze_team":
            return json.dumps(analyze_team(args.get("player_ids", []), args.get("formation", "1-1-1-2")))
        elif tool_name == "compare_teams":
            return json.dumps(compare_teams(
                args.get("team_a_ids", []),
                args.get("team_b_ids", []),
                args.get("formation_a", "1-1-1-2"),
                args.get("formation_b", "1-1-1-2")
            ))
        elif tool_name == "calculate_win_probability":
            return json.dumps(calculate_win_probability(
                {"strength": args.get("team_a_strength", 0.0)},
                {"strength": args.get("team_b_strength", 0.0)}
            ))
        else:
            return json.dumps({"error": f"Tool '{tool_name}' is not in the allowlist"})
    except Exception as e:
        return json.dumps({"error": str(e)})
