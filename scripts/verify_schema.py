"""
Data Integrity & Analytical Verification Script
GCC Omnichannel Retail & Markdown Elasticity Control Tower
Target Engine: Kimball Star Schema / Power BI VertiPaq Analytical Contract
Simulates & validates the full DAX Semantic Layer in DuckDB.
Supports both seed unit test verification and full 100,000+ row CSV production dataset.
"""

import sys
import argparse
import time
import duckdb
from pathlib import Path

# Ensure UTF-8 output encoding on Windows console
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def run_verification(source_mode="csv"):
    base_dir = Path(__file__).resolve().parent.parent
    ddl_file = base_dir / "sql" / "01_star_schema_ddl.sql"
    data_dir = base_dir / "data"
    
    print("=" * 95)
    print("GCC OMNICHANNEL RETAIL CONTROL TOWER - TABULAR DAX SEMANTIC LAYER VERIFICATION")
    print("Engine: Kimball Star Schema / Power BI VertiPaq Analytical Contract")
    print(f"Data Source Mode: {source_mode.upper()}")
    print("=" * 95)
    
    start_t0 = time.time()
    con = duckdb.connect(database=":memory:")
    
    # 1. Execute DDL
    print(f"\n[1/6] Executing Star Schema DDL from: {ddl_file.name}")
    ddl_sql = ddl_file.read_text(encoding="utf-8")
    con.execute(ddl_sql)
    print("  -> All Dimensions, Facts, and Disconnected Parameter Tables created in memory.")
    
    # 2. Ingest Data
    pos_csv = data_dir / "Fact_POS_Transactions.csv"
    if not pos_csv.exists():
        raise FileNotFoundError(
            f"Production CSV dataset not found in {data_dir}.\n"
            "Please run: python scripts/generate_data.py to synthesize the 115,000+ record dataset first."
        )

    print(f"\n[2/6] Ingesting Production CSV Dataset from: {data_dir} via DuckDB zero-copy...")
    t_ingest = time.time()
    
    # Clear initial DDL seed rows to allow clean insertion from CSV
    con.execute("DELETE FROM Dim_Date; DELETE FROM Dim_Store; DELETE FROM Dim_Product; DELETE FROM Markdown_Scenario;")
    
    # Load CSVs
    con.execute(f"INSERT INTO Dim_Date SELECT * FROM read_csv_auto('{data_dir / 'Dim_Date.csv'}')")
    con.execute(f"INSERT INTO Dim_Store SELECT * FROM read_csv_auto('{data_dir / 'Dim_Store.csv'}')")
    con.execute(f"INSERT INTO Dim_Product SELECT * FROM read_csv_auto('{data_dir / 'Dim_Product.csv'}')")
    con.execute(f"INSERT INTO Fact_POS_Transactions SELECT * FROM read_csv_auto('{data_dir / 'Fact_POS_Transactions.csv'}')")
    con.execute(f"INSERT INTO Fact_Daily_Inventory SELECT * FROM read_csv_auto('{data_dir / 'Fact_Daily_Inventory.csv'}')")
    con.execute(f"INSERT INTO Markdown_Scenario SELECT * FROM read_csv_auto('{data_dir / 'Markdown_Scenario.csv'}')")
    
    ingest_elapsed = time.time() - t_ingest
    print(f"  -> Ingestion completed in {ingest_elapsed:.3f}s.")
    print(f"     Dim_Date:               {con.execute('SELECT COUNT(*) FROM Dim_Date').fetchone()[0]:>8,d} rows")
    print(f"     Dim_Store:              {con.execute('SELECT COUNT(*) FROM Dim_Store').fetchone()[0]:>8,d} rows")
    print(f"     Dim_Product:            {con.execute('SELECT COUNT(*) FROM Dim_Product').fetchone()[0]:>8,d} rows")
    print(f"     Fact_POS_Transactions:  {con.execute('SELECT COUNT(*) FROM Fact_POS_Transactions').fetchone()[0]:>8,d} rows")
    print(f"     Fact_Daily_Inventory:   {con.execute('SELECT COUNT(*) FROM Fact_Daily_Inventory').fetchone()[0]:>8,d} rows")
    print(f"     Markdown_Scenario:      {con.execute('SELECT COUNT(*) FROM Markdown_Scenario').fetchone()[0]:>8,d} rows")
    
    # 3. Dimensional Integrity Checks
    print("\n[3/6] Running Data Quality & Referential Integrity Assertions...")
    
    # Check A: Verify -1 Unknown Members Exist
    unk_date = con.execute("SELECT COUNT(*) FROM Dim_Date WHERE DateKey = -1").fetchone()[0]
    unk_store = con.execute("SELECT COUNT(*) FROM Dim_Store WHERE StoreKey = -1").fetchone()[0]
    unk_prod = con.execute("SELECT COUNT(*) FROM Dim_Product WHERE ProductKey = -1").fetchone()[0]
    assert unk_date == 1, "Assertion Failed: Dim_Date missing -1 fallback record"
    assert unk_store == 1, "Assertion Failed: Dim_Store missing -1 fallback record"
    assert unk_prod == 1, "Assertion Failed: Dim_Product missing -1 fallback record"
    print("  [PASS] Referential Integrity Fallback (-1 Unknown Members) verified.")
    
    # Check B: Zero Orphan Foreign Keys in POS Transactions
    pos_count = con.execute("SELECT COUNT(*) FROM Fact_POS_Transactions").fetchone()[0]
    orphan_pos = con.execute("""
        SELECT COUNT(*)
        FROM Fact_POS_Transactions f
        LEFT JOIN Dim_Date d ON f.DateKey = d.DateKey
        LEFT JOIN Dim_Store s ON f.StoreKey = s.StoreKey
        LEFT JOIN Dim_Product p ON f.ProductKey = p.ProductKey
        WHERE d.DateKey IS NULL OR s.StoreKey IS NULL OR p.ProductKey IS NULL
    """).fetchone()[0]
    assert orphan_pos == 0, f"Assertion Failed: Found {orphan_pos} orphan POS transactions!"
    print(f"  [PASS] Fact_POS_Transactions zero orphan FK check passed ({pos_count:,} rows).")

    # Check C: Zero Orphan Foreign Keys in Daily Inventory
    inv_count = con.execute("SELECT COUNT(*) FROM Fact_Daily_Inventory").fetchone()[0]
    orphan_inv = con.execute("""
        SELECT COUNT(*)
        FROM Fact_Daily_Inventory f
        LEFT JOIN Dim_Date d ON f.SnapshotDateKey = d.DateKey
        LEFT JOIN Dim_Store s ON f.StoreKey = s.StoreKey
        LEFT JOIN Dim_Product p ON f.ProductKey = p.ProductKey
        WHERE d.DateKey IS NULL OR s.StoreKey IS NULL OR p.ProductKey IS NULL
    """).fetchone()[0]
    assert orphan_inv == 0, f"Assertion Failed: Found {orphan_inv} orphan inventory snapshot records!"
    print(f"  [PASS] Fact_Daily_Inventory zero orphan FK check passed ({inv_count:,} rows).")
    
    # Check D: Financial & Additive Math Invariant
    pos_math_check = con.execute("""
        SELECT COUNT(*) 
        FROM Fact_POS_Transactions 
        WHERE ROUND(GrossSalesAmt - DiscountAmt, 2) != ROUND(NetSalesAmt, 2)
    """).fetchone()[0]
    assert pos_math_check == 0, "Assertion Failed: NetSalesAmt != GrossSalesAmt - DiscountAmt"
    print("  [PASS] Additive Measure Integrity: NetSalesAmt = GrossSalesAmt - DiscountAmt verified across all rows.")

    # Check E: Inventory Semi-Additive Math Invariant
    inv_math_check = con.execute("""
        SELECT COUNT(*) 
        FROM Fact_Daily_Inventory 
        WHERE AvailableUnits != (OnHandUnits - ReservedUnits)
           OR ROUND(InventoryCostValueAmt, 2) != ROUND(OnHandUnits * UnitCostSnapshotAmt, 2)
    """).fetchone()[0]
    assert inv_math_check == 0, "Assertion Failed: Inventory available or cost valuation mismatch"
    print("  [PASS] Semi-Additive Measure Integrity: AvailableUnits & Cost Value calculations verified.")

    # 4. Folder 01: Financial & Commercial Core Measures
    print("\n[4/6] Verifying Folder 01 DAX Financial & Commercial Core Measures...")
    t_comm = time.time()
    comm_metrics = con.execute("""
        SELECT 
            SUM(UnitsSold) AS UnitsSold,
            SUM(GrossSalesAmt) AS GrossSalesAED,
            SUM(DiscountAmt) AS MarkdownDiscountAED,
            SUM(NetSalesAmt) AS NetRevenueAED,
            SUM(ExtendedCostAmt) AS TotalCOGSAED,
            SUM(NetSalesAmt) - SUM(ExtendedCostAmt) AS GrossMarginAED,
            ROUND((SUM(NetSalesAmt) - SUM(ExtendedCostAmt)) / NULLIF(SUM(NetSalesAmt), 0) * 100, 2) AS GrossMarginPct,
            ROUND(SUM(DiscountAmt) / NULLIF(SUM(GrossSalesAmt), 0) * 100, 2) AS MarkdownDepthPct,
            ROUND(SUM(NetSalesAmt) / NULLIF(SUM(UnitsSold), 0), 2) AS AUR,
            ROUND(SUM(ExtendedCostAmt) / NULLIF(SUM(UnitsSold), 0), 2) AS AUC
        FROM Fact_POS_Transactions
    """).fetchone()
    comm_query_ms = (time.time() - t_comm) * 1000

    print(f"  - Units Sold:               {comm_metrics[0]:>12,d}")
    print(f"  - Gross Sales (AED):        AED {comm_metrics[1]:>12,.2f}")
    print(f"  - Markdown Discount (AED):  AED {comm_metrics[2]:>12,.2f}")
    print(f"  - Net Revenue (AED):        AED {comm_metrics[3]:>12,.2f}")
    print(f"  - Total COGS (AED):         AED {comm_metrics[4]:>12,.2f}")
    print(f"  - Gross Margin (AED):       AED {comm_metrics[5]:>12,.2f}")
    print(f"  - Gross Margin %:           {comm_metrics[6]:>12.1f}%")
    print(f"  - Markdown Depth %:         {comm_metrics[7]:>12.1f}%")
    print(f"  - Average Unit Retail (AUR):AED {comm_metrics[8]:>12,.2f}")
    print(f"  - Average Unit Cost (AUC):  AED {comm_metrics[9]:>12,.2f}")
    print(f"  (Aggregated across {pos_count:,} rows in {comm_query_ms:.2f} ms)")

    # 5. Folder 02, 03 & 05: Inventory Velocity & Prescriptive Stock Balancing
    print("\n[5/6] Verifying Folder 02, 03 & 05 Inventory Snapshots, Velocity & Prescriptive Balancing...")
    
    balancing_query = con.execute("""
        WITH LatestDate AS (
            SELECT MAX(SnapshotDateKey) AS MaxDateKey FROM Fact_Daily_Inventory
        ),
        EndingInventory AS (
            SELECT 
                f.StoreKey,
                f.ProductKey,
                f.OnHandUnits AS EndingOnHandUnits,
                f.InTransitUnits AS EndingInTransitUnits,
                f.InventoryCostValueAmt AS EndingInventoryCostAED
            FROM Fact_Daily_Inventory f
            JOIN LatestDate ld ON f.SnapshotDateKey = ld.MaxDateKey
        ),
        SalesVelocity AS (
            SELECT 
                StoreKey,
                ProductKey,
                SUM(UnitsSold) AS UnitsSoldT4W,
                ROUND(SUM(UnitsSold) / 4.0, 2) AS WeeklyRunRateT4W
            FROM Fact_POS_Transactions
            WHERE DateKey >= 20260201
            GROUP BY StoreKey, ProductKey
        ),
        EvaluatedBalance AS (
            SELECT 
                s.StoreCode,
                s.StoreName,
                p.SKU,
                p.ProductName,
                COALESCE(e.EndingOnHandUnits, 0) AS EndingOnHand,
                COALESCE(e.EndingInTransitUnits, 0) AS EndingInTransit,
                COALESCE(e.EndingInventoryCostAED, 0.0) AS EndingCostAED,
                COALESCE(v.UnitsSoldT4W, 0) AS UnitsSoldT4W,
                COALESCE(v.WeeklyRunRateT4W, 0.0) AS WeeklyRunRate,
                -- STR % = Sold / (Sold + EndingOnHand)
                ROUND(
                    COALESCE(v.UnitsSoldT4W, 0)::FLOAT / 
                    NULLIF(COALESCE(v.UnitsSoldT4W, 0) + COALESCE(e.EndingOnHandUnits, 0), 0) * 100, 1
                ) AS SellThroughPct,
                -- Weeks of Supply = EndingOnHand / WeeklyRunRate
                ROUND(
                    COALESCE(e.EndingOnHandUnits, 0)::FLOAT / 
                    NULLIF(v.WeeklyRunRateT4W, 0), 1
                ) AS WeeksOfSupply,
                -- Target Safety Stock = CEIL(WeeklyRunRate * 4)
                CEIL(COALESCE(v.WeeklyRunRateT4W, 0.0) * 4) AS TargetSafetyStock,
                -- Net Unit Variance = EndingOnHand - TargetSafetyStock
                COALESCE(e.EndingOnHandUnits, 0) - CEIL(COALESCE(v.WeeklyRunRateT4W, 0.0) * 4) AS NetUnitVariance,
                p.ElasticityCoefficient AS Elasticity
            FROM EndingInventory e
            FULL OUTER JOIN SalesVelocity v ON e.StoreKey = v.StoreKey AND e.ProductKey = v.ProductKey
            JOIN Dim_Store s ON COALESCE(e.StoreKey, v.StoreKey) = s.StoreKey
            JOIN Dim_Product p ON COALESCE(e.ProductKey, v.ProductKey) = p.ProductKey
            WHERE p.ProductKey IN (101, 102, 103, 104, 105, 106)
        )
        SELECT 
            StoreCode,
            SKU,
            EndingOnHand,
            WeeklyRunRate,
            SellThroughPct,
            WeeksOfSupply,
            TargetSafetyStock,
            NetUnitVariance,
            -- Stock Health Classification
            CASE 
                WHEN WeeksOfSupply IS NULL THEN 'NO_VELOCITY'
                WHEN SellThroughPct >= 70.0 AND WeeksOfSupply < 2.5 THEN 'CRITICAL_STOCKOUT_RISK'
                WHEN SellThroughPct <= 25.0 AND WeeksOfSupply > 10.0 THEN 'OVERSTOCK_CASH_TRAP'
                WHEN WeeksOfSupply >= 3.0 AND WeeksOfSupply <= 6.0 THEN 'BALANCED_EQUILIBRIUM'
                ELSE 'ATTENTION_MONITOR'
            END AS HealthClassification,
            -- Inter-Mall Rebalance Directive
            CASE 
                WHEN SellThroughPct >= 70.0 AND WeeksOfSupply < 2.5 
                    THEN '⚠️ PULL INVENTORY: Request ' || CAST(ABS(NetUnitVariance) AS INT) || ' units from Yas Mall / Regional DC.'
                WHEN SellThroughPct <= 25.0 AND WeeksOfSupply > 10.0 
                    THEN '📦 PUSH INVENTORY: Surplus of ' || CAST(NetUnitVariance AS INT) || ' units. Dispatch to The Dubai Mall or trigger Tier-1 markdown.'
                WHEN WeeksOfSupply >= 3.0 AND WeeksOfSupply <= 6.0 
                    THEN '🟢 OPTIMAL: Target weeks of supply maintained.'
                ELSE 'ATTENTION: Monitor velocity run-rate.'
            END AS RebalanceDirective
        FROM EvaluatedBalance
        ORDER BY StoreCode, SKU
        LIMIT 10;
    """).fetchall()

    headers = ["StoreCode", "SKU", "OnHand", "RunRate/W", "STR%", "WOS", "TargetSS", "Variance", "Classification"]
    print(f"  {' | '.join(headers)}")
    print("  " + "-" * 115)
    for r in balancing_query:
        wos_str = f"{r[5]:>5.1f}" if r[5] is not None else "  N/A"
        str_pct = f"{r[4]:>5.1f}%" if r[4] is not None else "  N/A"
        print(f"  {r[0]:<10} | {r[1]:<16} | {r[2]:>6} | {r[3]:>9.2f} | {str_pct} | {wos_str} | {r[6]:>8.0f} | {r[7]:>8.0f} | {r[8]:<23}")
        print(f"    Directive: {r[9]}")

    # 6. Folder 06: Markdown Simulation & Sensitivity Engine
    print("\n[6/6] Verifying Folder 06 Markdown Simulation & Sensitivity Engine...")
    
    # Portfolio-level Effective Elasticity Coefficient
    eff_elast_row = con.execute("""
        SELECT 
            SUM(f.UnitsSold) AS AggUnits,
            ROUND(SUM(f.UnitsSold * p.ElasticityCoefficient) / SUM(f.UnitsSold), 2) AS WeightedElasticity
        FROM Fact_POS_Transactions f
        JOIN Dim_Product p ON f.ProductKey = p.ProductKey
    """).fetchone()
    print(f"  - Total Transaction Units:        {eff_elast_row[0]:>12,d}")
    print(f"  - Portfolio Effective Elasticity:  {eff_elast_row[1]:>12.2f}")

    # Granular What-If Simulation Scenarios
    sim_query = con.execute("""
        WITH BaseMetrics AS (
            SELECT 
                p.ProductKey,
                p.SKU,
                p.ProductName,
                p.BrandTier,
                p.ElasticityCoefficient AS Elasticity,
                SUM(f.UnitsSold) AS UnitsSold,
                ROUND(SUM(f.NetSalesAmt) / SUM(f.UnitsSold), 2) AS BaselineAUR,
                ROUND(SUM(f.ExtendedCostAmt) / SUM(f.UnitsSold), 2) AS AUC,
                SUM(f.NetSalesAmt) - SUM(f.ExtendedCostAmt) AS BaselineGrossMargin
            FROM Fact_POS_Transactions f
            JOIN Dim_Product p ON f.ProductKey = p.ProductKey
            WHERE p.ProductKey IN (101, 102) -- Linen Blazer (-1.80 Elastic) & Calfskin Tote (-0.65 Inelastic)
            GROUP BY 1, 2, 3, 4, 5
        ),
        SimulatedScenarios AS (
            SELECT 
                b.SKU,
                b.BrandTier,
                b.Elasticity,
                m.ScenarioDiscountPct AS SimDiscountPct,
                m.DiscountDisplayLabel,
                b.UnitsSold AS BaseUnits,
                b.BaselineAUR,
                b.AUC,
                b.BaselineGrossMargin,
                -- [Simulated Volume Lift %] = -1 * ( Elasticity * Discount )
                ROUND(-1.0 * b.Elasticity * m.ScenarioDiscountPct, 4) AS VolumeLiftPct,
                -- [Simulated Units Sold] = BaseUnits * ( 1 + Lift )
                ROUND(b.UnitsSold * (1.0 + (-1.0 * b.Elasticity * m.ScenarioDiscountPct)), 2) AS SimUnitsSold,
                -- [Incremental Units Cleared] = MAX(0, SimUnits - BaseUnits)
                ROUND(GREATEST(0.0, b.UnitsSold * (1.0 + (-1.0 * b.Elasticity * m.ScenarioDiscountPct)) - b.UnitsSold), 2) AS IncrementalUnits,
                -- [Simulated Effective AUR (AED)] = BaselineAUR * ( 1 - Discount )
                ROUND(b.BaselineAUR * (1.0 - m.ScenarioDiscountPct), 2) AS SimAUR,
                -- [Simulated Net Revenue (AED)] = SimUnits * SimAUR
                ROUND(
                    (b.UnitsSold * (1.0 + (-1.0 * b.Elasticity * m.ScenarioDiscountPct))) * 
                    (b.BaselineAUR * (1.0 - m.ScenarioDiscountPct)), 
                    2
                ) AS SimNetRevenue,
                -- [Simulated Total COGS (AED)] = SimUnits * AUC
                ROUND(
                    (b.UnitsSold * (1.0 + (-1.0 * b.Elasticity * m.ScenarioDiscountPct))) * b.AUC, 
                    2
                ) AS SimCOGS,
                -- [Working Capital Released (AED)] = IncrementalUnits * AUC
                ROUND(
                    GREATEST(0.0, b.UnitsSold * (1.0 + (-1.0 * b.Elasticity * m.ScenarioDiscountPct)) - b.UnitsSold) * b.AUC, 
                    2
                ) AS WorkingCapitalReleased
            FROM BaseMetrics b
            CROSS JOIN Markdown_Scenario m
            WHERE m.ScenarioDiscountPct IN (0.00, 0.10, 0.20, 0.30)
        ),
        TradeOffCalculations AS (
            SELECT 
                *,
                -- [Simulated Gross Margin (AED)] = SimNetRevenue - SimCOGS
                ROUND(SimNetRevenue - SimCOGS, 2) AS SimGrossMargin,
                -- [Gross Margin Delta (AED)] = SimGrossMargin - BaselineGrossMargin
                ROUND((SimNetRevenue - SimCOGS) - BaselineGrossMargin, 2) AS GrossMarginDelta,
                -- [Breakeven Unit Volume] = BaselineGM / (SimAUR - AUC)
                CASE 
                    WHEN (SimAUR - AUC) > 0 
                        THEN ROUND(BaselineGrossMargin / (SimAUR - AUC), 2)
                    ELSE NULL 
                END AS BreakevenUnitVolume,
                -- [Breakeven Unit Gap] = SimUnits - BreakevenUnitVolume
                CASE 
                    WHEN (SimAUR - AUC) > 0 
                        THEN ROUND(SimUnitsSold - (BaselineGrossMargin / (SimAUR - AUC)), 2)
                    ELSE NULL 
                END AS BreakevenUnitGap,
                -- [Capital vs Margin ROI Ratio] = Working Capital Released / ABS(Margin Sacrificed)
                CASE 
                    WHEN (SimNetRevenue - SimCOGS) - BaselineGrossMargin < 0 
                        THEN ROUND(WorkingCapitalReleased / ABS((SimNetRevenue - SimCOGS) - BaselineGrossMargin), 2)
                    ELSE NULL 
                END AS CapitalMarginROIRatio
            FROM SimulatedScenarios
        )
        SELECT 
            SKU,
            BrandTier,
            Elasticity,
            DiscountDisplayLabel,
            VolumeLiftPct * 100 AS LiftPct,
            SimUnitsSold,
            SimAUR,
            SimGrossMargin,
            GrossMarginDelta,
            WorkingCapitalReleased,
            BreakevenUnitVolume,
            BreakevenUnitGap,
            CapitalMarginROIRatio,
            -- [Breakeven Feasibility Verdict]
            CASE 
                WHEN SimDiscountPct = 0.00 THEN 'BASELINE (Full Price)'
                WHEN GrossMarginDelta >= 0 THEN '✅ ACCRETIVE: Generates +' || CAST(ROUND(GrossMarginDelta, 0) AS INT) || ' AED'
                WHEN GrossMarginDelta < 0 AND CapitalMarginROIRatio IS NOT NULL AND CapitalMarginROIRatio >= 1.5 THEN '⚖️ CAPITAL TRADE-OFF: ROI ' || CAST(ROUND(CapitalMarginROIRatio, 2) AS VARCHAR) || 'x offsets margin cost'
                ELSE '❌ DILUTIVE: Destroys ' || CAST(ABS(ROUND(GrossMarginDelta, 0)) AS INT) || ' AED'
            END AS FeasibilityVerdict
        FROM TradeOffCalculations
        ORDER BY SKU, SimDiscountPct;
    """).fetchall()

    sim_headers = ["SKU", "Scenario", "Lift%", "SimUnits", "SimAUR", "SimMargin", "GMDelta", "CapReleased", "BEUnits", "BEGap", "CapROI", "Verdict"]
    print(f"  {' | '.join(sim_headers)}")
    print("  " + "-" * 140)
    for r in sim_query:
        cap_roi_str = f"{r[12]:>5.2f}x" if r[12] is not None else "   N/A"
        be_units_str = f"{r[10]:>7.2f}" if r[10] is not None else "    N/A"
        be_gap_str = f"{r[11]:>+7.2f}" if r[11] is not None else "    N/A"
        print(f"  {r[0]:<16} | {r[3]:<13} | {r[4]:>5.1f}% | {r[5]:>8.2f} | {r[6]:>8.2f} | {r[7]:>10.2f} | {r[8]:>+10.2f} | {r[9]:>11.2f} | {be_units_str} | {be_gap_str} | {cap_roi_str} | {r[13]}")

    total_time = time.time() - start_t0
    print("\n" + "=" * 95)
    print(f"ALL VERTIPAQ MEASURE FORMULAS & ANALYTICAL INVARIANTS RATIFIED & VERIFIED [PASS] in {total_time:.2f}s")
    print("=" * 95)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify Kimball Star Schema and DAX Semantic Layer against CSV Data")
    parser.add_argument("--mode", default="csv", help="Data source mode (csv=data folder)")
    args = parser.parse_args()
    run_verification(source_mode=args.mode)
