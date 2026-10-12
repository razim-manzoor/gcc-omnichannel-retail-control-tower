# ⚙️ Technical Requirements & Architecture Document (TRD)
## GCC Omnichannel Retail & Markdown Elasticity Control Tower

**Document Version:** 1.0.0  
**Target Engine:** Microsoft Tabular / VertiPaq, DuckDB, Apache Parquet, FastAPI, Rill, MCP  
**Project Repository:** `gcc-omnichannel-retail-control-tower`

---

## 1. System Architecture Overview

The GCC Omnichannel Retail Control Tower implements a **Tri-Layer Analytical Architecture** engineered for sub-10ms query execution, mathematical rigor, and dual human/AI consumption:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. LAKEHOUSE STORAGE & SYNTHESIS LAYER                                                │
│    • Synthetic Data Engine (Python 3.12, NumPy, Pandas, Faker)                         │
│    • Raw Star Schema CSVs (data/*.csv)                                                 │
│    • Snappy-Compressed Columnar Lakehouse Storage (data/parquet/*.parquet)             │
│    • Storage Efficiency: 10.74 MB -> 4.24 MB (60.5% reduction)                         │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. IN-MEMORY OLAP & SEMANTIC ENGINES                                                   │
│    • Power BI VertiPaq Tabular Engine (43 Production Measures in model.bim / DAX)     │
│    • DuckDB Vectorized In-Memory OLAP Engine (Sub-10ms Columnar Aggregations)          │
│    • Rill Developer BI-as-Code Declarative Metrics Layer (rill/)                      │
│    • Invariant Test Suite & Mathematical Parity Gate (scripts/audit_everything.py)     │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. MULTI-MODAL DELIVERY & CONSUMPTION LAYER                                            │
│    • C-Suite Executive Web UI: Responsive Bento-Grid Dashboard (web/index.html)        │
│    • Enterprise Tabular BI: Power BI Desktop & Service Publish-to-Web                  │
│    • REST Analytical API: FastAPI Microservice with OpenAPI Swagger UI (api/main.py)   │
│    • Conversational AI Interface: Model Context Protocol (MCP) Server (mcp/)          │
│    • CI/CD Quality Assurance: Automated GitHub Actions Pipeline (.github/workflows/)   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Kimball Dimensional Star Schema Architecture

The data warehouse strictly adheres to **Ralph Kimball's Dimensional Modeling standards**. All facts connect directly to dimensions via integer surrogate keys with **1-to-Many single-direction relationships** to eliminate ambiguous circular filter paths and bidirectional cross-filter penalties.

```
                   ┌────────────────────────┐
                   │        Dim_Date        │
                   │────────────────────────│
                   │ PK  DateKey (Int)      │
                   │     FullDate           │
                   │     FiscalYear         │
                   │     FiscalQuarter      │
                   │     FiscalMonthName    │
                   │     RetailWeekNum      │
                   │     IsWeekendGCC       │
                   │     IsRetailPeakSeason │
                   └───────────┬────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            │ 1:M                                 │ 1:M
            ▼                                     ▼
┌───────────────────────────┐         ┌───────────────────────────┐
│   Fact_POS_Transactions   │         │   Fact_Daily_Inventory    │
│───────────────────────────│         │───────────────────────────│
│ PK  TransactionLineKey    │         │ PK  InventorySnapshotKey  │
│ FK  DateKey               │         │ FK  SnapshotDateKey       │
│ FK  StoreKey              │         │ FK  StoreKey              │
│ FK  ProductKey            │         │ FK  ProductKey            │
│     BasketID              │         │     OnHandUnits           │
│     UnitsSold             │         │     InTransitUnits        │
│     GrossSalesAmt         │         │     ReservedUnits         │
│     DiscountAmt           │         │     AvailableUnits        │
│     NetSalesAmt           │         │     UnitCostSnapshotAmt   │
│     ExtendedCostAmt       │         │     InventoryCostValueAmt │
│     TaxAmtAED             │         └───────────▲───────────────┘
└───────────▲───────────────┘                     │
            │                                     │
            ├──────────────────┬──────────────────┤
            │ 1:M              │ 1:M              │
            │                  │                  │
┌───────────┴───────────┐      │      ┌───────────┴───────────┐
│       Dim_Store       │      │      │      Dim_Product      │
│───────────────────────│      │      │───────────────────────│
│ PK  StoreKey (Int)    │◄─────┘      │ PK  ProductKey (Int)  │
│     StoreCode         │             │     SKU               │
│     StoreName         │             │     ProductName       │
│     Channel           │             │     Department        │
│     Emirate / City    │             │     Category          │
│     Country           │             │     SubCategory       │
│     ClusterTier       │             │     BrandTier         │
│     HubFulfillment    │             │     BaseRetailPrice   │
└───────────────────────┘             │     BaseUnitCost      │
                                      │     ElasticityCoeff   │
                                      └───────────────────────┘
```

### 2.1 Table Schema Specifications

| Table Name | Granularity | Row Count | Primary Key | Foreign Keys | Role / Notes |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `Fact_POS_Transactions` | Line item per transaction | 115,008 | `TransactionLineKey` | `DateKey`, `StoreKey`, `ProductKey` | Transactional sales fact with additive prices, discounts, and costs. |
| `Fact_Daily_Inventory` | Store-Product per day | 53,808 | `InventorySnapshotKey` | `SnapshotDateKey`, `StoreKey`, `ProductKey` | Semi-additive periodic snapshot fact recording closing stock balances. |
| `Dim_Date` | Calendar day (2025–2026) | 731 | `DateKey` (YYYYMMDD) | None | Full GCC retail calendar (Ramadan, DSF, Friday-Sunday weekends). |
| `Dim_Store` | Retail location / channel | 9 | `StoreKey` | None | 8 active GCC locations + `-1 Unknown` surrogate key member. |
| `Dim_Product` | Luxury retail SKU | 115 | `ProductKey` | None | 114 active SKUs + `-1 Unknown` surrogate key member. Includes price elasticity. |
| `Markdown_Scenario` | Disconnected parameter | 11 | `ScenarioDiscountPct` | None | Disconnected table (0.00 to 0.50 in 5% increments) for What-If parameter harvesting. |

---

## 3. Mathematical Foundations & Semantic Calculation Architecture

### 3.1 Financial & Commercial Core (Folder 01)
- **Net Realized Revenue:**
  $$\text{Net Revenue} = \sum(\text{Fact\_POS\_Transactions}[\text{NetSalesAmt}])$$
  *Invariant Check:* $\text{NetSalesAmt} = \text{GrossSalesAmt} - \text{DiscountAmt}$
- **Gross Margin (AED):**
  $$\text{Gross Margin} = \text{Net Revenue} - \text{Total COGS}$$
- **Gross Margin %:**
  $$\text{Gross Margin \%} = \frac{\text{Gross Margin}}{\text{Net Revenue}} = \mathbf{69.73\%}$$
- **Average Unit Retail (AUR) & Average Unit Cost (AUC):**
  $$\text{AUR} = \frac{\text{Net Revenue}}{\text{Units Sold}} = \mathbf{\text{AED } 1,350.91}, \quad \text{AUC} = \frac{\text{Total COGS}}{\text{Units Sold}} = \mathbf{\text{AED } 408.90}$$

### 3.2 Semi-Additive Inventory Logic (Folder 02)
Unlike transaction facts, inventory balances cannot be summed across dates. The calculation uses strict point-in-time snapshot filtering:
```dax
[Ending On Hand Units] = 
VAR LastAvailableDate = MAX ( Dim_Date[FullDate] )
VAR TargetDateKey = 
    YEAR ( LastAvailableDate ) * 10000 
    + MONTH ( LastAvailableDate ) * 100 
    + DAY ( LastAvailableDate )
RETURN
    CALCULATE (
        SUM ( Fact_Daily_Inventory[OnHandUnits] ),
        Fact_Daily_Inventory[SnapshotDateKey] = TargetDateKey,
        REMOVEFILTERS ( Dim_Date )
    )
```

### 3.3 Asset Productivity & Forward Stock Cover (Folder 03)
- **Sell-Through Rate (STR %):**
  $$\text{STR \%} = \frac{\text{Units Sold}}{\text{Units Sold} + \text{Ending On-Hand Units}}$$
- **Trailing 4-Week Run Rate & Weeks of Supply (WOS):**
  $$\text{Weekly Sales Run Rate} = \frac{\text{Units Sold Trailing 28 Days}}{4}$$
  $$\text{Weeks of Supply (WOS)} = \frac{\text{Ending On Hand Units}}{\text{Weekly Sales Run Rate}}$$
- **GMROI (Gross Margin Return on Investment):**
  $$\text{GMROI} = \frac{\text{Annualized Gross Margin}}{\text{Average Inventory Landed Cost}}$$

### 3.4 Prescriptive Stock Balancing Directives (Folder 05)
The engine evaluates velocity divergence to trigger automated operational instructions:
```dax
[Stock Health Classification] = 
SWITCH (
    TRUE (),
    ISBLANK ( [Weeks of Supply] ), "NO_VELOCITY",
    [Sell-Through Rate %] >= 0.70 && [Weeks of Supply] < 2.5, "CRITICAL_STOCKOUT_RISK",
    [Sell-Through Rate %] <= 0.25 && [Weeks of Supply] > 10.0, "OVERSTOCK_CASH_TRAP",
    [Weeks of Supply] >= 3.0 && [Weeks of Supply] <= 6.0, "BALANCED_EQUILIBRIUM",
    "ATTENTION_MONITOR"
)
```

### 3.5 What-If Elasticity Simulator (Folder 06)
1. **Effective Elasticity Coefficient:**
   $$\varepsilon_{\text{eff}} = \frac{\sum(\text{UnitsSold} \times \text{ElasticityCoefficient})}{\sum\text{UnitsSold}}$$
2. **Projected Volume Lift %:**
   $$\text{Lift \%} = -1 \times (\varepsilon_{\text{eff}} \times \Delta_{\text{discount}})$$
3. **Simulated Units & Revenue:**
   $$\text{Units}_{\text{sim}} = \text{Units}_{\text{base}} \times (1 + \text{Lift \%})$$
   $$\text{AUR}_{\text{sim}} = \text{AUR}_{\text{base}} \times (1 - \Delta_{\text{discount}})$$
   $$\text{Net Revenue}_{\text{sim}} = \text{Units}_{\text{sim}} \times \text{AUR}_{\text{sim}}$$
4. **P&L Variance & Working Capital Released:**
   $$\Delta \text{Gross Margin} = (\text{Net Revenue}_{\text{sim}} - \text{COGS}_{\text{sim}}) - \text{Gross Margin}_{\text{base}}$$
   $$\text{Working Capital Released} = (\text{Units}_{\text{sim}} - \text{Units}_{\text{base}}) \times \text{AUC}_{\text{base}}$$
5. **Breakeven Hurdle:**
   $$\text{Breakeven Unit Volume} = \frac{\text{Gross Margin}_{\text{base}}}{\text{AUR}_{\text{sim}} - \text{AUC}_{\text{base}}}$$

---

## 4. Lakehouse Storage & Columnar Optimization (Parquet)

To transition the data architecture to modern lakehouse standards, raw CSVs are converted to **Snappy-compressed Apache Parquet** via DuckDB (`scripts/convert_to_parquet.py`):

```sql
COPY (SELECT * FROM read_csv_auto('data/Fact_POS_Transactions.csv'))
TO 'data/parquet/Fact_POS_Transactions.parquet' (FORMAT PARQUET, COMPRESSION SNAPPY);
```

### Storage & Throughput Benchmarks

| Metric | Raw CSV Layer | Parquet Lakehouse Layer | Efficiency Gain |
| :--- | :---: | :---: | :---: |
| **Total Storage Size** | 10.74 MB | **4.24 MB** | **60.5% space reduction** |
| **Full Aggregation Time** | 109.98 ms | **7.33 ms** | **15.01x faster** |
| **Column-Pruned Scan Time** | 100.61 ms | **3.52 ms** | **28.55x faster** |
| **Filtered Slice Query Time**| 106.09 ms | **7.48 ms** | **14.18x faster** |

---

## 5. REST API Microservice Specification (FastAPI)

- **Entrypoint:** `api/main.py`
- **Port:** `8000` (Swagger UI at `http://localhost:8000/docs`)
- **Engine:** DuckDB In-Memory singleton reading Parquet/CSV on startup.

### Core Endpoints

| Method | Route | Description | Query / Body Params | Response DTO |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service health & verified row counter | None | `{status: "healthy", verified_pos_records: 115008}` |
| `GET` | `/api/kpis` | Aggregated commercial metrics | `store_code`, `channel_type`, `fiscal_quarter` | `KPIResponse` (Gross, Net, Margin %, AUR, AUC) |
| `GET` | `/api/inventory/stockouts` | Critical stockout risk alerts | `limit` (int, default 10) | `List[StockoutAlert]` with rebalance directives |
| `POST` | `/api/simulation/markdown` | What-If price elasticity simulation | `{"discount_pct": float, "store_code": str, "sku": str}` | `MarkdownSimulationResponse` with P&L delta & verdict |
| `GET` | `/api/stores` | Dimension metadata for GCC nodes | None | `List[StoreInfo]` |

---

## 6. Model Context Protocol (MCP) Server Architecture

- **Entrypoint:** `mcp/duckdb_mcp_server.py`
- **Protocol:** Model Context Protocol (MCP v2024-11-05) via JSON-RPC 2.0 over `stdio`.
- **Purpose:** Enables conversational AI agents (Antigravity, Claude Desktop, Cursor) to inspect retail KPIs and simulate scenarios without SQL hallucinations.

### MCP Tools Specification

| Tool Name | Input Arguments | Output Format | Purpose |
| :--- | :--- | :--- | :--- |
| `get_executive_kpis` | `store_name`, `channel_type`, `fiscal_quarter` | JSON object | Returns certified commercial KPIs. |
| `get_stockout_alerts` | `limit` (default 10) | JSON array | Surfaces locations with $WOS < 2.5$. |
| `simulate_markdown` | `discount_pct` (float), `store_code`, `sku` | JSON object | Projects volume lift %, margin delta, and verdict. |
| `run_read_only_sql` | `query` (SELECT or WITH) | JSON array | Executes safe read-only SQL queries in DuckDB. |

---

## 7. Automated CI/CD Testing & Invariant Gate

- **Workflow:** `.github/workflows/verify_pipeline.yml`
- **Matrix:** 6 Automated Verification Stages on every push/PR:
  1. `python scripts/verify_schema.py --mode csv` (Referential integrity, math invariants).
  2. `python scripts/convert_to_parquet.py` (Storage compression & query benchmarks).
  3. `python scripts/verify_rill_models.py` (Rill models, metrics, and DAX parity).
  4. `python scripts/verify_mcp_server.py` (MCP handshake, tool discovery, and stdio execution).
  5. `python scripts/audit_everything.py` (Full 10-point master integrity audit).
  6. `pytest tests/` (FastAPI REST endpoint contracts).
