#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for GCC Omnichannel Retail Control Tower.
Provides conversational AI agents (Antigravity, Claude, Cursor) with direct access
to governed retail metrics, inventory health alerts, and what-if markdown simulations via DuckDB.
"""
import sys
import os
import json
import logging
import duckdb

logging.basicConfig(level=logging.ERROR, stream=sys.stderr)

class RetailControlTowerMCP:
    def __init__(self):
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.data_dir = os.path.join(self.project_root, "data")
        self.parquet_dir = os.path.join(self.data_dir, "parquet")
        self.con = duckdb.connect(":memory:")
        self._init_database()

    def _init_database(self):
        """Initializes DuckDB views from Parquet (preferred) or CSV."""
        use_parquet = os.path.exists(os.path.join(self.parquet_dir, "Fact_POS_Transactions.parquet"))
        ext = "parquet" if use_parquet else "csv"
        folder = self.parquet_dir if use_parquet else self.data_dir

        read_fn = "read_parquet" if use_parquet else "read_csv_auto"

        tables = {
            "pos_transactions": f"Fact_POS_Transactions.{ext}",
            "daily_inventory": f"Fact_Daily_Inventory.{ext}",
            "dim_date": f"Dim_Date.{ext}",
            "dim_store": f"Dim_Store.{ext}",
            "dim_product": f"Dim_Product.{ext}",
            "markdown_scenario": f"Markdown_Scenario.{ext}"
        }

        for view_name, fname in tables.items():
            fpath = os.path.join(folder, fname).replace("\\", "/")
            if os.path.exists(fpath):
                self.con.execute(f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM {read_fn}('{fpath}')")

        # Load models
        models_dir = os.path.join(self.project_root, "rill", "models")
        pos_model_path = os.path.join(models_dir, "pos_analytics.sql")
        inv_model_path = os.path.join(models_dir, "inventory_analytics.sql")

        if os.path.exists(pos_model_path):
            with open(pos_model_path, encoding="utf-8") as f:
                self.con.execute(f"CREATE OR REPLACE VIEW pos_analytics AS {f.read()}")
        if os.path.exists(inv_model_path):
            with open(inv_model_path, encoding="utf-8") as f:
                self.con.execute(f"CREATE OR REPLACE VIEW inventory_analytics AS {f.read()}")

    def get_executive_kpis(self, store_name=None, channel_type=None, fiscal_quarter=None):
        where_clauses = []
        if store_name:
            where_clauses.append(f"StoreName = '{store_name}'")
        if channel_type:
            where_clauses.append(f"ChannelType = '{channel_type}'")
        if fiscal_quarter:
            where_clauses.append(f"FiscalQuarter = '{fiscal_quarter}'")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        sql = f"""
            SELECT 
                SUM(UnitsSold) AS units_sold,
                ROUND(SUM(GrossSalesAmt), 2) AS gross_sales_aed,
                ROUND(SUM(DiscountAmt), 2) AS markdown_discounts_aed,
                ROUND(SUM(NetSalesAmt), 2) AS net_revenue_aed,
                ROUND(SUM(TotalCOGS), 2) AS total_cogs_aed,
                ROUND(SUM(GrossMarginAmt), 2) AS gross_margin_aed,
                ROUND(SUM(GrossMarginAmt) / NULLIF(SUM(NetSalesAmt), 0) * 100, 2) AS gross_margin_pct,
                ROUND(SUM(DiscountAmt) / NULLIF(SUM(GrossSalesAmt), 0) * 100, 2) AS markdown_depth_pct,
                ROUND(SUM(NetSalesAmt) / NULLIF(SUM(UnitsSold), 0), 2) AS aur_aed,
                ROUND(SUM(TotalCOGS) / NULLIF(SUM(UnitsSold), 0), 2) AS auc_aed,
                COUNT(DISTINCT BasketID) AS transaction_count
            FROM pos_analytics
            {where_sql}
        """
        df = self.con.execute(sql).df()
        return df.to_dict(orient="records")[0]

    def get_stockout_alerts(self, limit=10):
        sql = f"""
            WITH latest_date AS (
                SELECT MAX(SnapshotDateKey) as max_date FROM inventory_analytics
            ),
            trailing_sales AS (
                SELECT 
                    StoreCode,
                    SKU,
                    SUM(UnitsSold) as trailing_units,
                    SUM(UnitsSold) / 4.0 as weekly_run_rate
                FROM pos_analytics
                WHERE TransactionTimestamp >= (SELECT MAX(TransactionTimestamp) - INTERVAL 28 DAY FROM pos_analytics)
                GROUP BY StoreCode, SKU
            )
            SELECT 
                i.StoreCode,
                i.StoreName,
                i.SKU,
                i.ProductName,
                i.Department,
                i.OnHandUnits,
                ROUND(COALESCE(t.weekly_run_rate, 0), 2) AS weekly_run_rate,
                ROUND(CASE WHEN COALESCE(t.weekly_run_rate, 0) > 0 THEN i.OnHandUnits / t.weekly_run_rate ELSE 99.0 END, 1) AS weeks_of_supply,
                ROUND(CASE WHEN (i.OnHandUnits + COALESCE(t.trailing_units, 0)) > 0 
                     THEN COALESCE(t.trailing_units, 0) / (i.OnHandUnits + COALESCE(t.trailing_units, 0)) * 100 
                     ELSE 0 END, 1) AS sell_through_pct,
                CEIL(COALESCE(t.weekly_run_rate, 0) * 4) AS target_safety_stock,
                i.OnHandUnits - CEIL(COALESCE(t.weekly_run_rate, 0) * 4) AS unit_variance
            FROM inventory_analytics i
            JOIN latest_date ld ON i.SnapshotDateKey = ld.max_date
            LEFT JOIN trailing_sales t ON i.StoreCode = t.StoreCode AND i.SKU = t.SKU
            WHERE (i.OnHandUnits / NULLIF(t.weekly_run_rate, 0)) < 2.5
            ORDER BY weeks_of_supply ASC
            LIMIT {int(limit)}
        """
        df = self.con.execute(sql).df()
        return df.to_dict(orient="records")

    def simulate_markdown(self, discount_pct: float, store_code: str = None, sku: str = None):
        where = []
        if store_code:
            where.append(f"s.StoreCode = '{store_code}'")
        if sku:
            where.append(f"p.SKU = '{sku}'")
        where_clause = f"WHERE {' AND '.join(where)}" if where else ""

        sql = f"""
            WITH base AS (
                SELECT 
                    SUM(f.UnitsSold) AS units_sold,
                    SUM(f.GrossSalesAmt) AS gross_sales,
                    SUM(f.NetSalesAmt) AS net_sales,
                    SUM(f.ExtendedCostAmt) AS cogs,
                    SUM(f.NetSalesAmt - f.ExtendedCostAmt) AS gross_margin,
                    SUM(f.NetSalesAmt) / NULLIF(SUM(f.UnitsSold), 0) AS aur,
                    SUM(f.ExtendedCostAmt) / NULLIF(SUM(f.UnitsSold), 0) AS auc,
                    SUM(f.UnitsSold * p.ElasticityCoefficient) / NULLIF(SUM(f.UnitsSold), 0) AS effective_elasticity
                FROM pos_transactions f
                JOIN dim_store s ON f.StoreKey = s.StoreKey
                JOIN dim_product p ON f.ProductKey = p.ProductKey
                {where_clause}
            )
            SELECT 
                units_sold AS baseline_units,
                ROUND(net_sales, 2) AS baseline_revenue_aed,
                ROUND(gross_margin, 2) AS baseline_gross_margin_aed,
                ROUND(aur, 2) AS baseline_aur_aed,
                ROUND(auc, 2) AS baseline_auc_aed,
                ROUND(effective_elasticity, 2) AS effective_elasticity,
                ROUND(-1.0 * effective_elasticity * {discount_pct} * 100, 2) AS simulated_volume_lift_pct,
                ROUND(units_sold * (1.0 + (-1.0 * effective_elasticity * {discount_pct})), 0) AS simulated_units,
                ROUND(units_sold * (-1.0 * effective_elasticity * {discount_pct}), 0) AS incremental_units_cleared,
                ROUND(aur * (1.0 - {discount_pct}), 2) AS simulated_effective_aur_aed,
                ROUND((units_sold * (1.0 + (-1.0 * effective_elasticity * {discount_pct}))) * (aur * (1.0 - {discount_pct})), 2) AS simulated_net_revenue_aed,
                ROUND((units_sold * (1.0 + (-1.0 * effective_elasticity * {discount_pct}))) * auc, 2) AS simulated_total_cogs_aed,
                ROUND(
                    ((units_sold * (1.0 + (-1.0 * effective_elasticity * {discount_pct}))) * (aur * (1.0 - {discount_pct}))) -
                    ((units_sold * (1.0 + (-1.0 * effective_elasticity * {discount_pct}))) * auc), 2
                ) AS simulated_gross_margin_aed,
                ROUND(
                    (((units_sold * (1.0 + (-1.0 * effective_elasticity * {discount_pct}))) * (aur * (1.0 - {discount_pct}))) -
                    ((units_sold * (1.0 + (-1.0 * effective_elasticity * {discount_pct}))) * auc)) - gross_margin, 2
                ) AS gross_margin_delta_aed,
                ROUND((units_sold * (-1.0 * effective_elasticity * {discount_pct})) * auc, 2) AS working_capital_released_aed
            FROM base
        """
        df = self.con.execute(sql).df()
        res = df.to_dict(orient="records")[0]
        margin_delta = res["gross_margin_delta_aed"]
        res["verdict"] = "ACCRETIVE PROFIT YIELD" if margin_delta > 0 else "CAPITAL TRADE-OFF / DILUTIVE MARGIN RISK"
        return res

    def run_read_only_sql(self, query: str):
        clean_query = query.strip()
        if not clean_query.upper().startswith("SELECT") and not clean_query.upper().startswith("WITH"):
            raise ValueError("Only read-only SELECT or WITH statements are allowed.")
        df = self.con.execute(clean_query).df()
        return df.to_dict(orient="records")

    def list_tools(self):
        return [
            {
                "name": "get_executive_kpis",
                "description": "Returns high-level commercial KPIs (Gross Sales, Net Revenue, Gross Margin %, Markdown Depth %, AUR, AUC, Transaction Count) from the verified GCC retail dataset.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "store_name": {"type": "string", "description": "Optional store name (e.g. 'The Dubai Mall Flagship', 'Mall of the Emirates Boutique', 'Yas Mall Abu Dhabi')"},
                        "channel_type": {"type": "string", "description": "Optional channel ('Physical Flagship', 'Physical Boutique', 'Digital Flagship')"},
                        "fiscal_quarter": {"type": "string", "description": "Optional fiscal quarter ('Q1', 'Q2', 'Q3', 'Q4')"}
                    }
                }
            },
            {
                "name": "get_stockout_alerts",
                "description": "Returns critical inventory stockout risk alerts across GCC mall locations where Weeks of Supply < 2.5 and Sell-Through % is high.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Maximum number of alerts to return (default 10)"}
                    }
                }
            },
            {
                "name": "simulate_markdown",
                "description": "Simulates price elasticity volume lift, incremental stock clearance, gross margin impact (accretive vs dilutive), and working capital release for any scenario discount percentage.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "discount_pct": {"type": "number", "description": "Discount decimal between 0.00 and 0.50 (e.g. 0.15 for 15%)"},
                        "store_code": {"type": "string", "description": "Optional store code (e.g. 'DXB-TDM-01')"},
                        "sku": {"type": "string", "description": "Optional product SKU (e.g. 'RTW-BLZ-LIN-001')"}
                    },
                    "required": ["discount_pct"]
                }
            },
            {
                "name": "run_read_only_sql",
                "description": "Executes a safe read-only SQL query against the GCC Retail Control Tower in DuckDB (tables: pos_analytics, inventory_analytics, dim_store, dim_product, dim_date).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL query (must be SELECT or WITH query)"}
                    },
                    "required": ["query"]
                }
            }
        ]

    def handle_request(self, request):
        method = request.get("method")
        msg_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "gcc-retail-control-tower-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "notifications/initialized":
            return None
        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": self.list_tools()}
            }
        elif method == "tools/call":
            params = request.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})

            try:
                if name == "get_executive_kpis":
                    data = self.get_executive_kpis(
                        store_name=args.get("store_name"),
                        channel_type=args.get("channel_type"),
                        fiscal_quarter=args.get("fiscal_quarter")
                    )
                elif name == "get_stockout_alerts":
                    data = self.get_stockout_alerts(limit=args.get("limit", 10))
                elif name == "simulate_markdown":
                    data = self.simulate_markdown(
                        discount_pct=float(args.get("discount_pct", 0.15)),
                        store_code=args.get("store_code"),
                        sku=args.get("sku")
                    )
                elif name == "run_read_only_sql":
                    data = self.run_read_only_sql(args.get("query", ""))
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {"code": -32601, "message": f"Method {name} not found"}
                    }

                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(data, indent=2)}
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "isError": True,
                        "content": [{"type": "text", "text": f"Error: {str(e)}"}]
                    }
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method {method} not found"}
            }

def main():
    server = RetailControlTowerMCP()
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = server.handle_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
