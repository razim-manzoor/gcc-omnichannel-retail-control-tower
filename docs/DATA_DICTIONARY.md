# 📚 Data Dictionary & Semantic Measure Catalog (DATA_DICTIONARY.md)
## GCC Omnichannel Retail & Markdown Elasticity Control Tower

**Document Version:** 1.0.0  
**Target Engines:** Kimball Dimensional Warehouse, Power BI VertiPaq, DuckDB, Rill, FastAPI, MCP  
**Project Repository:** `gcc-omnichannel-retail-control-tower`

---

## 1. Relational Star Schema Data Dictionary

### 1.1 `Fact_POS_Transactions`
- **Description:** Granular transactional POS checkouts across GCC physical boutiques and digital fulfillment channels.
- **Granularity:** One record per item scanned in a shopping basket.
- **Total Record Count:** **115,008 rows**

| Column Name | Data Type | Nullable | Key Type | Description | Example Value |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `TransactionLineKey` | `BIGINT` | No | **PK** | Surrogate primary key for the transaction line item. | `1001` |
| `DateKey` | `INT` | No | **FK** | Surrogate key linking to `Dim_Date[DateKey]`. | `20260313` |
| `StoreKey` | `INT` | No | **FK** | Surrogate key linking to `Dim_Store[StoreKey]`. | `1` |
| `ProductKey` | `INT` | No | **FK** | Surrogate key linking to `Dim_Product[ProductKey]`. | `101` |
| `BasketID` | `VARCHAR` | No | Attribute | Unique identifier grouping items purchased in the same POS basket. | `BSK-DXB-0001` |
| `PaymentType` | `VARCHAR` | No | Attribute | Payment tender method (ApplePay, Visa, Mastercard, Cash, Tamara). | `ApplePay` |
| `UnitsSold` | `INT` | No | Metric | Physical count of units commercialized in the transaction. | `1` |
| `GrossSalesAmt` | `DECIMAL(12,2)` | No | Metric | Full ticket retail price in AED prior to promotional deductions. | `1450.00` |
| `DiscountAmt` | `DECIMAL(12,2)` | No | Metric | Promotional or markdown concession deducted at checkout. | `0.00` |
| `NetSalesAmt` | `DECIMAL(12,2)` | No | Metric | Realized net revenue in AED ($Net = Gross - Discount$). | `1450.00` |
| `ExtendedCostAmt` | `DECIMAL(12,2)` | No | Metric | Total landed Cost of Goods Sold (COGS) for the line item. | `450.00` |
| `TaxAmtAED` | `DECIMAL(12,2)` | No | Metric | 5% UAE/GCC VAT applied at transaction finalization. | `72.50` |

---

### 1.2 `Fact_Daily_Inventory`
- **Description:** Daily periodic closing snapshot recording store-level stock holdings across the GCC omnichannel network.
- **Granularity:** One record per SKU per store per calendar date.
- **Total Record Count:** **53,808 rows**

| Column Name | Data Type | Nullable | Key Type | Description | Example Value |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `InventorySnapshotKey`| `BIGINT` | No | **PK** | Surrogate primary key for daily snapshot record. | `50001` |
| `SnapshotDateKey` | `INT` | No | **FK** | Surrogate key linking to `Dim_Date[DateKey]`. | `20260101` |
| `StoreKey` | `INT` | No | **FK** | Surrogate key linking to `Dim_Store[StoreKey]`. | `1` |
| `ProductKey` | `INT` | No | **FK** | Surrogate key linking to `Dim_Product[ProductKey]`. | `101` |
| `OnHandUnits` | `INT` | No | Metric | Physical closing unit stock on boutique shelves and backroom. | `24` |
| `InTransitUnits` | `INT` | No | Metric | Units in transit from Central Distribution Center to boutique. | `6` |
| `ReservedUnits` | `INT` | No | Metric | Units reserved for click-and-collect or pending online dispatch. | `2` |
| `AvailableUnits` | `INT` | No | Metric | Units unallocated and available for immediate customer sale ($OnHand - Reserved$). | `22` |
| `UnitCostSnapshotAmt` | `DECIMAL(10,2)` | No | Metric | Landed cost snapshot per unit in AED at close of business. | `450.00` |
| `InventoryCostValueAmt`| `DECIMAL(14,2)`| No | Metric | Total working capital tied in inventory at landed cost ($OnHand \times UnitCost$). | `10800.00` |

---

### 1.3 `Dim_Date`
- **Description:** Conformed enterprise retail calendar covering two full fiscal years (2025–2026) with GCC regional dynamics.
- **Granularity:** One record per calendar day.
- **Total Record Count:** **731 rows** (730 calendar days + 1 Unknown row)

| Column Name | Data Type | Nullable | Key Type | Description | Example Value |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `DateKey` | `INT` | No | **PK** | Date integer surrogate key formatted as `YYYYMMDD` (`-1` for Unknown). | `20260313` |
| `FullDate` | `DATE` | No | Attribute | Standard ISO-8601 calendar date. | `2026-03-13` |
| `FiscalYear` | `INT` | No | Attribute | Fiscal year identifier (`2025` or `2026`). | `2026` |
| `FiscalQuarter` | `VARCHAR` | No | Attribute | Fiscal quarter designation (`Q1`, `Q2`, `Q3`, `Q4`). | `Q1` |
| `FiscalMonthNum` | `INT` | No | Attribute | Calendar month number (1 to 12). | `3` |
| `FiscalMonthName` | `VARCHAR` | No | Attribute | Full English month name (`January`, `February`, etc.). | `March` |
| `RetailWeekNum` | `INT` | No | Attribute | National Retail Federation / 4-5-4 retail week index (1 to 52). | `11` |
| `DayOfWeekName` | `VARCHAR` | No | Attribute | Day name (`Monday`, `Tuesday`, ..., `Sunday`). | `Friday` |
| `DayOfWeekNum` | `INT` | No | Attribute | Day sequence index (1 to 7). | `5` |
| `IsWeekendGCC` | `BOOLEAN` | No | Flag | Identifies GCC statutory weekend days (Friday, Saturday, Sunday). | `True` |
| `IsRetailPeakSeason` | `BOOLEAN` | No | Flag | Flags major GCC shopping windows (Ramadan, Eid, DSF, White Friday). | `True` |

---

### 1.4 `Dim_Store`
- **Description:** Store footprint and fulfillment nodes operating across the United Arab Emirates and Kingdom of Saudi Arabia.
- **Granularity:** One record per store location.
- **Total Record Count:** **9 rows** (8 active locations + 1 Unknown row)

| Column Name | Data Type | Nullable | Key Type | Description | Example Value |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `StoreKey` | `INT` | No | **PK** | Store surrogate key (`-1` for Unknown member fallback). | `1` |
| `StoreCode` | `VARCHAR` | No | Attribute | Unique boutique code identifier. | `DXB-TDM-01` |
| `StoreName` | `VARCHAR` | No | Attribute | Formal retail location name. | `The Dubai Mall Flagship` |
| `Channel` | `VARCHAR` | No | Attribute | Omnichannel operational channel (Physical Flagship, Boutique, Digital). | `Physical Flagship` |
| `Emirate` | `VARCHAR` | No | Attribute | Regional city/emirate jurisdiction (Dubai, Abu Dhabi, Riyadh). | `Dubai` |
| `Country` | `VARCHAR` | No | Attribute | Sovereign country (United Arab Emirates, Saudi Arabia). | `United Arab Emirates` |
| `GrossLeasableAreaSqFt`| `INT` | No | Attribute | Gross leasable retail space in square feet. | `14500` |
| `ClusterTier` | `VARCHAR` | No | Attribute | Commercial tier classification (Flagship, Boutique, Digital Hub). | `Flagship` |
| `HubFulfillmentEligible`| `BOOLEAN`| No | Flag | Flags whether store can fulfill ship-from-store online orders. | `True` |

---

### 1.5 `Dim_Product`
- **Description:** Luxury and contemporary retail merchandise hierarchy across ready-to-wear, leather goods, footwear, and beauty.
- **Granularity:** One record per luxury SKU.
- **Total Record Count:** **115 rows** (114 active SKUs + 1 Unknown row)

| Column Name | Data Type | Nullable | Key Type | Description | Example Value |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `ProductKey` | `INT` | No | **PK** | Product surrogate key (`-1` for Unknown member fallback). | `101` |
| `SKU` | `VARCHAR` | No | Attribute | Unique stock keeping unit code. | `RTW-BLZ-LIN-001` |
| `ProductName` | `VARCHAR` | No | Attribute | Branded luxury product catalog title. | `Structured Linen Blazer Ivory` |
| `Department` | `VARCHAR` | No | Attribute | Top-level merchandising division (Apparel, Leather Goods, Footwear). | `Apparel` |
| `Category` | `VARCHAR` | No | Attribute | Mid-level merchandise classification (Tailoring, Handbags, Sneakers).| `Outerwear` |
| `SubCategory` | `VARCHAR` | No | Attribute | Granular product style categorization (Blazers, Totes, Loafers). | `Blazers` |
| `BrandTier` | `VARCHAR` | No | Attribute | Luxury positioning tier (Haute Horlogerie, Luxury Prestige, Core Luxury).| `Luxury Prestige` |
| `BaseRetailPriceAED` | `DECIMAL(10,2)` | No | Metric | Master retail list price in AED before discounts. | `1450.00` |
| `BaseUnitCostAED` | `DECIMAL(10,2)` | No | Metric | Standard landed unit cost snapshot in AED. | `450.00` |
| `ElasticityCoefficient`| `DECIMAL(4,2)` | No | Parameter | Econometric price elasticity coefficient ($\% \Delta Q / \% \Delta P$). | `-1.45` |

---

## 2. Authoritative 43 DAX Measures Catalog

All 43 DAX measures reside in the `_Measures` table within the Tabular Model (`tabular/model.bim`), automated via [`scripts/Apply_Tabular_Metadata.cs`](file:///r:/Projects/Omnichannel%20Retail%20Control%20Tower/scripts/Apply_Tabular_Metadata.cs).

### Folder 01: Financial & Commercial Core (10 Measures)
| Measure Name | DAX Expression | Format String | Description |
| :--- | :--- | :--- | :--- |
| `[Units Sold]` | `SUM(Fact_POS_Transactions[UnitsSold])` | `#,##0` | Total units sold across all POS checkouts. |
| `[Gross Sales (AED)]` | `SUM(Fact_POS_Transactions[GrossSalesAmt])` | `AED #,##0.00` | Total list sales before promotions. |
| `[Markdown Discount (AED)]`| `SUM(Fact_POS_Transactions[DiscountAmt])` | `AED #,##0.00` | Total promotional concessions. |
| `[Net Revenue (AED)]` | `SUM(Fact_POS_Transactions[NetSalesAmt])` | `AED #,##0.00` | Net revenue realized after discounts. |
| `[Total COGS (AED)]` | `SUM(Fact_POS_Transactions[ExtendedCostAmt])` | `AED #,##0.00` | Total landed Cost of Goods Sold. |
| `[Gross Margin (AED)]` | `[Net Revenue (AED)] - [Total COGS (AED)]` | `AED #,##0.00` | Realized gross margin in AED. |
| `[Gross Margin %]` | `DIVIDE([Gross Margin (AED)], [Net Revenue (AED)], 0)` | `0.0%` | Gross margin % of net revenue (69.73%). |
| `[Markdown Depth %]` | `DIVIDE([Markdown Discount (AED)], [Gross Sales (AED)], 0)` | `0.0%` | Promotional discount depth % (6.09%). |
| `[Average Unit Retail (AUR)]`| `DIVIDE([Net Revenue (AED)], [Units Sold], 0)` | `AED #,##0.00` | Realized selling price per unit sold (AED 1,350.91). |
| `[Average Unit Cost (AUC)]` | `DIVIDE([Total COGS (AED)], [Units Sold], 0)` | `AED #,##0.00` | Realized landed cost per unit sold (AED 408.90). |

---

### Folder 02: Semi-Additive Inventory Snapshots (4 Measures)
| Measure Name | DAX Expression Summary | Format String | Description |
| :--- | :--- | :--- | :--- |
| `[Ending On Hand Units]` | `CALCULATE(SUM(Fact_Daily_Inventory[OnHandUnits]), Fact_Daily_Inventory[SnapshotDateKey] = TargetDateKey, REMOVEFILTERS(Dim_Date))` | `#,##0` | Closing on-hand stock for selected period. |
| `[Ending In-Transit Units]` | `CALCULATE(SUM(Fact_Daily_Inventory[InTransitUnits]), ...)` | `#,##0` | Closing in-transit stock en route to stores. |
| `[Ending Inventory Cost (AED)]`| `CALCULATE(SUM(Fact_Daily_Inventory[InventoryCostValueAmt]), ...)` | `AED #,##0.00` | Closing inventory valuation at landed cost. |
| `[Average Inventory Cost (AED)]`| `AVERAGEX(KEEPFILTERS(VALUES(Dim_Date[DateKey])), CALCULATE(SUM(...)))` | `AED #,##0.00` | Daily average inventory value across selection. |

---

### Folder 03: Asset Productivity & Supply Velocity (5 Measures)
| Measure Name | DAX Expression Summary | Format String | Description |
| :--- | :--- | :--- | :--- |
| `[Sell-Through Rate %]` | `DIVIDE([Units Sold], [Units Sold] + [Ending On Hand Units], 0)` | `0.0%` | Commercial sell-through velocity percentage. |
| `[Units Sold Trailing 4W]` | `CALCULATE([Units Sold], DATESINPERIOD(Dim_Date[FullDate], CurrentMaxDate, -28, DAY))` | `#,##0` | 28-day trailing unit sales volume. |
| `[Weekly Sales Run Rate (T4W)]`| `DIVIDE([Units Sold Trailing 4W], 4, 0)` | `#,##0.0` | Weekly sales run rate smoothing footfall spikes. |
| `[Weeks of Supply]` | `DIVIDE([Ending On Hand Units], [Weekly Sales Run Rate (T4W)], BLANK())` | `0.0` | Forward stock cover in weeks. |
| `[GMROI]` | `DIVIDE([Annualized Margin], [Average Inventory Cost (AED)], 0)` | `0.00` | Gross Margin Return on Investment. |

---

### Folder 04: Time Intelligence & Variance (4 Measures)
| Measure Name | DAX Expression Summary | Format String | Description |
| :--- | :--- | :--- | :--- |
| `[Net Revenue MTD]` | `TOTALMTD([Net Revenue (AED)], Dim_Date[FullDate])` | `AED #,##0.00` | Month-to-date realized net revenue. |
| `[Net Revenue YTD]` | `TOTALYTD([Net Revenue (AED)], Dim_Date[FullDate])` | `AED #,##0.00` | Year-to-date realized net revenue. |
| `[Net Revenue Prior Period]` | `CALCULATE([Net Revenue (AED)], DATESBETWEEN(...))` | `AED #,##0.00` | Revenue for comparative prior period of equal length. |
| `[Net Revenue Growth %]` | `DIVIDE([Net Revenue] - [Prior], [Prior], BLANK())` | `0.0%` | Period-over-period percentage growth. |

---

### Folder 05: Prescriptive Stock Balancing (6 Measures)
| Measure Name | DAX Expression Summary | Format String | Description |
| :--- | :--- | :--- | :--- |
| `[Stock Health Classification]` | Evaluates STR % and WOS into 4 categorical states | Text | Stock health (`CRITICAL_STOCKOUT_RISK`, `OVERSTOCK_CASH_TRAP`, etc.). |
| `[Target Safety Stock Units]` | `CEILING([Weekly Sales Run Rate (T4W)] * 4, 1)` | `#,##0` | Target safety buffer representing 4 weeks of cover. |
| `[Inter-Mall Net Unit Variance]`| `[Ending On Hand Units] - [Target Safety Stock Units]` | `#,##0` | Net unit surplus (+) or deficit (-) vs safety buffer. |
| `[Inter-Mall Rebalance Directive]`| Formats categorical directive string with transfer volume | Text | Actionable transfer recommendation (Push vs Pull). |
| `[Merchandising Action Trigger]`| Multi-factor trigger evaluating STR, WOS, and Elasticity | Text | Rebalance, markdown liquidation, or e-com reallocation. |
| `[Days of Inventory Remaining]` | `[Weeks of Supply] * 7` | `0` | Estimated days until shelf stockout. |

---

### Folder 06: Markdown Simulation & Sensitivity (14 Measures)
| Measure Name | DAX Expression Summary | Format String | Description |
| :--- | :--- | :--- | :--- |
| `[Simulated Discount %]` | `SELECTEDVALUE('Markdown_Scenario'[ScenarioDiscountPct], 0.00)` | `0.0%` | Harvested discount percentage from parameter table. |
| `[Effective Elasticity Coeff]`| `DIVIDE(SUMX(Dim_Product, [Units Sold] * Elasticity), [Units Sold], -1.50)` | `0.00` | Volume-weighted elasticity coefficient. |
| `[Simulated Volume Lift %]` | `-1 * ([Effective Elasticity Coeff] * [Simulated Discount %])` | `0.0%` | Econometric projected demand volume lift %. |
| `[Simulated Units Sold]` | `[Units Sold] * (1 + [Simulated Volume Lift %])` | `#,##0` | Total projected sales volume under discount scenario. |
| `[Incremental Units Cleared]` | `MAX(0, [Simulated Units Sold] - [Units Sold])` | `#,##0` | Additional units cleared beyond baseline. |
| `[Simulated Effective AUR (AED)]`| `[Average Unit Retail (AUR)] * (1 - [Simulated Discount %])` | `AED #,##0.00` | Projected realized average selling price per unit. |
| `[Simulated Net Revenue (AED)]`| `[Simulated Units Sold] * [Simulated Effective AUR (AED)]` | `AED #,##0.00` | Projected net revenue under markdown scenario. |
| `[Simulated Total COGS (AED)]` | `[Simulated Units Sold] * [Average Unit Cost (AUC)]` | `AED #,##0.00` | Projected COGS for simulated volume. |
| `[Simulated Gross Margin (AED)]`| `[Simulated Net Revenue] - [Simulated Total COGS]` | `AED #,##0.00` | Projected gross margin realized in AED. |
| `[Gross Margin Delta (AED)]` | `[Simulated Gross Margin] - [Gross Margin]` | `AED #,##0.00` | Profit accretion (+) or dilution (-) vs actuals. |
| `[Working Capital Released (AED)]`| `[Incremental Units Cleared] * [Average Unit Cost (AUC)]` | `AED #,##0.00` | Landed inventory cost converted to liquid cash. |
| `[Breakeven Unit Volume]` | `DIVIDE([Gross Margin (AED)], [Sim AUR] - [AUC], 0)` | `#,##0` | Unit volume required to match 100% baseline profit. |
| `[Breakeven Unit Gap]` | `[Simulated Units Sold] - [Breakeven Unit Volume]` | `#,##0` | Safety margin between simulated and breakeven units. |
| `[Breakeven Feasibility Verdict]`| Categorical decision gate evaluating margin delta | Text | Verdict (`ACCRETIVE PROFIT YIELD`, `CAPITAL TRADE-OFF`, etc.). |
