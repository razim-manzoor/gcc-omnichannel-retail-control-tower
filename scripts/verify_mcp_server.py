"""
Test verification script for Retail Control Tower MCP Server over stdio.
Sends JSON-RPC 2.0 messages (initialize, tools/list, tools/call) and validates output.
"""
import subprocess
import json
import sys

def verify_mcp():
    print("=" * 70)
    print("VERIFYING MODEL CONTEXT PROTOCOL (MCP) SERVER")
    print("=" * 70)

    proc = subprocess.Popen(
        [sys.executable, "mcp/duckdb_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {
            "jsonrpc": "2.0", 
            "id": 3, 
            "method": "tools/call", 
            "params": {"name": "get_executive_kpis", "arguments": {}}
        },
        {
            "jsonrpc": "2.0", 
            "id": 4, 
            "method": "tools/call", 
            "params": {"name": "simulate_markdown", "arguments": {"discount_pct": 0.15}}
        },
        {
            "jsonrpc": "2.0", 
            "id": 5, 
            "method": "tools/call", 
            "params": {"name": "get_stockout_alerts", "arguments": {"limit": 3}}
        }
    ]

    for req in requests:
        proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()
        line = proc.stdout.readline()
        resp = json.loads(line)

        req_id = resp.get("id")
        if req_id == 1:
            server_name = resp["result"]["serverInfo"]["name"]
            print(f"  [1] MCP Handshake: Server '{server_name}' initialized successfully")
        elif req_id == 2:
            tools = resp["result"]["tools"]
            tool_names = [t["name"] for t in tools]
            print(f"  [2] Tools Discovered ({len(tools)}): {', '.join(tool_names)}")
            assert len(tools) == 4, f"Expected 4 tools, got {len(tools)}"
        elif req_id == 3:
            content = json.loads(resp["result"]["content"][0]["text"])
            gross = content["gross_sales_aed"]
            margin_pct = content["gross_margin_pct"]
            print(f"  [3] Tool 'get_executive_kpis': Gross AED {gross:,.2f} | Margin {margin_pct}%")
            assert round(gross, 2) == 205230433.50, f"Unexpected gross sales: {gross}"
            assert round(margin_pct, 2) == 69.73, f"Unexpected margin %: {margin_pct}"
        elif req_id == 4:
            content = json.loads(resp["result"]["content"][0]["text"])
            lift = content["simulated_volume_lift_pct"]
            verdict = content["verdict"]
            print(f"  [4] Tool 'simulate_markdown' (15%): Volume Lift +{lift}% | Verdict: {verdict}")
            assert lift > 0, "Expected positive volume lift"
        elif req_id == 5:
            content = json.loads(resp["result"]["content"][0]["text"])
            print(f"  [5] Tool 'get_stockout_alerts': Returned {len(content)} critical stockout risks")
            assert len(content) > 0, "Expected stockout alerts"

    proc.stdin.close()
    proc.terminate()
    print("=" * 70)
    print("ALL MCP SERVER CHECKS PASSED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    verify_mcp()
