# 📊 Rill BI-as-Code — GCC Omnichannel Retail Control Tower

This directory contains the declarative **Rill BI-as-Code** project for the GCC Omnichannel Retail Control Tower, built directly on top of the Kimball Star Schema production CSVs in `../data/`.

---

## 🏗️ Project Architecture

```text
rill/
├── rill.yaml                  # Project metadata & DuckDB configuration
├── sources/                   # Raw star schema ingestion layers
│   ├── pos_transactions.yaml  # Fact_POS_Transactions (115,000+ rows)
│   ├── daily_inventory.yaml   # Fact_Daily_Inventory (53,000+ rows)
│   ├── dim_product.yaml       # Dim_Product (115 luxury SKUs)
│   ├── dim_store.yaml         # Dim_Store (9 GCC locations)
│   └── dim_date.yaml          # Dim_Date (730 days calendar)
├── models/                    # DuckDB transformation joins
│   ├── pos_analytics.sql      # Star-joined POS transactions + margin logic
│   └── inventory_analytics.sql# Star-joined inventory snapshots
├── metrics/                   # Semantic metrics & KPI definitions
│   ├── retail_kpis.yaml       # Commercial KPIs (Revenue, Margin %, AUR, Markdown Depth)
│   └── inventory_kpis.yaml    # Supply chain KPIs (On Hand, Available, Inventory Cost)
└── dashboards/                # Interactive exploratory dashboards
    ├── retail_overview.yaml   # Executive Retail Performance Control Tower
    └── inventory_health.yaml  # Store Inventory Health & Balancing
```

---

## 🚀 How to Run Rill

Because Rill's local engine currently targets Linux/macOS, run it via **Windows Subsystem for Linux (WSL)** or **Docker**:

### Method 1: Via WSL (Ubuntu) — Recommended

1. Open your WSL terminal (e.g., Ubuntu).
2. Install Rill CLI (takes ~10 seconds):
   ```bash
   curl -s https://cdn.rilldata.com/install.sh | bash
   ```
3. Navigate to this directory inside WSL:
   ```bash
   cd "/mnt/r/Projects/Omnichannel Retail Control Tower/rill"
   ```
4. Start Rill:
   ```bash
   rill start
   ```
5. Open `http://localhost:9009` in your Windows browser to explore your metrics live!

---

### Method 2: Via Docker

If Docker Desktop is running:
```bash
docker run -it --rm \
  -p 9009:9009 \
  -v "R:/Projects/Omnichannel Retail Control Tower:/project" \
  -w /project/rill \
  ghcr.io/rilldata/rill:latest start
```

---

## 🤖 AI Agent MCP Server Integration
Rill features native Model Context Protocol (MCP) support. Once running, you can connect Antigravity or Claude to query your live retail metrics in natural language without manual SQL:
```bash
rill start --readonly
```
Connect via MCP on port `9009` to inspect measures, dimension cardinality, and trend anomalies.
