-- Model: inventory_analytics
-- Joins Kimball Star Schema dimensions to Fact_Daily_Inventory
SELECT
  i.InventorySnapshotKey,
  i.SnapshotDateKey,
  d.FullDate AS SnapshotDate,
  CAST(d.FullDate AS TIMESTAMP) AS SnapshotTimestamp,
  d.FiscalYear,
  d.FiscalQuarter,
  d.FiscalMonthName,
  d.RetailWeekNum,
  s.StoreCode,
  s.StoreName,
  s.Channel AS ChannelType,
  s.Emirate,
  s.Emirate AS City,
  s.Country,
  p.SKU,
  p.ProductName,
  p.Department,
  p.Category,
  p.SubCategory,
  p.Brand,
  p.BaseRetailPriceAED,
  p.BaseUnitCostAED,
  i.OnHandUnits,
  i.InTransitUnits,
  i.ReservedUnits,
  i.AvailableUnits,
  i.UnitCostSnapshotAmt,
  i.InventoryCostValueAmt,
  i.InventoryCostValueAmt AS InventoryCostValue,
  (i.OnHandUnits * p.BaseRetailPriceAED) AS InventoryRetailValueAmt,
  (i.OnHandUnits * p.BaseRetailPriceAED) AS InventoryRetailValue
FROM daily_inventory i
LEFT JOIN dim_date d ON i.SnapshotDateKey = d.DateKey
LEFT JOIN dim_store s ON i.StoreKey = s.StoreKey
LEFT JOIN dim_product p ON i.ProductKey = p.ProductKey
