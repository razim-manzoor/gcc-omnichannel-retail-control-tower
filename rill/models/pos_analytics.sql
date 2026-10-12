-- Model: pos_analytics
-- Joins Kimball Star Schema dimensions to Fact_POS_Transactions
SELECT
  f.TransactionLineKey,
  f.BasketID,
  f.BasketID AS TransactionID,
  d.FullDate AS TransactionDate,
  CAST(d.FullDate AS TIMESTAMP) AS TransactionTimestamp,
  d.FiscalYear,
  d.FiscalQuarter,
  d.FiscalMonthName,
  d.RetailWeekNum,
  d.DayOfWeekName,
  d.IsWeekendGCC,
  d.IsRetailPeakSeason,
  s.StoreCode,
  s.StoreName,
  s.Channel AS ChannelType,
  s.Emirate,
  s.Emirate AS City,
  s.Country,
  s.ClusterTier,
  p.SKU,
  p.ProductName,
  p.Department,
  p.Category,
  p.SubCategory,
  p.Brand,
  p.BrandTier,
  p.ElasticityCoefficient,
  f.PaymentType,
  f.UnitsSold,
  f.GrossSalesAmt,
  f.DiscountAmt,
  f.NetSalesAmt,
  f.ExtendedCostAmt AS TotalCOGS,
  (f.NetSalesAmt - f.ExtendedCostAmt) AS GrossMarginAmt,
  f.TaxAmtAED,
  CASE WHEN f.GrossSalesAmt > 0 THEN (f.DiscountAmt / f.GrossSalesAmt) ELSE 0 END AS MarkdownRate,
  CASE WHEN f.DiscountAmt > 0 THEN true ELSE false END AS IsMarkdown
FROM pos_transactions f
LEFT JOIN dim_date d ON f.DateKey = d.DateKey
LEFT JOIN dim_store s ON f.StoreKey = s.StoreKey
LEFT JOIN dim_product p ON f.ProductKey = p.ProductKey
