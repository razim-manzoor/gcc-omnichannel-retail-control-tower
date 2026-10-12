# 🔄 End-to-End System & Sequence Flows (SYSTEM_FLOWS.md)
## GCC Omnichannel Retail & Markdown Elasticity Control Tower

**Document Version:** 1.0.0  
**Status:** Production Verified  
**Diagram Format:** Mermaid Diagrams (Supported across GitHub, VSCode, Obsidian, and Markdown Viewers)

---

## 1. High-Level Architectural Landscape

```mermaid
flowchart TD
    subgraph S1["1. Synthesis & Lakehouse Layer"]
        A["Python Data Generator<br/>(scripts/generate_data.py)"] -->|Outputs CSV| B["data/*.csv<br/>(Kimball Star Schema)"]
        B -->|DuckDB Vectorized Converter| C["data/parquet/*.parquet<br/>(Snappy Compressed -60.5%)"]
    end

    subgraph S2["2. Processing & Semantic Layer"]
        B -->|Power Query M ETL| D["Power BI Tabular Model<br/>(model.bim & 43 DAX Measures)"]
        C -->|In-Memory DuckDB| E["DuckDB OLAP Engine<br/>(scripts/verify_schema.py)"]
        B -->|SQL Joins & YAML Metrics| F["Rill BI-as-Code<br/>(rill/models & metrics)"]
    end

    subgraph S3["3. Service & API Layer"]
        E --> G["FastAPI Microservice<br/>(api/main.py - Port 8000)"]
        E --> H["MCP Server over Stdio<br/>(mcp/duckdb_mcp_server.py)"]
        F --> I["Rill Developer Web UI<br/>(Port 9009)"]
    end

    subgraph S4["4. User & Consumer Layer"]
        G -->|JSON REST Endpoints| J["C-Suite Web Dashboard<br/>(web/index.html)"]
        D -->|VertiPaq Analytics| K["Power BI Executive Report<br/>(Desktop / Service)"]
        H -->|Tool Call Execution| L["AI Pair Programmer / Agent<br/>(Antigravity / Claude / Cursor)"]
        J -->|What-If Adjustments| M["Executive Decision Maker<br/>(CCO, Merchandiser, Supply Chain)"]
    end

    subgraph S5["5. Automated Quality Gate"]
        N["GitHub Actions CI/CD<br/>(.github/workflows/verify_pipeline.yml)"] -.->|Validates| B
        N -.->|Benchmarking| C
        N -.->|Parity Checks| D
        N -.->|Contract Tests| G
        N -.->|Tool Tests| H
    end
```

---

## 2. Data Synthesis & Lakehouse Ingestion Pipeline Flow

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Data Engineer / CI Runner
    participant Gen as scripts/generate_data.py
    participant CSV as data/*.csv
    participant Pq as scripts/convert_to_parquet.py
    participant Audit as scripts/audit_everything.py
    participant VertiPaq as Tabular Editor / Power BI

    Dev->>Gen: Execute python generate_data.py
    Gen->>Gen: Sample realistic GCC retail calendar & footfall weights
    Gen->>Gen: Generate 115,008 POS transactions & 53,808 daily stock balances
    Gen->>CSV: Write 5 Relational CSVs + Markdown_Scenario.csv

    Dev->>Pq: Execute python convert_to_parquet.py
    Pq->>CSV: Read CSV via DuckDB read_csv_auto()
    Pq->>Pq: Apply Snappy compression & dictionary encoding
    Pq->>Pq: Benchmark CSV vs Parquet query throughput
    Pq-->>Dev: Log 60.5% space savings & 15x-28x speedups

    Dev->>Audit: Execute python audit_everything.py
    Audit->>CSV: Verify foreign key referential integrity (0 orphans)
    Audit->>CSV: Verify math invariants (Net = Gross - Discount)
    Audit->>CSV: Verify closing balance inventory math
    Audit-->>Dev: 100% Audit Passed (0 issues identified)

    Dev->>VertiPaq: Run Apply_Tabular_Metadata.cs
    VertiPaq->>VertiPaq: Compile 43 DAX measures across 6 display folders
```

---

## 3. What-If Markdown Elasticity Simulation Loop

```mermaid
sequenceDiagram
    autonumber
    actor Exec as Merchandiser / C-Suite User
    participant UI as Web UI / API Endpoint
    participant Eng as Elasticity Engine (DuckDB/DAX)
    participant Model as Star Schema Models

    Exec->>UI: Select Scenario Discount % (e.g. 15% Slider)
    UI->>Eng: POST /api/simulation/markdown {"discount_pct": 0.15}
    
    Eng->>Model: Query baseline Units, Net Sales, COGS, and Elasticity
    Model-->>Eng: Base Units: 142,664 | Elasticity: -1.37 | AUR: 1,350.91 | AUC: 408.90
    
    Eng->>Eng: Compute Projected Lift: -1 * (-1.37 * 0.15) = +20.51%
    Eng->>Eng: Compute Simulated Units: 142,664 * 1.2051 = 171,924 units
    Eng->>Eng: Compute Simulated AUR: 1,350.91 * (1 - 0.15) = AED 1,148.27
    Eng->>Eng: Compute Simulated Net Revenue: 171,924 * 1,148.27 = AED 197.42M
    Eng->>Eng: Compute Simulated COGS: 171,924 * 408.90 = AED 70.30M
    Eng->>Eng: Compute Simulated Gross Margin: AED 197.42M - AED 70.30M = AED 127.12M
    Eng->>Eng: Evaluate Delta: AED 127.12M - AED 134.39M = -AED 7.27M (Dilution)
    Eng->>Eng: Compute Capital Released: 29,260 extra units * 408.90 = AED 11.96M
    
    Eng->>Eng: Evaluate Commercial Decision Gate Verdict
    Note over Eng: Margin Delta <= 0 -> "CAPITAL TRADE-OFF / DILUTIVE MARGIN RISK"
    
    Eng-->>UI: Return JSON Payload (Simulated P&L, Verdict, Capital Released)
    UI-->>Exec: Render Waterfall Chart, Dynamic KPI Cards, and Action Guidance
```

---

## 4. Prescriptive Inter-Mall Stock Balancing Flow

```mermaid
flowchart TD
    Start["Daily Inventory Snapshot Ingested<br/>(Fact_Daily_Inventory)"] --> Fetch["Calculate Trailing 4-Week Sales Run Rate<br/>(Trailing 28 Days / 4)"]
    Fetch --> EvalWOS["Compute Weeks of Supply (WOS)<br/>Ending On-Hand / Weekly Run Rate"]
    Fetch --> EvalSTR["Compute Sell-Through Rate (STR %)<br/>Sold Units / (Sold Units + Ending On-Hand)"]
    
    EvalWOS & EvalSTR --> Decision{"Classify Stock Health State"}
    
    Decision -->|"STR >= 70% & WOS < 2.5"| Stockout["⚠️ CRITICAL_STOCKOUT_RISK<br/>High Footfall Depletion"]
    Decision -->|"STR <= 25% & WOS > 10.0"| Overstock["📦 OVERSTOCK_CASH_TRAP<br/>Idle Warehouse Capital"]
    Decision -->|"3.0 <= WOS <= 6.0"| Balanced["🟢 BALANCED_EQUILIBRIUM<br/>Optimal Supply Buffer"]
    Decision -->|"Other"| Monitor["🔍 ATTENTION_MONITOR<br/>Velocity Surveillance"]
    
    Stockout --> Pull["Generate Action Directive:<br/>🚨 PULL INVENTORY from Yas Mall / Regional DC<br/>Target: Buffer to 4 Weeks Safety Stock"]
    Overstock --> Push["Generate Action Directive:<br/>🔄 PUSH INVENTORY to Flagship or Trigger Elastic Markdown<br/>Surplus: Deficit Liquidation"]
    Balanced --> Stable["Maintain current replenishment schedule"]
    
    Pull & Push & Stable --> AlertStream["Surface on Web UI Table, FastAPI (/api/inventory/stockouts), and MCP"]
```

---

## 5. Conversational AI Agent Interaction Flow (MCP)

```mermaid
sequenceDiagram
    autonumber
    actor User as Executive / Developer
    participant LLM as AI Coding Assistant (Antigravity / Claude)
    participant MCP as MCP Server (mcp/duckdb_mcp_server.py)
    participant Duck as DuckDB In-Memory Columnar Engine
    participant Lakehouse as data/parquet/*.parquet

    User->>LLM: "What was our markdown depth in Abu Dhabi boutiques last quarter?"
    LLM->>LLM: Analyze intent & inspect registered MCP tool definitions
    LLM->>MCP: Call tool "get_executive_kpis" over Stdio JSON-RPC
    Note over LLM,MCP: {"params": {"store_name": "Yas Mall Abu Dhabi", "fiscal_quarter": "Q4"}}
    
    MCP->>Duck: Execute optimized parameterized SQL query
    Duck->>Lakehouse: Scan parquet with column pruning & predicate pushdown
    Lakehouse-->>Duck: Return vector results in 3.5ms
    Duck-->>MCP: {gross_sales: 18.2M, markdown_depth_pct: 6.12%, margin_pct: 69.8%}
    
    MCP-->>LLM: Return JSON-RPC result payload
    LLM->>LLM: Synthesize executive summary using verified figures
    LLM-->>User: "In Q4, Yas Mall Abu Dhabi operated at a 6.12% markdown depth with AED 18.2M in gross sales, preserving a 69.8% gross margin."
```

---

## 6. Automated CI/CD Quality Assurance Gate

```mermaid
flowchart LR
    Push["Developer pushes commit<br/>or opens Pull Request to 'main'"] --> Actions["GitHub Actions Runner<br/>(ubuntu-latest, Python 3.12)"]
    
    subgraph Gate["Automated Verification Pipeline (.github/workflows/verify_pipeline.yml)"]
        direction TB
        S1["Step 1: Kimball Star Schema & DAX Invariants<br/>(scripts/verify_schema.py)"]
        S2["Step 2: Parquet Conversion & Benchmark<br/>(scripts/convert_to_parquet.py)"]
        S3["Step 3: Rill BI-as-Code Model Parity<br/>(scripts/verify_rill_models.py)"]
        S4["Step 4: Model Context Protocol (MCP) Server<br/>(scripts/verify_mcp_server.py)"]
        S5["Step 5: Full 360-Degree Integrity Audit<br/>(scripts/audit_everything.py)"]
        S6["Step 6: FastAPI Microservice Integration Tests<br/>(pytest tests/ -v)"]
        
        S1 --> S2 --> S3 --> S4 --> S5 --> S6
    end
    
    Actions --> Gate
    Gate -->|"Any Check Fails (Exit Code != 0)"| Fail["❌ Build Fails & PR Blocked<br/>Prevents Regression"]
    Gate -->|"All Checks Pass (Exit Code 0)"| Pass["🟢 Build Passes<br/>README Badge: Passing"]
```
