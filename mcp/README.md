# 🤖 Model Context Protocol (MCP) — Retail Control Tower

This directory exposes the **GCC Omnichannel Retail Control Tower** to conversational AI agents (Antigravity, Claude Desktop, Cursor) via the open **Model Context Protocol (MCP)**.

---

## 🛠️ Available MCP Tools

| Tool Name | Parameters | Purpose |
| :--- | :--- | :--- |
| `get_executive_kpis` | `store_name`, `channel_type`, `fiscal_quarter` | Returns certified commercial KPIs: Gross Sales, Net Revenue, COGS, Gross Margin %, Markdown Depth %, AUR, AUC, and Transaction Count. |
| `get_stockout_alerts` | `limit` (default 10) | Identifies real-time critical stockout risks across GCC malls where Weeks of Supply < 2.5 and Sell-Through % is elevated. |
| `simulate_markdown` | `discount_pct` (e.g. `0.15`), `store_code`, `sku` | Projects elasticity-driven volume lift %, incremental stock liquidation, Gross Margin Delta AED, and commercial verdict (Accretive vs Dilutive). |
| `run_read_only_sql` | `query` (must be `SELECT` or `WITH`) | Executes safe, sub-millisecond DuckDB SQL queries over parquet/CSV tables. |

---

## 🚀 How to Connect

### Option 1: Claude Desktop / Cursor / Antigravity MCP Config
Add this entry to your `claude_desktop_config.json` or Antigravity configuration:

```json
{
  "mcpServers": {
    "retail-control-tower": {
      "command": "python",
      "args": [
        "R:/Projects/Omnichannel Retail Control Tower/mcp/duckdb_mcp_server.py"
      ]
    }
  }
}
```

### Option 2: Verify MCP Server Locally
Run the automated test harness:
```powershell
python scripts/verify_mcp_server.py
```
Outputs:
- Handshake & tool discovery (`tools/list`)
- Execution tests for KPIs, Markdown Simulation, and Stockout Alerts over `stdio`.
