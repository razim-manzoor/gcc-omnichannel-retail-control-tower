-- ==============================================================================
-- Mock Data Seed Script: GCC Omnichannel Retail Control Tower
-- Provides realistic sample data for Dim_Date, Dim_Store, Dim_Product,
-- Fact_POS_Transactions, Fact_Daily_Inventory, and Markdown_Scenario
-- ==============================================================================

-- 1. SEED DIM_DATE (March 2026 Focus Window + Key Peak Season Dates)
INSERT INTO Dim_Date (
    DateKey, FullDate, FiscalYear, FiscalQuarter, FiscalMonthNum,
    FiscalMonthName, RetailWeekNum, DayOfWeekName, DayOfWeekNum,
    IsWeekendGCC, IsRetailPeakSeason
) VALUES
    (20260312, '2026-03-12', 2026, 'Q1', 3, 'March', 11, 'Thursday', 5, FALSE, TRUE),
    (20260313, '2026-03-13', 2026, 'Q1', 3, 'March', 11, 'Friday', 6, TRUE, TRUE),
    (20260314, '2026-03-14', 2026, 'Q1', 3, 'March', 11, 'Saturday', 7, TRUE, TRUE),
    (20260315, '2026-03-15', 2026, 'Q1', 3, 'March', 11, 'Sunday', 1, TRUE, TRUE),
    (20260316, '2026-03-16', 2026, 'Q1', 3, 'March', 12, 'Monday', 2, FALSE, TRUE),
    (20260317, '2026-03-17', 2026, 'Q1', 3, 'March', 12, 'Tuesday', 3, FALSE, TRUE),
    (20260318, '2026-03-18', 2026, 'Q1', 3, 'March', 12, 'Wednesday', 4, FALSE, TRUE)
ON CONFLICT (DateKey) DO NOTHING;

-- 2. SEED DIM_STORE (GCC Flagships, Boutiques, Outlets, and Central E-Commerce DC)
INSERT INTO Dim_Store (
    StoreKey, StoreCode, StoreName, Channel, Emirate, Country,
    GrossLeasableAreaSqFt, ClusterTier, HubFulfillmentEligible
) VALUES
    (1, 'DXB-TDM-01', 'The Dubai Mall Flagship', 'Physical Flagship', 'Dubai', 'United Arab Emirates', 12500, 'Flagship', TRUE),
    (2, 'DXB-MOE-02', 'Mall of the Emirates Boutique', 'Physical Boutique', 'Dubai', 'United Arab Emirates', 6500, 'Boutique', TRUE),
    (3, 'AUH-YAS-01', 'Yas Mall Abu Dhabi', 'Physical Boutique', 'Abu Dhabi', 'United Arab Emirates', 7200, 'Boutique', TRUE),
    (4, 'DXB-OUT-01', 'Dubai Outlet Mall Clearance', 'Physical Outlet', 'Dubai', 'United Arab Emirates', 4500, 'Outlet', FALSE),
    (5, 'ECOM-UAE-01', 'UAE Central DC & Digital Hub', 'Digital E-Commerce', 'Dubai', 'United Arab Emirates', 45000, 'Fulfillment Hub', TRUE)
ON CONFLICT (StoreKey) DO NOTHING;

-- 3. SEED DIM_PRODUCT (Multi-Tier Portfolio: Ultra-Luxury, Bridge Luxury, Mass Premium)
-- With authentic retail price elasticity coefficients
INSERT INTO Dim_Product (
    ProductKey, SKU, ProductName, Department, Category, SubCategory,
    Brand, BrandTier, BaseUnitCostAED, BaseRetailPriceAED, ElasticityCoefficient
) VALUES
    (101, 'RTW-BLZ-LIN-001', 'Unstructured Linen Blazer Sand', 'Apparel', 'Menswear', 'Tailored Jackets', 'Private Label Atelier', 'Bridge Luxury', 450.0000, 1450.0000, -1.80),
    (102, 'LEA-TOT-GLD-002', 'Grain Calfskin Everyday Tote Noir', 'Accessories', 'Leather Goods', 'Tote Bags', 'Maison Rivoli', 'Ultra-Luxury', 1850.0000, 5200.0000, -0.65),
    (103, 'FTW-SNK-LTH-003', 'Heritage Tennis Sneaker White', 'Footwear', 'Menswear', 'Sneakers', 'AeroSport Milano', 'Mass Premium', 180.0000, 650.0000, -2.20),
    (104, 'DRS-SLK-EVN-004', 'Bias-Cut Silk Evening Gown Emerald', 'Apparel', 'Womenswear', 'Dresses', 'Private Label Atelier', 'Bridge Luxury', 620.0000, 2100.0000, -1.40),
    (105, 'BTY-EXT-OUD-005', 'Desert Amber Extrait de Parfum 100ml', 'Beauty', 'Fragrance', 'Niche Perfumery', 'Sultanate Parfums', 'Ultra-Luxury', 320.0000, 1150.0000, -0.45),
    (106, 'RTW-TEE-COT-006', 'Supima Heavyweight Cotton T-Shirt', 'Apparel', 'Menswear', 'T-Shirts', 'Basics Lab', 'Mass Premium', 45.0000, 195.0000, -2.50)
ON CONFLICT (ProductKey) DO NOTHING;

-- 4. SEED FACT_POS_TRANSACTIONS (Checkout baskets with omnichannel payment types)
INSERT INTO Fact_POS_Transactions (
    TransactionLineKey, DateKey, StoreKey, ProductKey, BasketID,
    PaymentType, UnitsSold, GrossSalesAmt, DiscountAmt, NetSalesAmt,
    ExtendedCostAmt, TaxAmtAED
) VALUES
    -- Basket 1: Dubai Mall Flagship (Blazer + Sneaker) via ApplePay
    (1001, 20260313, 1, 101, 'BSK-DXB-0001', 'ApplePay', 1, 1450.0000, 0.0000, 1450.0000, 450.0000, 72.5000),
    (1002, 20260313, 1, 103, 'BSK-DXB-0001', 'ApplePay', 1, 650.0000, 0.0000, 650.0000, 180.0000, 32.5000),
    
    -- Basket 2: Mall of the Emirates (Ultra-Luxury Tote) via CreditCard
    (1003, 20260313, 2, 102, 'BSK-MOE-0002', 'CreditCard', 1, 5200.0000, 0.0000, 5200.0000, 1850.0000, 260.0000),
    
    -- Basket 3: E-Commerce Digital Hub (Silk Gown + Perfume) via Tabby BNPL
    (1004, 20260314, 5, 104, 'BSK-ECM-0003', 'Tabby_BNPL', 1, 2100.0000, 210.0000, 1890.0000, 620.0000, 94.5000),
    (1005, 20260314, 5, 105, 'BSK-ECM-0003', 'Tabby_BNPL', 2, 2300.0000, 0.0000, 2300.0000, 640.0000, 115.0000),
    
    -- Basket 4: Yas Mall Abu Dhabi (2x Linen Blazer with 15% VIP discount) via ApplePay
    (1006, 20260315, 3, 101, 'BSK-YAS-0004', 'ApplePay', 2, 2900.0000, 435.0000, 2465.0000, 900.0000, 123.2500),
    
    -- Basket 5: Dubai Mall Flagship (4x Cotton T-Shirts) via Cash
    (1007, 20260315, 1, 106, 'BSK-DXB-0005', 'Cash', 4, 780.0000, 78.0000, 702.0000, 180.0000, 35.1000),
    
    -- Basket 6: E-Commerce Digital Hub (3x Sneakers) via CreditCard
    (1008, 20260315, 5, 103, 'BSK-ECM-0006', 'CreditCard', 3, 1950.0000, 195.0000, 1755.0000, 540.0000, 87.7500)
ON CONFLICT (TransactionLineKey) DO NOTHING;

-- 5. SEED FACT_DAILY_INVENTORY (Daily Closing Inventory Snapshots)
INSERT INTO Fact_Daily_Inventory (
    InventorySnapshotKey, SnapshotDateKey, StoreKey, ProductKey,
    OnHandUnits, InTransitUnits, ReservedUnits, AvailableUnits,
    UnitCostSnapshotAmt, InventoryCostValueAmt
) VALUES
    -- March 14 Snapshots
    (5001, 20260314, 1, 101, 18, 5, 2, 16, 450.0000, 8100.0000),
    (5002, 20260314, 1, 102, 4, 0, 1, 3, 1850.0000, 7400.0000),
    (5003, 20260314, 2, 101, 10, 2, 0, 10, 450.0000, 4500.0000),
    (5004, 20260314, 2, 102, 3, 0, 0, 3, 1850.0000, 5550.0000),
    (5005, 20260314, 5, 101, 85, 20, 15, 70, 450.0000, 38250.0000),
    (5006, 20260314, 5, 102, 25, 5, 4, 21, 1850.0000, 46250.0000),

    -- March 15 Snapshots (Reflecting sales and stock position changes)
    (5007, 20260315, 1, 101, 17, 5, 1, 16, 450.0000, 7650.0000),
    (5008, 20260315, 1, 102, 4, 0, 0, 4, 1850.0000, 7400.0000),
    (5009, 20260315, 1, 106, 46, 10, 2, 44, 45.0000, 2070.0000),
    (5010, 20260315, 2, 101, 10, 2, 0, 10, 450.0000, 4500.0000),
    (5011, 20260315, 3, 101, 8, 4, 1, 7, 450.0000, 3600.0000),
    (5012, 20260315, 5, 101, 85, 20, 12, 73, 450.0000, 38250.0000),
    (5013, 20260315, 5, 103, 112, 30, 8, 104, 180.0000, 20160.0000)
ON CONFLICT (InventorySnapshotKey) DO NOTHING;
