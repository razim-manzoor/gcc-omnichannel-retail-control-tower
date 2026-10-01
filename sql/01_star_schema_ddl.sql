-- ==============================================================================
-- Enterprise Dimensional Star Schema DDL Specification
-- Domain: GCC Omnichannel Retail & Markdown Elasticity Control Tower
-- Target Architecture: Tabular Engine (Power BI / VertiPaq) & SQL Lakehouse / Warehouse
-- Methodology: Kimball Dimensional Modeling (Conformed Dimensions, Strict Fact Grain)
-- Compatible with: PostgreSQL, DuckDB, Microsoft Fabric / Synapse, Snowflake
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. CONFORMED DIMENSIONS
-- ------------------------------------------------------------------------------

-- Dim_Date: 1 record per Gregorian calendar day
CREATE TABLE IF NOT EXISTS Dim_Date (
    DateKey                 INTEGER NOT NULL,                     -- YYYYMMDD surrogate integer key (e.g. 20260315, -1 for Unknown)
    FullDate                DATE NOT NULL,                        -- Gregorian Calendar Date
    FiscalYear              INTEGER NOT NULL,                     -- e.g. 2026
    FiscalQuarter           VARCHAR(10) NOT NULL,                 -- 'Q1', 'Q2', 'Q3', 'Q4'
    FiscalMonthNum          INTEGER NOT NULL,                     -- 1 to 12
    FiscalMonthName         VARCHAR(20) NOT NULL,                 -- 'January' - 'December'
    RetailWeekNum           INTEGER NOT NULL,                     -- 1 to 52 (NRF 4-5-4 Standard)
    DayOfWeekName           VARCHAR(20) NOT NULL,                 -- 'Sunday', 'Monday', etc.
    DayOfWeekNum            INTEGER NOT NULL,                     -- 1 (Sunday/Monday) depending on standard
    IsWeekendGCC            BOOLEAN NOT NULL DEFAULT FALSE,       -- 1 for Friday/Saturday/Sunday per UAE/GCC commercial calendar
    IsRetailPeakSeason      BOOLEAN NOT NULL DEFAULT FALSE,       -- 1 for Ramadan, Eid al-Fitr, Eid al-Adha, DSF, White Friday
    CONSTRAINT PK_Dim_Date PRIMARY KEY (DateKey)
);

-- Dim_Store: 1 record per physical retail store or fulfillment warehouse/channel
CREATE TABLE IF NOT EXISTS Dim_Store (
    StoreKey                INTEGER NOT NULL,                     -- Surrogate integer key (-1 for Unknown)
    StoreCode               VARCHAR(50) NOT NULL,                 -- Natural Key: DXB-TDM-01, DXB-MOE-02, ECOM-UAE-01
    StoreName               VARCHAR(150) NOT NULL,                -- The Dubai Mall Flagship, Yas Mall Abu Dhabi
    Channel                 VARCHAR(50) NOT NULL,                 -- Physical Flagship, Physical Boutique, Digital E-Commerce
    Emirate                 VARCHAR(50) NOT NULL,                 -- Dubai, Abu Dhabi, Sharjah, etc.
    Country                 VARCHAR(50) NOT NULL,                 -- United Arab Emirates, Saudi Arabia
    GrossLeasableAreaSqFt   INTEGER NOT NULL DEFAULT 0,           -- Physical footprint for sales density calculation (AED/sq ft)
    ClusterTier             VARCHAR(50) NOT NULL,                 -- Flagship, Boutique, Outlet, Fulfillment Hub
    HubFulfillmentEligible  BOOLEAN NOT NULL DEFAULT FALSE,       -- 1 if store can transfer/fulfill omnichannel orders, 0 if outlet-only
    CONSTRAINT PK_Dim_Store PRIMARY KEY (StoreKey)
);

-- Dim_Product: 1 record per unique Stock Keeping Unit (SKU). Flattened hierarchy (No snowflaking).
CREATE TABLE IF NOT EXISTS Dim_Product (
    ProductKey              INTEGER NOT NULL,                     -- Surrogate integer key (-1 for Unknown)
    SKU                     VARCHAR(100) NOT NULL,                -- Natural Key: RTW-BLZ-LIN-001
    ProductName             VARCHAR(255) NOT NULL,                -- Unstructured Linen Blazer Sand
    Department              VARCHAR(100) NOT NULL,                -- Apparel, Footwear, Accessories, Beauty
    Category                VARCHAR(100) NOT NULL,                -- Menswear, Womenswear, Leather Goods
    SubCategory             VARCHAR(100) NOT NULL,                -- Tailored Jackets, Sneakers, Tote Bags
    Brand                   VARCHAR(100) NOT NULL,                -- Private Label Atelier, Concession Brand A
    BrandTier               VARCHAR(50) NOT NULL,                 -- Ultra-Luxury, Bridge Luxury, Mass Premium
    BaseUnitCostAED         DECIMAL(19, 4) NOT NULL DEFAULT 0.0,  -- Landed cost price per unit in AED
    BaseRetailPriceAED      DECIMAL(19, 4) NOT NULL DEFAULT 0.0,  -- First-ticket full price (MSRP) in AED
    ElasticityCoefficient   DECIMAL(5, 2) NOT NULL DEFAULT -1.0,  -- Product-specific price elasticity factor (e.g. -1.80, -0.65)
    CONSTRAINT PK_Dim_Product PRIMARY KEY (ProductKey)
);

-- ------------------------------------------------------------------------------
-- 2. FACT TABLES
-- ------------------------------------------------------------------------------

-- Fact_POS_Transactions: Transactional Fact (1 record per SKU line item per completed checkout/basket)
CREATE TABLE IF NOT EXISTS Fact_POS_Transactions (
    TransactionLineKey      BIGINT NOT NULL,                      -- Primary Key
    DateKey                 INTEGER NOT NULL,                     -- FK -> Dim_Date[DateKey]
    StoreKey                INTEGER NOT NULL,                     -- FK -> Dim_Store[StoreKey]
    ProductKey              INTEGER NOT NULL,                     -- FK -> Dim_Product[ProductKey]
    BasketID                VARCHAR(100) NOT NULL,                -- Degenerate Dimension: Order/Receipt number
    PaymentType             VARCHAR(50) NOT NULL,                 -- Degenerate Dimension: CreditCard, ApplePay, Cash, Tabby_BNPL
    UnitsSold               INTEGER NOT NULL,                     -- Additive: Quantity sold
    GrossSalesAmt           DECIMAL(19, 4) NOT NULL,              -- Additive: UnitsSold * Dim_Product[BaseRetailPriceAED]
    DiscountAmt             DECIMAL(19, 4) NOT NULL DEFAULT 0.0,  -- Additive: Promotional or markdown amount deducted
    NetSalesAmt             DECIMAL(19, 4) NOT NULL,              -- Additive: GrossSalesAmt - DiscountAmt
    ExtendedCostAmt         DECIMAL(19, 4) NOT NULL,              -- Additive: UnitsSold * UnitCostSnapshotAmt
    TaxAmtAED               DECIMAL(19, 4) NOT NULL DEFAULT 0.0,  -- Additive: 5% UAE VAT amount
    CONSTRAINT PK_Fact_POS_Transactions PRIMARY KEY (TransactionLineKey),
    CONSTRAINT FK_POS_Date FOREIGN KEY (DateKey) REFERENCES Dim_Date(DateKey),
    CONSTRAINT FK_POS_Store FOREIGN KEY (StoreKey) REFERENCES Dim_Store(StoreKey),
    CONSTRAINT FK_POS_Product FOREIGN KEY (ProductKey) REFERENCES Dim_Product(ProductKey)
);

-- Fact_Daily_Inventory: Periodic Snapshot Fact (1 record per SKU per Store per Calendar Day Closing Balance)
CREATE TABLE IF NOT EXISTS Fact_Daily_Inventory (
    InventorySnapshotKey    BIGINT NOT NULL,                      -- Primary Key
    SnapshotDateKey         INTEGER NOT NULL,                     -- FK -> Dim_Date[DateKey]
    StoreKey                INTEGER NOT NULL,                     -- FK -> Dim_Store[StoreKey]
    ProductKey              INTEGER NOT NULL,                     -- FK -> Dim_Product[ProductKey]
    OnHandUnits             INTEGER NOT NULL DEFAULT 0,           -- Semi-Additive: Physical salable stock at end of day
    InTransitUnits          INTEGER NOT NULL DEFAULT 0,           -- Semi-Additive: Stock in-transit from DC/inter-mall transfer
    ReservedUnits           INTEGER NOT NULL DEFAULT 0,           -- Semi-Additive: Locked for click-and-collect / online fulfillment
    AvailableUnits          INTEGER NOT NULL DEFAULT 0,           -- Semi-Additive: OnHandUnits - ReservedUnits
    UnitCostSnapshotAmt     DECIMAL(19, 4) NOT NULL DEFAULT 0.0,  -- Landed unit cost at snapshot date
    InventoryCostValueAmt   DECIMAL(19, 4) NOT NULL DEFAULT 0.0,  -- Semi-Additive: OnHandUnits * UnitCostSnapshotAmt (Working Capital)
    CONSTRAINT PK_Fact_Daily_Inventory PRIMARY KEY (InventorySnapshotKey),
    CONSTRAINT FK_Inv_Date FOREIGN KEY (SnapshotDateKey) REFERENCES Dim_Date(DateKey),
    CONSTRAINT FK_Inv_Store FOREIGN KEY (StoreKey) REFERENCES Dim_Store(StoreKey),
    CONSTRAINT FK_Inv_Product FOREIGN KEY (ProductKey) REFERENCES Dim_Product(ProductKey)
);

-- ------------------------------------------------------------------------------
-- 3. DISCONNECTED PARAMETER TABLE (WHAT-IF SIMULATION)
-- ------------------------------------------------------------------------------

-- Markdown_Scenario: Simulation Parameter table with ZERO relational joins to fact tables
CREATE TABLE IF NOT EXISTS Markdown_Scenario (
    ScenarioDiscountPct     DECIMAL(4, 2) NOT NULL,               -- PK: 0.00, 0.05, 0.10, ..., 0.50
    DiscountDisplayLabel    VARCHAR(50) NOT NULL,                 -- '0% (Full Price)', '10% Off', '25% Off'
    SimulationSortOrder     INTEGER NOT NULL,                     -- 0, 1, 2, 3...
    CONSTRAINT PK_Markdown_Scenario PRIMARY KEY (ScenarioDiscountPct)
);

-- ------------------------------------------------------------------------------
-- 4. REFERENTIAL INTEGRITY (-1 FALLBACK MEMBERS)
-- ------------------------------------------------------------------------------

-- Seed Unknown Member for Dim_Date
INSERT INTO Dim_Date (
    DateKey, FullDate, FiscalYear, FiscalQuarter, FiscalMonthNum,
    FiscalMonthName, RetailWeekNum, DayOfWeekName, DayOfWeekNum,
    IsWeekendGCC, IsRetailPeakSeason
) VALUES (
    -1, '1900-01-01', 1900, 'N/A', 0,
    'Unknown', 0, 'Unknown', 0,
    FALSE, FALSE
) ON CONFLICT (DateKey) DO NOTHING;

-- Seed Unknown Member for Dim_Store
INSERT INTO Dim_Store (
    StoreKey, StoreCode, StoreName, Channel, Emirate, Country,
    GrossLeasableAreaSqFt, ClusterTier, HubFulfillmentEligible
) VALUES (
    -1, 'UNK', 'Unknown Store', 'Unknown', 'Unknown', 'Unknown',
    0, 'Unknown', FALSE
) ON CONFLICT (StoreKey) DO NOTHING;

-- Seed Unknown Member for Dim_Product
INSERT INTO Dim_Product (
    ProductKey, SKU, ProductName, Department, Category, SubCategory,
    Brand, BrandTier, BaseUnitCostAED, BaseRetailPriceAED, ElasticityCoefficient
) VALUES (
    -1, 'UNKNOWN-SKU', 'Unknown Product', 'Unknown', 'Unknown', 'Unknown',
    'Unknown', 'Unknown', 0.0000, 0.0000, 0.00
) ON CONFLICT (ProductKey) DO NOTHING;

-- Seed Markdown Simulation Scenarios
INSERT INTO Markdown_Scenario (ScenarioDiscountPct, DiscountDisplayLabel, SimulationSortOrder) VALUES
    (0.00, '0% (Full Price)', 0),
    (0.05, '5% Discount', 1),
    (0.10, '10% Discount', 2),
    (0.15, '15% Discount', 3),
    (0.20, '20% Discount', 4),
    (0.25, '25% Discount', 5),
    (0.30, '30% Discount', 6),
    (0.35, '35% Discount', 7),
    (0.40, '40% Discount', 8),
    (0.45, '45% Discount', 9),
    (0.50, '50% Clearance', 10)
ON CONFLICT (ScenarioDiscountPct) DO UPDATE
SET DiscountDisplayLabel = EXCLUDED.DiscountDisplayLabel,
    SimulationSortOrder = EXCLUDED.SimulationSortOrder;

-- ------------------------------------------------------------------------------
-- 5. PERFORMANCE INDEXES (FOR RELATIONAL WAREHOUSE QUERY ACCELERATION)
-- ------------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS IX_POS_DateKey ON Fact_POS_Transactions (DateKey);
CREATE INDEX IF NOT EXISTS IX_POS_StoreKey ON Fact_POS_Transactions (StoreKey);
CREATE INDEX IF NOT EXISTS IX_POS_ProductKey ON Fact_POS_Transactions (ProductKey);
CREATE INDEX IF NOT EXISTS IX_POS_BasketID ON Fact_POS_Transactions (BasketID);

CREATE INDEX IF NOT EXISTS IX_Inv_SnapshotDate ON Fact_Daily_Inventory (SnapshotDateKey);
CREATE INDEX IF NOT EXISTS IX_Inv_StoreKey ON Fact_Daily_Inventory (StoreKey);
CREATE INDEX IF NOT EXISTS IX_Inv_ProductKey ON Fact_Daily_Inventory (ProductKey);
