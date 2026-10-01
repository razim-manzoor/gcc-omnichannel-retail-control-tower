# Power Query (M Language) Ingestion & Transformation Guide

This folder contains the complete Power Query (M) transformation pipeline for importing the synthetic GCC Omnichannel Retail Control Tower datasets into Microsoft Power BI Desktop.

---

## 1. Setup in Power BI Desktop

### Step A: Define the `DataFolderPath` Parameter
1. Open **Power BI Desktop**.
2. Click **Transform Data** (Home Ribbon) to open the Power Query Editor.
3. In the Home Ribbon, select **Manage Parameters** > **New Parameter**:
   - **Name:** `DataFolderPath`
   - **Description:** Absolute path to the repository `data/` directory.
   - **Type:** `Text`
   - **Suggested Values:** `Any value`
   - **Current Value:** `R:\Projects\Omnichannel Retail Control Tower\data` (or your local path).
4. Click **OK**.

---

## 2. Ingesting Tables (6 Queries)

For each file below, click **New Source** > **Blank Query**, open the **Advanced Editor**, and paste the corresponding M code:

| Target Query Name | File | Description & Transformations |
| :--- | :--- | :--- |
| `Dim_Date` | [`Dim_Date.m`](./Dim_Date.m) | Date dimension with YYYYMMDD `DateKey`, Gregorian date typing, NRF 4-5-4 retail calendar, GCC weekend flags (`IsWeekendGCC`), and peak season indicators (`IsRetailPeakSeason`). |
| `Dim_Store` | [`Dim_Store.m`](./Dim_Store.m) | Store dimension with `StoreKey`, physical mall & digital DC metadata, GLA sq ft, and fulfillment eligibility flags. |
| `Dim_Product` | [`Dim_Product.m`](./Dim_Product.m) | Product hierarchy dimension with `ProductKey`, department, brand tier, base cost/retail, and price elasticity coefficient. |
| `Fact_POS_Transactions` | [`Fact_POS_Transactions.m`](./Fact_POS_Transactions.m) | 115,000+ transaction lines with basket IDs, payment tenders, units sold, gross/net sales, discounts, landed cost, and VAT. |
| `Fact_Daily_Inventory` | [`Fact_Daily_Inventory.m`](./Fact_Daily_Inventory.m) | 53,000+ daily periodic closing inventory snapshots with on-hand, in-transit, reserved, available units, and cost valuation. |
| `Markdown_Scenario` | [`Markdown_Scenario.m`](./Markdown_Scenario.m) | Disconnected parameter table (0% to 50% discount tiers) for the What-If simulation slider. |

---

## 3. Applying Changes & Building Relationships

1. Click **Close & Apply** in the Power Query Editor.
2. In Power BI Model View, verify single-direction (1-to-many) relationships:
   - `Dim_Date[DateKey] (1) ---> (*) Fact_POS_Transactions[DateKey]`
   - `Dim_Store[StoreKey] (1) ---> (*) Fact_POS_Transactions[StoreKey]`
   - `Dim_Product[ProductKey] (1) ---> (*) Fact_POS_Transactions[ProductKey]`
   - `Dim_Date[DateKey] (1) ---> (*) Fact_Daily_Inventory[SnapshotDateKey]`
   - `Dim_Store[StoreKey] (1) ---> (*) Fact_Daily_Inventory[StoreKey]`
   - `Dim_Product[ProductKey] (1) ---> (*) Fact_Daily_Inventory[ProductKey]`
   - `Markdown_Scenario` remains **disconnected** (0 relationships).
