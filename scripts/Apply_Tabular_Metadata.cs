// ============================================================================
// GCC RETAIL CONTROL TOWER - TABULAR MODEL OBJECT MODEL (TOM) AUTOMATION SCRIPT
// Compatible with: Tabular Editor 2 (TE2) and Tabular Editor 3 (TE3)
// Enforces 1-Click Measure Creation, Display Folders, Formatting, and Governance
// Target Repository Table: _Measures
// ============================================================================

// 1. Ensure centralized measure repository table exists
if (!Model.Tables.Contains("_Measures"))
{
    var newTable = Model.AddTable("_Measures");
    newTable.Description = "Centralized Repository for GCC Omnichannel Retail & Markdown Elasticity Measures";
    newTable.IsHidden = false;
}

var measuresTable = Model.Tables["_Measures"];

// 2. Measure Master Catalog (43 Production DAX Measures across 6 Display Folders)
var measureCatalog = new []
{
    // -------------------------------------------------------------------------
    // FOLDER 01: Financial & Commercial Core
    // -------------------------------------------------------------------------
    new {
        Name = "Units Sold",
        Folder = "01 Financial & Commercial Core",
        Format = "#,##0",
        Desc = "Base Additive Metrics: Total units sold across POS checkouts",
        Dax = "SUM ( Fact_POS_Transactions[UnitsSold] )"
    },
    new {
        Name = "Gross Sales (AED)",
        Folder = "01 Financial & Commercial Core",
        Format = "#,##0 \"AED\"",
        Desc = "Base Additive Metrics: Gross ticket sales before any discount or markdown deductions",
        Dax = "SUM ( Fact_POS_Transactions[GrossSalesAmt] )"
    },
    new {
        Name = "Markdown Discount (AED)",
        Folder = "01 Financial & Commercial Core",
        Format = "#,##0 \"AED\"",
        Desc = "Base Additive Metrics: Total promotional discounts, vouchers, and price markdowns deducted at checkout",
        Dax = "SUM ( Fact_POS_Transactions[DiscountAmt] )"
    },
    new {
        Name = "Net Revenue (AED)",
        Folder = "01 Financial & Commercial Core",
        Format = "#,##0 \"AED\"",
        Desc = "Base Additive Metrics: Realized net sales revenue after discounts (Net Sales = Gross - Discount)",
        Dax = "SUM ( Fact_POS_Transactions[NetSalesAmt] )"
    },
    new {
        Name = "Total COGS (AED)",
        Folder = "01 Financial & Commercial Core",
        Format = "#,##0 \"AED\"",
        Desc = "Base Additive Metrics: Total Cost of Goods Sold (COGS) based on landed unit cost snapshot",
        Dax = "SUM ( Fact_POS_Transactions[ExtendedCostAmt] )"
    },
    new {
        Name = "Gross Margin (AED)",
        Folder = "01 Financial & Commercial Core",
        Format = "#,##0 \"AED\"",
        Desc = "Commercial Profitability: Absolute Gross Margin in AED realized from completed transactions",
        Dax = "[Net Revenue (AED)] - [Total COGS (AED)]"
    },
    new {
        Name = "Gross Margin %",
        Folder = "01 Financial & Commercial Core",
        Format = "0.0%",
        Desc = "Commercial Profitability: Gross Margin percentage of net revenue",
        Dax = "DIVIDE ( [Gross Margin (AED)], [Net Revenue (AED)], 0 )"
    },
    new {
        Name = "Markdown Depth %",
        Folder = "01 Financial & Commercial Core",
        Format = "0.0%",
        Desc = "Commercial Profitability: Markdown depth percentage relative to gross sales",
        Dax = "DIVIDE ( [Markdown Discount (AED)], [Gross Sales (AED)], 0 )"
    },
    new {
        Name = "Average Unit Retail (AUR)",
        Folder = "01 Financial & Commercial Core",
        Format = "#,##0 \"AED\"",
        Desc = "Commercial Profitability: Average Realized Selling Price per unit sold",
        Dax = "DIVIDE ( [Net Revenue (AED)], [Units Sold], 0 )"
    },
    new {
        Name = "Average Unit Cost (AUC)",
        Folder = "01 Financial & Commercial Core",
        Format = "#,##0 \"AED\"",
        Desc = "Commercial Profitability: Average Cost of Goods Sold per unit sold",
        Dax = "DIVIDE ( [Total COGS (AED)], [Units Sold], 0 )"
    },

    // -------------------------------------------------------------------------
    // FOLDER 02: Semi-Additive Inventory Snapshots
    // -------------------------------------------------------------------------
    new {
        Name = "Ending On Hand Units",
        Folder = "02 Semi-Additive Inventory Snapshots",
        Format = "#,##0",
        Desc = "Strict Point-in-Time Snapshot Filtering (Closing Balance On-Hand)",
        Dax = "VAR LastAvailableDate = MAX ( Dim_Date[FullDate] )\nVAR TargetDateKey = \n    YEAR ( LastAvailableDate ) * 10000 \n    + MONTH ( LastAvailableDate ) * 100 \n    + DAY ( LastAvailableDate )\nRETURN\n    CALCULATE (\n        SUM ( Fact_Daily_Inventory[OnHandUnits] ),\n        Fact_Daily_Inventory[SnapshotDateKey] = TargetDateKey,\n        REMOVEFILTERS ( Dim_Date )\n    )"
    },
    new {
        Name = "Ending In-Transit Units",
        Folder = "02 Semi-Additive Inventory Snapshots",
        Format = "#,##0",
        Desc = "Strict Point-in-Time Snapshot Filtering (Closing Balance In-Transit)",
        Dax = "VAR LastAvailableDate = MAX ( Dim_Date[FullDate] )\nVAR TargetDateKey = \n    YEAR ( LastAvailableDate ) * 10000 \n    + MONTH ( LastAvailableDate ) * 100 \n    + DAY ( LastAvailableDate )\nRETURN\n    CALCULATE (\n        SUM ( Fact_Daily_Inventory[InTransitUnits] ),\n        Fact_Daily_Inventory[SnapshotDateKey] = TargetDateKey,\n        REMOVEFILTERS ( Dim_Date )\n    )"
    },
    new {
        Name = "Ending Inventory Cost (AED)",
        Folder = "02 Semi-Additive Inventory Snapshots",
        Format = "#,##0 \"AED\"",
        Desc = "Strict Point-in-Time Snapshot Filtering (Closing Inventory Landed Cost Value)",
        Dax = "VAR LastAvailableDate = MAX ( Dim_Date[FullDate] )\nVAR TargetDateKey = \n    YEAR ( LastAvailableDate ) * 10000 \n    + MONTH ( LastAvailableDate ) * 100 \n    + DAY ( LastAvailableDate )\nRETURN\n    CALCULATE (\n        SUM ( Fact_Daily_Inventory[InventoryCostValueAmt] ),\n        Fact_Daily_Inventory[SnapshotDateKey] = TargetDateKey,\n        REMOVEFILTERS ( Dim_Date )\n    )"
    },
    new {
        Name = "Average Inventory Cost (AED)",
        Folder = "02 Semi-Additive Inventory Snapshots",
        Format = "#,##0 \"AED\"",
        Desc = "Daily Average Inventory Value over the active evaluation window",
        Dax = "AVERAGEX (\n    KEEPFILTERS ( VALUES ( Dim_Date[DateKey] ) ),\n    CALCULATE ( SUM ( Fact_Daily_Inventory[InventoryCostValueAmt] ) )\n)"
    },

    // -------------------------------------------------------------------------
    // FOLDER 03: Asset Productivity & Supply Velocity
    // -------------------------------------------------------------------------
    new {
        Name = "Sell-Through Rate %",
        Folder = "03 Asset Productivity & Supply Velocity",
        Format = "0.0%",
        Desc = "Sell-Through Rate (STR %) = Units Sold / (Units Sold + Ending On-Hand Units)",
        Dax = "VAR SoldUnits = [Units Sold]\nVAR OnHand = [Ending On Hand Units]\nVAR PipelineTotal = SoldUnits + OnHand\nRETURN\n    DIVIDE ( SoldUnits, PipelineTotal, 0 )"
    },
    new {
        Name = "Units Sold Trailing 4W",
        Folder = "03 Asset Productivity & Supply Velocity",
        Format = "#,##0",
        Desc = "Trailing 28-Day Run Rate to smooth weekly footfall cycles",
        Dax = "VAR CurrentMaxDate = MAX ( Dim_Date[FullDate] )\nRETURN\n    CALCULATE (\n        [Units Sold],\n        DATESINPERIOD ( Dim_Date[FullDate], CurrentMaxDate, -28, DAY )\n    )"
    },
    new {
        Name = "Weekly Sales Run Rate (T4W)",
        Folder = "03 Asset Productivity & Supply Velocity",
        Format = "#,##0.0",
        Desc = "Weekly Sales Velocity over trailing 4 weeks",
        Dax = "DIVIDE ( [Units Sold Trailing 4W], 4, 0 )"
    },
    new {
        Name = "Weeks of Supply",
        Folder = "03 Asset Productivity & Supply Velocity",
        Format = "0.0 \"Wks\"",
        Desc = "Weeks of Supply (WOS / Forward Stock Cover)",
        Dax = "DIVIDE ( [Ending On Hand Units], [Weekly Sales Run Rate (T4W)], BLANK () )"
    },
    new {
        Name = "GMROI",
        Folder = "03 Asset Productivity & Supply Velocity",
        Format = "0.00\"x\"",
        Desc = "Gross Margin Return on Investment (GMROI) = Annualized Margin / Average Inventory at Cost",
        Dax = "VAR EvaluatedDays = COUNTROWS ( VALUES ( Dim_Date[DateKey] ) )\nVAR AnnualizationFactor = DIVIDE ( 365, MAX ( 1, EvaluatedDays ), 1 )\nVAR AnnualizedMargin = [Gross Margin (AED)] * AnnualizationFactor\nVAR AvgInventory = [Average Inventory Cost (AED)]\nRETURN\n    DIVIDE ( AnnualizedMargin, AvgInventory, 0 )"
    },

    // -------------------------------------------------------------------------
    // FOLDER 04: Time Intelligence & Variance
    // -------------------------------------------------------------------------
    new {
        Name = "Net Revenue MTD",
        Folder = "04 Time Intelligence & Variance",
        Format = "#,##0 \"AED\"",
        Desc = "Month-To-Date Net Revenue",
        Dax = "TOTALMTD ( [Net Revenue (AED)], Dim_Date[FullDate] )"
    },
    new {
        Name = "Net Revenue YTD",
        Folder = "04 Time Intelligence & Variance",
        Format = "#,##0 \"AED\"",
        Desc = "Year-To-Date Net Revenue",
        Dax = "TOTALYTD ( [Net Revenue (AED)], Dim_Date[FullDate] )"
    },
    new {
        Name = "Net Revenue Prior Period",
        Folder = "04 Time Intelligence & Variance",
        Format = "#,##0 \"AED\"",
        Desc = "Net Revenue for dynamic prior comparative period matching current selection length",
        Dax = "VAR SelectedDays = COUNTROWS ( VALUES ( Dim_Date[DateKey] ) )\nVAR MinDate = MIN ( Dim_Date[FullDate] )\nRETURN\n    CALCULATE (\n        [Net Revenue (AED)],\n        DATESBETWEEN (\n            Dim_Date[FullDate],\n            MinDate - SelectedDays,\n            MinDate - 1\n        )\n    )"
    },
    new {
        Name = "Net Revenue Growth %",
        Folder = "04 Time Intelligence & Variance",
        Format = "+0.0%;-0.0%;0.0%",
        Desc = "Period-over-period Net Revenue percentage growth",
        Dax = "VAR CurrentRev = [Net Revenue (AED)]\nVAR PriorRev = [Net Revenue Prior Period]\nRETURN\n    DIVIDE ( CurrentRev - PriorRev, PriorRev, BLANK () )"
    },

    // -------------------------------------------------------------------------
    // FOLDER 05: Prescriptive Stock Balancing
    // -------------------------------------------------------------------------
    new {
        Name = "Stock Health Classification",
        Folder = "05 Prescriptive Stock Balancing",
        Format = "",
        Desc = "Categorical Status based on velocity divergence & inventory cover",
        Dax = "VAR STR = [Sell-Through Rate %]\nVAR WOS = [Weeks of Supply]\nRETURN\n    SWITCH (\n        TRUE (),\n        ISBLANK ( WOS ), \"NO_VELOCITY\",\n        STR >= 0.70 && WOS < 2.5, \"CRITICAL_STOCKOUT_RISK\",\n        STR <= 0.25 && WOS > 10.0, \"OVERSTOCK_CASH_TRAP\",\n        WOS >= 3.0 && WOS <= 6.0, \"BALANCED_EQUILIBRIUM\",\n        \"ATTENTION_MONITOR\"\n    )"
    },
    new {
        Name = "Target Safety Stock Units",
        Folder = "05 Prescriptive Stock Balancing",
        Format = "#,##0",
        Desc = "Target buffer = 4.0 Weeks of Supply",
        Dax = "CEILING ( [Weekly Sales Run Rate (T4W)] * 4, 1 )"
    },
    new {
        Name = "Inter-Mall Net Unit Variance",
        Folder = "05 Prescriptive Stock Balancing",
        Format = "+#,##0;-#,##0;0",
        Desc = "Net Unit Variance relative to Target Safety Stock buffer",
        Dax = "[Ending On Hand Units] - [Target Safety Stock Units]"
    },
    new {
        Name = "Inter-Mall Rebalance Directive",
        Folder = "05 Prescriptive Stock Balancing",
        Format = "",
        Desc = "Prescriptive Transfer Recommendation & Action Directive",
        Dax = "VAR Status = [Stock Health Classification]\nVAR StoreCode = SELECTEDVALUE ( Dim_Store[StoreCode] )\nVAR UnitVariance = [Inter-Mall Net Unit Variance]\nRETURN\n    SWITCH (\n        Status,\n        \"CRITICAL_STOCKOUT_RISK\", \n            \"⚠️ PULL INVENTORY: Request \" & FORMAT ( ABS ( UnitVariance ), \"#,##0\" ) & \" units from Yas Mall / Regional DC.\",\n        \"OVERSTOCK_CASH_TRAP\", \n            \"📦 PUSH INVENTORY: Surplus of \" & FORMAT ( UnitVariance, \"#,##0\" ) & \" units. Dispatch to The Dubai Mall or trigger Tier-1 markdown.\",\n        \"BALANCED_EQUILIBRIUM\", \n            \"🟢 OPTIMAL: Target weeks of supply maintained.\",\n        BLANK ()\n    )"
    },
    new {
        Name = "Merchandising Action Trigger",
        Folder = "05 Prescriptive Stock Balancing",
        Format = "",
        Desc = "Real-time omnichannel merchandising trigger evaluating inter-mall pull, markdown liquidation, or e-com reallocation",
        Dax = "VAR STR = [Sell-Through Rate %]\nVAR WOS = [Weeks of Supply]\nVAR Elasticity = [Effective Elasticity Coeff]\nVAR OnHand = [Ending On Hand Units]\nRETURN\n    SWITCH (\n        TRUE (),\n        STR >= 0.70 && WOS < 2.0, \n            \"🚨 INTER-MALL PULL: Stockout in <14 days. Rebalance from Yas Mall/DC.\",\n        STR < 0.25 && WOS > 12.0 && Elasticity <= -1.40,\n            \"🏷️ TIER-2 MARKDOWN (25-30%): Highly elastic. Discount will release working capital fast.\",\n        STR < 0.25 && WOS > 12.0 && Elasticity > -1.40,\n            \"🔄 TRANSFER TO E-COM: Inelastic demand. Hold price; reallocate to digital hub.\",\n        WOS >= 3.0 && WOS <= 6.0, \n            \"🟢 HEALTHY: Operating at optimal sell-through equilibrium.\",\n        \"MONITOR VELOCITY\"\n    )"
    },

    // -------------------------------------------------------------------------
    // FOLDER 06: Markdown Simulation & Sensitivity
    // -------------------------------------------------------------------------
    new {
        Name = "Simulated Discount %",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "0.0%",
        Desc = "Harvests the selected discount percentage from disconnected parameter table Markdown_Scenario",
        Dax = "SELECTEDVALUE ( 'Markdown_Scenario'[ScenarioDiscountPct], 0.00 )"
    },
    new {
        Name = "Effective Elasticity Coeff",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "0.00",
        Desc = "Weighted average elasticity across selected products or transaction context",
        Dax = "VAR AggUnits = [Units Sold]\nRETURN\n    IF (\n        AggUnits > 0,\n        DIVIDE (\n            SUMX (\n                Dim_Product,\n                [Units Sold] * Dim_Product[ElasticityCoefficient]\n            ),\n            AggUnits,\n            -1.50\n        ),\n        -1.50\n    )"
    },
    new {
        Name = "Simulated Volume Lift %",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "+0.0%;-0.0%;0.0%",
        Desc = "Projected demand volume lift percentage driven by effective elasticity and scenario discount",
        Dax = "VAR Discount = [Simulated Discount %]\nVAR Elasticity = [Effective Elasticity Coeff]\nRETURN\n    -1 * ( Elasticity * Discount )"
    },
    new {
        Name = "Simulated Units Sold",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "#,##0",
        Desc = "Total projected simulated unit sales volume under the selected discount scenario",
        Dax = "VAR BaseUnits = [Units Sold]\nVAR Lift = [Simulated Volume Lift %]\nRETURN\n    BaseUnits * ( 1 + Lift )"
    },
    new {
        Name = "Incremental Units Cleared",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "#,##0",
        Desc = "Additional units cleared beyond baseline sales velocity",
        Dax = "MAX ( 0, [Simulated Units Sold] - [Units Sold] )"
    },
    new {
        Name = "Simulated Effective AUR (AED)",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "#,##0 \"AED\"",
        Desc = "Simulated realized average selling price per unit after scenario markdown",
        Dax = "VAR BaselineAUR = [Average Unit Retail (AUR)]\nVAR Discount = [Simulated Discount %]\nRETURN\n    BaselineAUR * ( 1 - Discount )"
    },
    new {
        Name = "Simulated Net Revenue (AED)",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "#,##0 \"AED\"",
        Desc = "Simulated net sales revenue realized under the markdown scenario",
        Dax = "[Simulated Units Sold] * [Simulated Effective AUR (AED)]"
    },
    new {
        Name = "Simulated Total COGS (AED)",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "#,##0 \"AED\"",
        Desc = "Simulated Cost of Goods Sold for the total projected volume",
        Dax = "VAR UnitCost = [Average Unit Cost (AUC)]\nRETURN\n    [Simulated Units Sold] * UnitCost"
    },
    new {
        Name = "Simulated Gross Margin (AED)",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "#,##0 \"AED\"",
        Desc = "Simulated Gross Margin realized under the markdown scenario",
        Dax = "[Simulated Net Revenue (AED)] - [Simulated Total COGS (AED)]"
    },
    new {
        Name = "Gross Margin Delta (AED)",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "+#,##0 \"AED\";-#,##0 \"AED\";0 \"AED\"",
        Desc = "Gross margin variance between markdown simulation and baseline actuals",
        Dax = "[Simulated Gross Margin (AED)] - [Gross Margin (AED)]"
    },
    new {
        Name = "Working Capital Released (AED)",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "#,##0 \"AED\"",
        Desc = "Additional inventory landed cost converted from warehouse shelves to liquid cash",
        Dax = "VAR UnitCost = [Average Unit Cost (AUC)]\nVAR ExtraUnits = [Incremental Units Cleared]\nRETURN\n    ExtraUnits * UnitCost"
    },
    new {
        Name = "Breakeven Unit Volume",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "#,##0",
        Desc = "Exact number of units required under discounted unit contribution margin to yield 100% of baseline Gross Margin",
        Dax = "VAR BaselineGM = [Gross Margin (AED)]\nVAR DiscountedUnitAUR = [Simulated Effective AUR (AED)]\nVAR UnitCost = [Average Unit Cost (AUC)]\nVAR UnitContributionMargin = DiscountedUnitAUR - UnitCost\nRETURN\n    IF (\n        UnitContributionMargin > 0,\n        DIVIDE ( BaselineGM, UnitContributionMargin, BLANK () ),\n        BLANK ()\n    )"
    },
    new {
        Name = "Breakeven Unit Gap",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "+#,##0;-#,##0;0",
        Desc = "Unit surplus or deficit against breakeven volume hurdle",
        Dax = "[Simulated Units Sold] - [Breakeven Unit Volume]"
    },
    new {
        Name = "Breakeven Feasibility Verdict",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "",
        Desc = "Executive green/red feasibility verdict classifying commercial profitability vs volume buffer",
        Dax = "VAR MarginDelta = [Gross Margin Delta (AED)]\nVAR CapROI = [Capital vs Margin ROI Ratio]\nRETURN\n    SWITCH (\n        TRUE (),\n        [Simulated Discount %] == 0, \"BASELINE (Full Price)\",\n        MarginDelta >= 0, \"✅ ACCRETIVE: Generates +\" & FORMAT ( MarginDelta, \"#,##0 AED\" ) & \" Net Profit\",\n        MarginDelta < 0 && NOT ISBLANK ( CapROI ) && CapROI >= 1.5, \"⚖️ CAPITAL TRADE-OFF: Working capital ROI \" & FORMAT ( CapROI, \"0.00x\" ) & \" offsets margin cost\",\n        \"❌ DILUTIVE: Destroys \" & FORMAT ( ABS ( MarginDelta ), \"#,##0 AED\" ) & \" Gross Margin\"\n    )"
    },
    new {
        Name = "Capital vs Margin ROI Ratio",
        Folder = "06 Markdown Simulation & Sensitivity",
        Format = "0.00\"x\"",
        Desc = "Working Capital Unlocked per 1 AED of Gross Margin Sacrificed",
        Dax = "VAR MarginSacrificed = ABS ( MIN ( 0, [Gross Margin Delta (AED)] ) )\nVAR CapitalReleased = [Working Capital Released (AED)]\nRETURN\n    IF (\n        MarginSacrificed > 0,\n        DIVIDE ( CapitalReleased, MarginSacrificed, BLANK () ),\n        BLANK ()\n    )"
    }
};

// 3. Execution: Create missing measures and enforce metadata
int createdCount = 0;
int updatedCount = 0;

foreach (var item in measureCatalog)
{
    Measure m;
    if (!measuresTable.Measures.Contains(item.Name))
    {
        m = measuresTable.AddMeasure(item.Name, item.Dax);
        createdCount++;
    }
    else
    {
        m = measuresTable.Measures[item.Name];
        m.Expression = item.Dax;
        updatedCount++;
    }

    m.DisplayFolder = item.Folder;
    m.Description = item.Desc;
    if (!string.IsNullOrEmpty(item.Format))
    {
        m.FormatString = item.Format;
    }
}

// 4. Output Summary Callout
Info(string.Format("Tabular Model Metadata Applied Successfully!\n- Created: {0} measures\n- Updated/Verified: {1} measures\n- Total Measures in _Measures: {2}", 
    createdCount, updatedCount, measuresTable.Measures.Count));
