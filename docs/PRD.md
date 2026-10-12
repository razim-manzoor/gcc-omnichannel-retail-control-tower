# 📋 Product Requirements Document (PRD)
## GCC Omnichannel Retail & Markdown Elasticity Control Tower

**Document Version:** 1.0.0  
**Status:** Approved / Production Verified  
**Target Audience:** C-Suite Executives, Regional Commercial Directors, Merchandising Leads, Data Platform Engineers  
**Project Repository:** `gcc-omnichannel-retail-control-tower`

---

## 1. Executive Summary & Vision Statement

### 1.1 The Vision
To deliver an enterprise-grade, real-time **Decision Support Control Tower** that provides GCC luxury and premium retail executives with instant visibility into commercial profitability, omnichannel stock balancing, and price elasticity trade-offs across high-footfall mall destinations and digital fulfillment hubs.

### 1.2 Cognitive Target: The 3-Second Executive Rule
The interface and underlying architecture are purpose-built to answer three critical executive questions within 3 seconds of scanning:
1. **Macro Commercial Status:** *Are we meeting our margin targets (benchmark >65%) across channels?*
2. **Operational Bottleneck:** *Where are we experiencing stockout risks or margin-eroding markdowns?*
3. **Prescriptive Control Levers:** *What exact transfer or pricing action will liquidate inventory without destroying profitability?*

---

## 2. Business Problem & Market Context

### 2.1 The GCC Luxury Retail Reality
Retail groups in the GCC (**The Dubai Mall Flagship**, **Mall of the Emirates**, **Yas Mall Abu Dhabi**, **Kingdom Centre Riyadh**) operate in a unique environment characterized by:
- **Extreme Footfall Seasonality:** Dramatic demand spikes during Ramadan/Eid, Dubai Shopping Festival (DSF), and White Friday, contrasted with summer footfall migration.
- **High Carrying Costs:** Prime mall square footage leases demand exceptional asset turnover and high Average Unit Retail (AUR).
- **Asymmetric Inter-Mall Demand:** Stockouts frequently paralyze flagship stores while regional boutiques hold idle stock of identical SKUs.
- **Margin Erosion from Blunt Markdowns:** Traditional blanket promotions reduce inventory but heavily dilute brand prestige and gross margins.

### 2.2 Core Business Pain Points

| Pain Point | Impact on Retail Groups | Control Tower Solution |
| :--- | :--- | :--- |
| **Delayed Visibility** | Weekly batch reports hide stockouts until after footfall weekends pass. | Sub-10ms DuckDB OLAP engine and real-time REST API. |
| **Indiscriminate Promotions** | Markdowns applied blindly to inelastic products burn margin without driving volume. | Econometric elasticity simulation modeling volume lift vs. profit dilution. |
| **Sub-optimal Inventory Allocation** | Stores operate in silos, requiring emergency factory reorders while sister malls sit on surplus. | Automated prescriptive inter-mall rebalancing directives (Push vs. Pull). |
| **"Metrics Drift" Across Teams** | E-commerce, finance, and merchandising report conflicting gross margin and revenue figures. | Single-source-of-truth semantic layer certified across DAX, DuckDB, Rill, and MCP. |

---

## 3. User Personas & Jobs-to-be-Done (JTBD)

### 3.1 Persona 1: Chief Commercial Officer (CCO / CFO)
- **Role:** Regional commercial governance across UAE & KSA stores.
- **Core Goal:** Protect gross margins (holding the 69.7% luxury benchmark) while maximizing total net revenue.
- **JTBD:** *"When I review weekend performance on Monday morning, I want to immediately see whether revenue growth is accretive or driven by margin-destroying discounts."*

### 3.2 Persona 2: Head of Merchandising & Pricing
- **Role:** Category planning, pricing sensitivity, and markdown concession management.
- **Core Goal:** Liquidate slow-moving lines without sparking price wars or diluting profitability.
- **JTBD:** *"Before signing off on a 20% mid-season markdown, I want to simulate whether the projected volume lift covers the lower unit contribution margin."*

### 3.3 Persona 3: Omnichannel Supply Chain & Inventory Director
- **Role:** Regional DC and store-level stock replenishment across 8 GCC nodes.
- **Core Goal:** Minimize stockout loss while avoiding overstocked "cash traps".
- **JTBD:** *"When high footfall depletes flagship shelves, I want automated directives specifying which regional store has excess weeks of supply to pull stock from."*

### 3.4 Persona 4: Executive AI Pair Programmer / Agent (Antigravity / Claude)
- **Role:** Autonomous operational intelligence partner.
- **Core Goal:** Query commercial health and simulate scenarios in natural language.
- **JTBD:** *"When asked a natural language query, I want to call governed MCP tools to retrieve certified metrics with zero SQL hallucination."*

---

## 4. Functional Requirements (FR)

### FR-1: Commercial Aggregation & Core Profitability
- The system **MUST** track 115,000+ individual POS sales transactions across 114 luxury SKUs and 8 GCC locations.
- The system **MUST** compute core commercial KPIs:
  - **Gross Sales:** Full ticket value prior to discounts.
  - **Markdown Discounts:** Promotional concessions at checkout.
  - **Net Realized Revenue:** $Net = Gross - Discount$ (strictly enforced invariant).
  - **Landed COGS & Gross Margin:** Absolute gross margin in AED and Gross Margin %.
  - **AUR & AUC:** Average Unit Retail and Average Unit Cost.

### FR-2: Semi-Additive Closing Inventory Snapshots
- The system **MUST** track daily point-in-time inventory balances (53,808 snapshots).
- Snapshot balance measures **MUST NOT** sum across calendar dates; they must report the closing date balance for any selected period.
- The system **MUST** enforce the inventory invariant: $Available = OnHand - Reserved$.

### FR-3: Prescriptive Stock Balancing & Velocity Directives
- The system **MUST** compute:
  - **Sell-Through Rate (STR %):** $\frac{UnitsSold}{UnitsSold + EndingOnHand}$.
  - **Trailing 4-Week Velocity:** Weekly sales run rate.
  - **Weeks of Supply (WOS):** $\frac{EndingOnHand}{WeeklyRunRate}$.
- The system **MUST** classify stock into 4 states:
  - `CRITICAL_STOCKOUT_RISK`: $STR \ge 70\%$ and $WOS < 2.5$.
  - `OVERSTOCK_CASH_TRAP`: $STR \le 25\%$ and $WOS > 10.0$.
  - `BALANCED_EQUILIBRIUM`: $3.0 \le WOS \le 6.0$.
  - `ATTENTION_MONITOR`: Intermediate state.
- The system **MUST** generate human-readable prescriptive transfer directives (e.g., *"⚠️ PULL INVENTORY: Request 45 units from Yas Mall / Regional DC"*).

### FR-4: Econometric What-If Markdown Elasticity Simulator
- The system **MUST** allow continuous scenario discount adjustments ($0\%$ to $50\%$).
- The system **MUST** leverage product-specific elasticity coefficients (range $-0.85$ to $-2.40$) to project volume lift:
  $$\text{Simulated Volume Lift \%} = -1 \times (\text{Effective Elasticity} \times \text{Scenario Discount})$$
- The system **MUST** evaluate the financial hurdle:
  - $\Delta \text{Gross Margin} = \text{Simulated Margin} - \text{Baseline Margin}$.
  - Working Capital Released $= \text{Incremental Units Cleared} \times \text{AUC}$.
- The system **MUST** output a commercial decision gate verdict:
  - `ACCRETIVE PROFIT YIELD` ($\Delta GM > 0$).
  - `CAPITAL TRADE-OFF / DILUTIVE MARGIN RISK` ($\Delta GM \le 0$).

### FR-5: Declarative BI-as-Code Layer (Rill)
- The system **MUST** provide declarative YAML metrics views and DuckDB models (`rill/`).
- The system **MUST** provide instantaneous exploratory dashboards with time series brushing and leaderboards.

### FR-6: Lakehouse Parquet Storage & Benchmark Layer
- The system **MUST** convert raw transactional CSV data into Snappy-compressed Apache Parquet.
- The conversion **MUST** achieve $>50\%$ storage footprint reduction and $>10\times$ analytical query speedup.

### FR-7: High-Performance REST API Microservice
- The system **MUST** expose a FastAPI analytical microservice (`api/main.py`) with auto-generated Swagger UI (`/docs`).
- Endpoints **MUST** include:
  - `GET /api/kpis` (commercial aggregates with dimensional filtering).
  - `GET /api/inventory/stockouts` (real-time stockout risk alerts).
  - `POST /api/simulation/markdown` (elasticity simulation engine).
  - `GET /api/stores` (store metadata).

### FR-8: Conversational AI Agent Interface (Model Context Protocol - MCP)
- The system **MUST** implement a Model Context Protocol (MCP) server over `stdio` (`mcp/duckdb_mcp_server.py`).
- The MCP server **MUST** provide tools: `get_executive_kpis`, `get_stockout_alerts`, `simulate_markdown`, `run_read_only_sql`.

---

## 5. Non-Functional Requirements (NFR)

| ID | Requirement Area | Standard / Threshold | Verification Method |
| :--- | :--- | :--- | :--- |
| **NFR-1** | **Analytical Query Latency** | Sub-10ms for aggregations over 115k rows. | DuckDB in-memory columnar execution (`scripts/convert_to_parquet.py`). |
| **NFR-2** | **Zero Data Discrepancy** | Exact penny-level parity across DAX, DuckDB, Rill, FastAPI, and MCP. | `scripts/audit_everything.py` (Check 3 & Check 8). |
| **NFR-3** | **Referential Integrity** | Zero orphan foreign keys between Fact tables and Dimensions. | `scripts/audit_everything.py` (Check 2). |
| **NFR-4** | **Data Governance & Privacy** | 100% synthetic data; zero customer PII or confidential tenant data. | Inherent to statistical data generator (`scripts/generate_data.py`). |
| **NFR-5** | **Automated CI/CD Quality Gate**| 100% passing automated test suite on every Git push and PR. | GitHub Actions (`.github/workflows/verify_pipeline.yml`). |
| **NFR-6** | **Web Interface Accessibility**| WCAG 2.2 AA compliant contrast, semantic ARIA roles, and labels. | Semantic HTML audit in `web/index.html`. |

---

## 6. Success Metrics & Key Results (OKRs)

1. **Analytical Throughput:** In-memory verification completes in $<30$ ms for 115k records.
2. **Financial Precision:** 100% mathematical consistency with verified baseline:
   - Net Sales: **AED 192,726,717.08**
   - Gross Margin: **AED 134,392,065.08 (69.73%)**
   - Markdown Depth: **6.09%**
   - Units Sold: **142,664**
3. **Storage Efficiency:** Parquet lakehouse storage achieves $>60\%$ compression vs CSV.
4. **Agent Reliability:** MCP server executes and responds to analytical queries in $<15$ ms with 0 SQL hallucinations.
