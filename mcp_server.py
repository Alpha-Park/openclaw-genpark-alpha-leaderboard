# -*- coding: utf-8 -*-
import sys, json
from client import OpenClawGenParkAlphaLeaderboard

client = OpenClawGenParkAlphaLeaderboard()

TOOLS = [
    {
        "name": "update_trueskill_ratings",
        "description": "Updates Bayesian TrueSkill mu and sigma for two agents following a match.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "player1": {"type": "object"},
                "player2": {"type": "object"},
                "outcome": {"type": "number"},
                "beta": {"type": "number"}
            },
            "required": ["player1", "player2", "outcome"]
        }
    },
    {
        "name": "calculate_match_quality",
        "description": "Calculates competitive match quality between two agents.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "player1": {"type": "object"},
                "player2": {"type": "object"},
                "beta": {"type": "number"}
            },
            "required": ["player1", "player2"]
        }
    },
    {
        "name": "detect_collusion_sybils",
        "description": "Detects anomalous pairwise win-farming collusion patterns between agents.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "match_history": {"type": "array", "items": {"type": "object"}},
                "win_rate_threshold": {"type": "number"}
            },
            "required": ["match_history"]
        }
    }
]

def handle_request(req):
    method = req.get("method")
    rid = req.get("id")
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    elif method == "tools/call":
        params = req.get("params", {})
        tname = params.get("name")
        args = params.get("arguments", {})
        if tname == "update_trueskill_ratings":
            res = client.update_trueskill_ratings(args["player1"], args["player2"], args["outcome"], args.get("beta"))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "calculate_match_quality":
            res = client.calculate_match_quality(args["player1"], args["player2"], args.get("beta"))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "detect_collusion_sybils":
            res = client.detect_collusion_sybils(args["match_history"], args.get("win_rate_threshold", 0.90))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32600, "message": "Invalid Request"}}

def main():
    for line in sys.stdin:
        if not line.strip(): continue
        try:
            try:
                req = json.loads(line)
            except json.JSONDecodeError as exc:
                print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}), flush=True)
                continue
            if not isinstance(req, dict) or req.get("jsonrpc") != "2.0" or not isinstance(req.get("method"), str):
                print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request"}}), flush=True)
                continue
            # JSON-RPC notifications never receive a response or execute request-only tools.
            if "id" not in req:
                continue
            if req["method"] == "initialize":
                print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "result": {
                    "protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                    "serverInfo": {"name": 'openclaw-genpark-alpha-leaderboard', "version": "1.0.0"}
                }}), flush=True)
                continue
            if req["method"] == "ping":
                print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "result": {}}), flush=True)
                continue
            if req["method"] not in ("tools/list", "tools/call"):
                print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "error": {"code": -32601, "message": "Method not found"}}), flush=True)
                continue
            if req["method"] == "tools/call":
                params = req.get("params")
                if not isinstance(params, dict) or not isinstance(params.get("arguments", {}), dict) or params.get("name") not in ('update_trueskill_ratings', 'calculate_match_quality', 'detect_collusion_sybils'):
                    print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "error": {"code": -32602, "message": "Unknown tool or invalid arguments"}}), flush=True)
                    continue
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req.get("id") if isinstance(req, dict) else None, "error": {"code": -32700, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
