"""
Embedded FastAPI Analytical Microservice for GCC Omnichannel Retail Control Tower.
High-performance REST API powered by DuckDB in-memory columnar engine.
Interactive Swagger documentation available at: http://localhost:8000/docs
"""
import os
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import duckdb

app = FastAPI(
    title="GCC Omnichannel Retail Control Tower API",
    version="1.0.0",
    description="Operational retail analytics microservice providing sub-10ms queries for financial KPIs, inventory health alerts, and price elasticity simulations."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database singleton
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
PARQUET_DIR = os.path.join(DATA_DIR, "parquet")

db = duckdb.connect(":memory:")

def init_db():
    use_parquet = os.path.exists(os.path.join(PARQUET_DIR, "Fact_POS_Transactions.parquet"))
    ext = "parquet" if use_parquet else "csv"
    folder = PARQUET_DIR if use_parquet else DATA_DIR
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
            db.execute(f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM {read_fn}('{fpath}')")

    models_dir = os.path.join(PROJECT_ROOT, "rill", "models")
    pos_model = os.path.join(models_dir, "pos_analytics.sql")
    inv_model = os.path.join(models_dir, "inventory_analytics.sql")

    if os.path.exists(pos_model):
        with open(pos_model, encoding="utf-8") as f:
            db.execute(f"CREATE OR REPLACE VIEW pos_analytics AS {f.read()}")
    if os.path.exists(inv_model):
        with open(inv_model, encoding="utf-8") as f:
            db.execute(f"CREATE OR REPLACE VIEW inventory_analytics AS {f.read()}")

init_db()

# Request / Response Schemas
class KPIResponse(BaseModel):
    units_sold: int
    gross_sales_aed: float
    markdown_discounts_aed: float
    net_revenue_aed: float
    total_cogs_aed: float
    gross_margin_aed: float
    gross_margin_pct: float
    markdown_depth_pct: float
    aur_aed: float
    auc_aed: float
    transaction_count: int

class StockoutAlert(BaseModel):
    store_code: str
    store_name: str
    sku: str
    product_name: str
    department: str
    on_hand_units: int
    weekly_run_rate: float
    weeks_of_supply: float
    sell_through_pct: float
    target_safety_stock: int
    unit_variance: int
    rebalance_directive: str

class MarkdownSimulationRequest(BaseModel):
    discount_pct: float = Field(0.15, ge=0.0, le=0.50, description="Discount percentage (e.g., 0.15 for 15%)")
    store_code: Optional[str] = Field(None, description="Optional store code (e.g. DXB-TDM-01)")
    sku: Optional[str] = Field(None, description="Optional product SKU")

class MarkdownSimulationResponse(BaseModel):
    discount_pct: float
    baseline_units: int
    baseline_revenue_aed: float
    baseline_gross_margin_aed: float
    baseline_aur_aed: float
    baseline_auc_aed: float
    effective_elasticity: float
    simulated_volume_lift_pct: float
    simulated_units: int
    incremental_units_cleared: int
    simulated_effective_aur_aed: float
    simulated_net_revenue_aed: float
    simulated_total_cogs_aed: float
    simulated_gross_margin_aed: float
    gross_margin_delta_aed: float
    working_capital_released_aed: float
    verdict: str

class StoreInfo(BaseModel):
    store_key: int
    store_code: str
    store_name: str
    channel: str
    emirate: str
    country: str
    cluster_tier: str
    hub_fulfillment_eligible: bool

@app.get("/", tags=["Overview"])
def read_root():
    return {
        "title": "GCC Omnichannel Retail Control Tower API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "endpoints": {
            "kpis": "/api/kpis",
            "stockouts": "/api/inventory/stockouts",
            "simulation": "/api/simulation/markdown",
            "stores": "/api/stores",
            "health": "/health"
        }
    }

@app.get("/health", tags=["System"])
def health_check():
    row_count = db.execute("SELECT COUNT(*) FROM pos_analytics").fetchone()[0]
    return {
        "status": "healthy",
        "database_engine": "DuckDB In-Memory Columnar",
        "verified_pos_records": row_count
    }

@app.get("/api/kpis", response_model=KPIResponse, tags=["Commercial KPIs"])
def get_kpis(
    store_code: Optional[str] = Query(None, description="Filter by store code (e.g., DXB-TDM-01)"),
    channel_type: Optional[str] = Query(None, description="Filter by channel (e.g., Physical Flagship)"),
    fiscal_quarter: Optional[str] = Query(None, description="Filter by fiscal quarter (e.g., Q1, Q2)")
):
    where = []
    if store_code:
        where.append(f"StoreCode = '{store_code}'")
    if channel_type:
        where.append(f"ChannelType = '{channel_type}'")
    if fiscal_quarter:
        where.append(f"FiscalQuarter = '{fiscal_quarter}'")

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    sql = f"""
        SELECT 
            CAST(SUM(UnitsSold) AS BIGINT) AS units_sold,
            ROUND(SUM(GrossSalesAmt), 2) AS gross_sales_aed,
            ROUND(SUM(DiscountAmt), 2) AS markdown_discounts_aed,
            ROUND(SUM(NetSalesAmt), 2) AS net_revenue_aed,
            ROUND(SUM(TotalCOGS), 2) AS total_cogs_aed,
            ROUND(SUM(GrossMarginAmt), 2) AS gross_margin_aed,
            ROUND(SUM(GrossMarginAmt) / NULLIF(SUM(NetSalesAmt), 0) * 100, 2) AS gross_margin_pct,
            ROUND(SUM(DiscountAmt) / NULLIF(SUM(GrossSalesAmt), 0) * 100, 2) AS markdown_depth_pct,
            ROUND(SUM(NetSalesAmt) / NULLIF(SUM(UnitsSold), 0), 2) AS aur_aed,
            ROUND(SUM(TotalCOGS) / NULLIF(SUM(UnitsSold), 0), 2) AS auc_aed,
            CAST(COUNT(DISTINCT BasketID) AS BIGINT) AS transaction_count
        FROM pos_analytics
        {where_sql}
    """
    row = db.execute(sql).fetchone()
    if not row or row[0] is None:
        raise HTTPException(status_code=404, detail="No transaction data found for specified filter.")

    return KPIResponse(
        units_sold=row[0],
        gross_sales_aed=row[1],
        markdown_discounts_aed=row[2],
        net_revenue_aed=row[3],
        total_cogs_aed=row[4],
        gross_margin_aed=row[5],
        gross_margin_pct=row[6],
        markdown_depth_pct=row[7],
        aur_aed=row[8],
        auc_aed=row[9],
        transaction_count=row[10]
    )

@app.get("/api/inventory/stockouts", response_model=List[StockoutAlert], tags=["Supply Chain & Inventory"])
def get_stockouts(limit: int = Query(10, ge=1, le=100)):
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
            CAST(i.OnHandUnits AS INT) AS on_hand_units,
            ROUND(COALESCE(t.weekly_run_rate, 0), 2) AS weekly_run_rate,
            ROUND(CASE WHEN COALESCE(t.weekly_run_rate, 0) > 0 THEN i.OnHandUnits / t.weekly_run_rate ELSE 99.0 END, 1) AS weeks_of_supply,
            ROUND(CASE WHEN (i.OnHandUnits + COALESCE(t.trailing_units, 0)) > 0 
                 THEN COALESCE(t.trailing_units, 0) / (i.OnHandUnits + COALESCE(t.trailing_units, 0)) * 100 
                 ELSE 0 END, 1) AS sell_through_pct,
            CAST(CEIL(COALESCE(t.weekly_run_rate, 0) * 4) AS INT) AS target_safety_stock,
            CAST(i.OnHandUnits - CEIL(COALESCE(t.weekly_run_rate, 0) * 4) AS INT) AS unit_variance
        FROM inventory_analytics i
        JOIN latest_date ld ON i.SnapshotDateKey = ld.max_date
        LEFT JOIN trailing_sales t ON i.StoreCode = t.StoreCode AND i.SKU = t.SKU
        WHERE (i.OnHandUnits / NULLIF(t.weekly_run_rate, 0)) < 2.5
        ORDER BY weeks_of_supply ASC
        LIMIT {limit}
    """
    rows = db.execute(sql).fetchall()
    results = []
    for r in rows:
        variance = r[10]
        results.append(StockoutAlert(
            store_code=r[0],
            store_name=r[1],
            sku=r[2],
            product_name=r[3],
            department=r[4],
            on_hand_units=r[5],
            weekly_run_rate=r[6],
            weeks_of_supply=r[7],
            sell_through_pct=r[8],
            target_safety_stock=r[9],
            unit_variance=variance,
            rebalance_directive=f"⚠️ PULL INVENTORY: Deficit of {abs(variance)} units. Rebalance from Regional DC."
        ))
    return results

@app.post("/api/simulation/markdown", response_model=MarkdownSimulationResponse, tags=["Markdown Simulation"])
def simulate_markdown(req: MarkdownSimulationRequest):
    where = []
    if req.store_code:
        where.append(f"s.StoreCode = '{req.store_code}'")
    if req.sku:
        where.append(f"p.SKU = '{req.sku}'")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    discount = req.discount_pct

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
            {where_sql}
        )
        SELECT 
            CAST(units_sold AS BIGINT) AS baseline_units,
            ROUND(net_sales, 2) AS baseline_revenue,
            ROUND(gross_margin, 2) AS baseline_margin,
            ROUND(aur, 2) AS baseline_aur,
            ROUND(auc, 2) AS baseline_auc,
            ROUND(effective_elasticity, 2) AS elasticity,
            ROUND(-1.0 * effective_elasticity * {discount} * 100, 2) AS lift_pct,
            CAST(ROUND(units_sold * (1.0 + (-1.0 * effective_elasticity * {discount})), 0) AS BIGINT) AS sim_units,
            CAST(ROUND(units_sold * (-1.0 * effective_elasticity * {discount}), 0) AS BIGINT) AS extra_units,
            ROUND(aur * (1.0 - {discount}), 2) AS sim_aur,
            ROUND((units_sold * (1.0 + (-1.0 * effective_elasticity * {discount}))) * (aur * (1.0 - {discount})), 2) AS sim_rev,
            ROUND((units_sold * (1.0 + (-1.0 * effective_elasticity * {discount}))) * auc, 2) AS sim_cogs,
            ROUND(
                ((units_sold * (1.0 + (-1.0 * effective_elasticity * {discount}))) * (aur * (1.0 - {discount}))) -
                ((units_sold * (1.0 + (-1.0 * effective_elasticity * {discount}))) * auc), 2
            ) AS sim_margin,
            ROUND(
                (((units_sold * (1.0 + (-1.0 * effective_elasticity * {discount}))) * (aur * (1.0 - {discount}))) -
                ((units_sold * (1.0 + (-1.0 * effective_elasticity * {discount}))) * auc)) - gross_margin, 2
            ) AS margin_delta,
            ROUND((units_sold * (-1.0 * effective_elasticity * {discount})) * auc, 2) AS capital_released
        FROM base
    """
    row = db.execute(sql).fetchone()
    if not row or row[0] is None:
        raise HTTPException(status_code=404, detail="No base data found for markdown simulation.")

    margin_delta = row[13]
    verdict = "ACCRETIVE PROFIT YIELD" if margin_delta > 0 else "CAPITAL TRADE-OFF / DILUTIVE MARGIN RISK"

    return MarkdownSimulationResponse(
        discount_pct=discount,
        baseline_units=row[0],
        baseline_revenue_aed=row[1],
        baseline_gross_margin_aed=row[2],
        baseline_aur_aed=row[3],
        baseline_auc_aed=row[4],
        effective_elasticity=row[5],
        simulated_volume_lift_pct=row[6],
        simulated_units=row[7],
        incremental_units_cleared=row[8],
        simulated_effective_aur_aed=row[9],
        simulated_net_revenue_aed=row[10],
        simulated_total_cogs_aed=row[11],
        simulated_gross_margin_aed=row[12],
        gross_margin_delta_aed=margin_delta,
        working_capital_released_aed=row[14],
        verdict=verdict
    )

@app.get("/api/stores", response_model=List[StoreInfo], tags=["Dimension Metadata"])
def list_stores():
    sql = """
        SELECT 
            StoreKey,
            StoreCode,
            StoreName,
            Channel,
            Emirate,
            Country,
            ClusterTier,
            HubFulfillmentEligible
        FROM dim_store
        WHERE StoreKey > 0
        ORDER BY StoreKey ASC
    """
    rows = db.execute(sql).fetchall()
    return [
        StoreInfo(
            store_key=r[0],
            store_code=r[1],
            store_name=r[2],
            channel=r[3],
            emirate=r[4],
            country=r[5],
            cluster_tier=r[6],
            hub_fulfillment_eligible=bool(r[7])
        )
        for r in rows
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
