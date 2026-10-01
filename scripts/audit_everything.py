"""
Comprehensive 360-degree audit script for GCC Omnichannel Retail Control Tower.
Verifies all data files, schemas, DAX measures, C# TOM script, BIM file, and Web UI parameters.
"""
import os
import re
import json
import duckdb
import pandas as pd

def run_audit():
    print("=" * 80)
    print("STARTING END-TO-END 360-DEGREE AUDIT OF CONTROL TOWER")
    print("=" * 80)
    
    issues = []
    
    # 1. Check CSV files existence and row counts
    data_dir = "data"
    expected_files = {
        "Dim_Date.csv": 731,
        "Dim_Store.csv": 9,
        "Dim_Product.csv": 115,
        "Fact_POS_Transactions.csv": 115008,
        "Fact_Daily_Inventory.csv": 53808,
        "Markdown_Scenario.csv": 11
    }
    
    con = duckdb.connect()
    
    for filename, expected_rows in expected_files.items():
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            issues.append(f"MISSING FILE: {filepath}")
            continue
        count = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{filepath}')").fetchone()[0]
        match = "MATCH" if count == expected_rows else f"MISMATCH (expected {expected_rows})"
        print(f"File: {filename:<28} | Rows: {count:<8} | {match}")
        if count != expected_rows:
            issues.append(f"Row count mismatch in {filename}: got {count}, expected {expected_rows}")

    # 2. Check Data Integrity & Foreign Keys
    print("\n--- Checking Referential Integrity & Invariants ---")
    pos_orphans_store = con.execute("""
        SELECT COUNT(*) FROM read_csv_auto('data/Fact_POS_Transactions.csv') f
        LEFT JOIN read_csv_auto('data/Dim_Store.csv') s ON f.StoreKey = s.StoreKey
        WHERE s.StoreKey IS NULL
    """).fetchone()[0]
    
    pos_orphans_prod = con.execute("""
        SELECT COUNT(*) FROM read_csv_auto('data/Fact_POS_Transactions.csv') f
        LEFT JOIN read_csv_auto('data/Dim_Product.csv') p ON f.ProductKey = p.ProductKey
        WHERE p.ProductKey IS NULL
    """).fetchone()[0]
    
    inv_orphans_store = con.execute("""
        SELECT COUNT(*) FROM read_csv_auto('data/Fact_Daily_Inventory.csv') f
        LEFT JOIN read_csv_auto('data/Dim_Store.csv') s ON f.StoreKey = s.StoreKey
        WHERE s.StoreKey IS NULL
    """).fetchone()[0]
    
    inv_orphans_prod = con.execute("""
        SELECT COUNT(*) FROM read_csv_auto('data/Fact_Daily_Inventory.csv') f
        LEFT JOIN read_csv_auto('data/Dim_Product.csv') p ON f.ProductKey = p.ProductKey
        WHERE p.ProductKey IS NULL
    """).fetchone()[0]
    
    print(f"POS -> Store Orphan FKs:    {pos_orphans_store}")
    print(f"POS -> Product Orphan FKs:  {pos_orphans_prod}")
    print(f"Inv -> Store Orphan FKs:    {inv_orphans_store}")
    print(f"Inv -> Product Orphan FKs:  {inv_orphans_prod}")
    
    if any([pos_orphans_store, pos_orphans_prod, inv_orphans_store, inv_orphans_prod]):
        issues.append("Orphan foreign keys found in Fact tables!")

    # Check Additive Math: NetSalesAmt = GrossSalesAmt - DiscountAmt
    math_diff = con.execute("""
        SELECT COUNT(*) FROM read_csv_auto('data/Fact_POS_Transactions.csv')
        WHERE ROUND(NetSalesAmt, 2) != ROUND(GrossSalesAmt - DiscountAmt, 2)
    """).fetchone()[0]
    print(f"POS NetSales != Gross - Discount: {math_diff} rows")
    if math_diff > 0:
        issues.append(f"{math_diff} rows have NetSales != Gross - Discount")

    # 3. Check Financial Aggregates
    fin = con.execute("""
        SELECT 
            SUM(UnitsSold) as Units,
            SUM(GrossSalesAmt) as Gross,
            SUM(DiscountAmt) as Discount,
            SUM(NetSalesAmt) as Net,
            SUM(ExtendedCostAmt) as COGS,
            SUM(NetSalesAmt) - SUM(ExtendedCostAmt) as Margin,
            (SUM(NetSalesAmt) - SUM(ExtendedCostAmt)) / SUM(NetSalesAmt) * 100 as MarginPct,
            SUM(DiscountAmt) / SUM(GrossSalesAmt) * 100 as MarkdownDepthPct,
            SUM(NetSalesAmt) / SUM(UnitsSold) as AUR,
            SUM(ExtendedCostAmt) / SUM(UnitsSold) as AUC
        FROM read_csv_auto('data/Fact_POS_Transactions.csv')
    """).fetchone()
    
    print("\n--- Financial Core Aggregates ---")
    print(f"Units Sold:       {fin[0]:,}")
    print(f"Gross Sales:      AED {fin[1]:,.2f}")
    print(f"Markdown Disc:    AED {fin[2]:,.2f}")
    print(f"Net Revenue:      AED {fin[3]:,.2f}")
    print(f"Total COGS:       AED {fin[4]:,.2f}")
    print(f"Gross Margin:     AED {fin[5]:,.2f} ({fin[6]:.2f}%)")
    print(f"Markdown Depth:   {fin[7]:.2f}%")
    print(f"AUR:              AED {fin[8]:,.2f}")
    print(f"AUC:              AED {fin[9]:,.2f}")

    # 4. Check Power Query M scripts
    print("\n--- Checking Power Query M Scripts ---")
    pq_dir = "power_query"
    for fname in ["Dim_Date.m", "Dim_Store.m", "Dim_Product.m", "Fact_POS_Transactions.m", "Fact_Daily_Inventory.m", "Markdown_Scenario.m"]:
        p = os.path.join(pq_dir, fname)
        if not os.path.exists(p):
            issues.append(f"Missing Power Query file: {p}")
        else:
            content = open(p, encoding='utf-8').read()
            if "DataFolderPath" not in content:
                issues.append(f"{fname} does not reference parameter DataFolderPath")
            print(f"Power Query: {fname:<25} [OK]")

    # 5. Check Tabular Model BIM & C# TOM Script
    print("\n--- Checking Tabular Model BIM & C# Script ---")
    bim_path = "tabular/model.bim"
    bim = json.load(open(bim_path, encoding='utf-8'))
    bim_tables = {t['name']: t for t in bim['model']['tables']}
    print(f"BIM Tables ({len(bim_tables)}): {list(bim_tables.keys())}")
    
    # BIM relationships
    rels = bim['model'].get('relationships', [])
    print(f"BIM Relationships count: {len(rels)}")
    for r in rels:
        print(f"  {r['fromTable']}[{r['fromColumn']}] -> {r['toTable']}[{r['toColumn']}] (CrossFiltering: {r.get('crossFilteringBehavior', 'OneDirection')})")
        if r.get('crossFilteringBehavior', 'OneDirection') != 'OneDirection' and r.get('crossFilteringBehavior', 'oneDirection') != 'oneDirection':
            issues.append(f"Relationship not single-direction: {r}")

    # BIM Measures
    bim_measures = {m['name']: m for m in bim_tables['_Measures'].get('measures', [])}
    print(f"BIM Measures in _Measures: {len(bim_measures)}")

    # Parse C# catalog
    cs_path = "scripts/Apply_Tabular_Metadata.cs"
    cs_content = open(cs_path, encoding='utf-8').read()
    cs_measures = re.findall(r'Name\s*=\s*"([^"]+)"', cs_content)
    print(f"Measures in C# Catalog: {len(cs_measures)}")
    
    missing_in_bim = set(cs_measures) - set(bim_measures.keys())
    missing_in_cs = set(bim_measures.keys()) - set(cs_measures)
    if missing_in_bim:
        print(f"Measures in C# but NOT in BIM: {missing_in_bim}")
        issues.append(f"Measures in C# but missing from BIM: {missing_in_bim}")
    if missing_in_cs:
        print(f"Measures in BIM but NOT in C#: {missing_in_cs}")
        # Note: BIM might have additional helper measures, let's see

    # 6. Check Web UI index.html alignment
    print("\n--- Checking Web Control Tower Alignment ---")
    web_path = "web/index.html"
    web_content = open(web_path, encoding='utf-8').read()
    
    # Check if heuristic multipliers exist
    heuristic_patterns = [r'\*\s*180\b', r'\*\s*120\b', r'\*\s*45\b']
    for pat in heuristic_patterns:
        if re.search(pat, web_content):
            issues.append(f"Found forbidden heuristic multiplier pattern '{pat}' in web/index.html!")
            print(f"  [FAIL] Heuristic multiplier '{pat}' found in web/index.html")
        else:
            print(f"  [PASS] No heuristic pattern '{pat}'")

    # Check store count in web UI
    if "All Channels (8 GCC Locations)" in web_content:
        print("  [PASS] Web UI dropdown correctly reflects 8 GCC Locations")
    else:
        issues.append("Web UI dropdown does not mention 8 GCC Locations")

    # Check Gross Margin % in web UI
    if "69.7%" in web_content:
        print("  [PASS] Web UI reflects verified Gross Margin 69.7%")
    else:
        issues.append("Web UI missing 69.7% margin benchmark")

    # Check Base Unit Volumes in web UI
    expected_skus = ["RTW-BLZ-LIN-001", "LEA-TOT-GLD-002", "FTW-SNK-LTH-003", "DRS-SLK-EVN-004", "BTY-EXT-OUD-005", "RTW-TEE-COT-006"]
    for sku in expected_skus:
        if sku in web_content:
            print(f"  [PASS] SKU {sku} present in web UI simulation matrix")
        else:
            issues.append(f"SKU {sku} missing from web/index.html")

    # 7. Check Case Study & Readme
    print("\n--- Checking Documentation & Case Study Alignment ---")
    case_study_md = open("docs/CASE_STUDY.md", encoding='utf-8').read()
    cs_has_margin = ("69.7%" in case_study_md or "69.73%" in case_study_md)
    cs_has_gross = ("205.2M" in case_study_md or "205.23M" in case_study_md)
    cs_has_net = ("192.7M" in case_study_md or "192.73M" in case_study_md)
    if cs_has_margin and cs_has_gross and cs_has_net:
        print("  [PASS] docs/CASE_STUDY.md numbers align with dataset")
    else:
        issues.append(f"docs/CASE_STUDY.md has misaligned financial numbers (margin:{cs_has_margin}, gross:{cs_has_gross}, net:{cs_has_net})")
        
    readme_md = open("README.md", encoding='utf-8').read()
    rm_has_margin = ("69.7%" in readme_md or "69.73%" in readme_md)
    rm_has_rows = ("115,008" in readme_md or "115,000+" in readme_md)
    if rm_has_margin and rm_has_rows:
        print("  [PASS] README.md numbers align with dataset")
    else:
        issues.append(f"README.md has misaligned metrics (margin:{rm_has_margin}, rows:{rm_has_rows})")

    print("\n" + "=" * 80)
    print(f"AUDIT COMPLETE: {len(issues)} ISSUES IDENTIFIED")
    print("=" * 80)
    for i, issue in enumerate(issues, 1):
        print(f"[{i}] {issue}")

if __name__ == "__main__":
    run_audit()
