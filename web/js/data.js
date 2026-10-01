/**
 * GCC Omnichannel Retail Control Tower - Core Data Repository
 * Strictly aligned with Kimball Star Schema & DuckDB Semantic Layer
 */

export const rawProducts = [
  { key: 101, sku: 'RTW-BLZ-LIN-001', name: 'Unstructured Linen Blazer Sand', dept: 'Apparel', cat: 'Menswear', subcat: 'Tailored Jackets', cost: 450, price: 1450, elasticity: -1.80, baseUnits: 1592 },
  { key: 102, sku: 'LEA-TOT-GLD-002', name: 'Grain Calfskin Everyday Tote Noir', dept: 'Accessories', cat: 'Leather Goods', subcat: 'Tote Bags', cost: 1850, price: 5200, elasticity: -0.65, baseUnits: 630 },
  { key: 103, sku: 'FTW-SNK-LTH-003', name: 'Heritage Tennis Sneaker White', dept: 'Footwear', cat: 'Menswear', subcat: 'Sneakers', cost: 180, price: 650, elasticity: -2.20, baseUnits: 3420 },
  { key: 104, sku: 'DRS-SLK-EVN-004', name: 'Bias-Cut Silk Evening Gown Emerald', dept: 'Apparel', cat: 'Womenswear', subcat: 'Dresses', cost: 620, price: 2100, elasticity: -1.40, baseUnits: 1180 },
  { key: 105, sku: 'BTY-EXT-OUD-005', name: 'Desert Amber Extrait de Parfum 100ml', dept: 'Beauty', cat: 'Fragrance', subcat: 'Niche Perfumery', cost: 320, price: 1150, elasticity: -0.45, baseUnits: 890 },
  { key: 106, sku: 'RTW-TEE-COT-006', name: 'Supima Heavyweight Cotton T-Shirt', dept: 'Apparel', cat: 'Menswear', subcat: 'T-Shirts', cost: 45, price: 195, elasticity: -2.50, baseUnits: 4210 }
];

export const rawStores = [
  { key: 1, code: 'DXB-TDM-01', name: 'The Dubai Mall Flagship', channel: 'Physical Flagship', emirate: 'Dubai' },
  { key: 2, code: 'DXB-MOE-02', name: 'Mall of the Emirates Boutique', channel: 'Physical Boutique', emirate: 'Dubai' },
  { key: 3, code: 'AUH-YAS-01', name: 'Yas Mall Abu Dhabi', channel: 'Physical Boutique', emirate: 'Abu Dhabi' },
  { key: 4, code: 'DXB-OUT-01', name: 'Dubai Outlet Mall Clearance', channel: 'Physical Outlet', emirate: 'Dubai' },
  { key: 5, code: 'ECOM-UAE-01', name: 'UAE Central DC & Digital Hub', channel: 'Digital E-Commerce', emirate: 'Dubai' },
  { key: 6, code: 'AUH-GAL-02', name: 'The Galleria Al Maryah Island', channel: 'Physical Flagship', emirate: 'Abu Dhabi' },
  { key: 7, code: 'JED-RSM-01', name: 'Red Sea Mall Flagship Jeddah', channel: 'Physical Flagship', emirate: 'Makkah' },
  { key: 8, code: 'RUH-KGC-01', name: 'Kingdom Centre Flagship Riyadh', channel: 'Physical Flagship', emirate: 'Riyadh' }
];

export const initialInventoryPositions = [
  { storeCode: 'AUH-YAS-01', storeName: 'Yas Mall Abu Dhabi', sku: 'RTW-BLZ-LIN-001', prodName: 'Unstructured Linen Blazer Sand', dept: 'Apparel', subcat: 'Tailored Jackets', onHand: 8, runRate: 0.50, str: 20.0, wos: 16.0, targetSS: 2, unitCost: 450, gmroi: 2.15, status: 'OVERSTOCK_CASH_TRAP', directive: '📦 PUSH INVENTORY: Surplus of 6 units. Dispatch to The Dubai Mall or trigger Tier-1 markdown.' },
  { storeCode: 'DXB-TDM-01', storeName: 'The Dubai Mall Flagship', sku: 'FTW-SNK-LTH-003', prodName: 'Heritage Tennis Sneaker White', dept: 'Footwear', subcat: 'Sneakers', onHand: 2, runRate: 4.00, str: 94.5, wos: 0.5, targetSS: 16, unitCost: 180, gmroi: 4.80, status: 'CRITICAL_STOCKOUT_RISK', directive: '⚠️ PULL INVENTORY: Stockout imminent. Transfer 110 units from Central DC.' },
  { storeCode: 'DXB-MOE-02', storeName: 'Mall of the Emirates Boutique', sku: 'LEA-TOT-GLD-002', prodName: 'Grain Calfskin Everyday Tote Noir', dept: 'Accessories', subcat: 'Tote Bags', onHand: 1, runRate: 0.80, str: 88.5, wos: 1.25, targetSS: 3, unitCost: 1850, gmroi: 3.90, status: 'CRITICAL_STOCKOUT_RISK', directive: '⚠️ PULL INVENTORY: Urgent transfer 2 units from Yas Mall / Regional DC.' },
  { storeCode: 'ECOM-UAE-01', storeName: 'UAE Central DC & Digital Hub', sku: 'BTY-EXT-OUD-005', prodName: 'Desert Amber Extrait de Parfum 100ml', dept: 'Beauty', subcat: 'Niche Perfumery', onHand: 2, runRate: 1.20, str: 82.0, wos: 1.7, targetSS: 5, unitCost: 320, gmroi: 5.20, status: 'CRITICAL_STOCKOUT_RISK', directive: '🚨 RESTOCK PRIORITY: Fast-moving fragrance, request supplier direct shipment.' },
  { storeCode: 'ECOM-UAE-01', storeName: 'UAE Central DC & Digital Hub', sku: 'DRS-SLK-EVN-004', prodName: 'Bias-Cut Silk Evening Gown Emerald', dept: 'Apparel', subcat: 'Dresses', onHand: 1, runRate: 0.45, str: 74.0, wos: 2.2, targetSS: 2, unitCost: 620, gmroi: 3.65, status: 'CRITICAL_STOCKOUT_RISK', directive: '⚠️ PULL INVENTORY: Request 2 units from Mall of the Emirates reserve.' },
  { storeCode: 'DXB-MOE-02', storeName: 'Mall of the Emirates Boutique', sku: 'RTW-BLZ-LIN-001', prodName: 'Unstructured Linen Blazer Sand', dept: 'Apparel', subcat: 'Tailored Jackets', onHand: 10, runRate: 2.45, str: 71.0, wos: 4.1, targetSS: 10, unitCost: 450, gmroi: 3.45, status: 'BALANCED', directive: '✅ OPTIMAL COVER: Fast turnover in boutique, maintain safety buffer.' },
  { storeCode: 'DXB-TDM-01', storeName: 'The Dubai Mall Flagship', sku: 'LEA-TOT-GLD-002', prodName: 'Grain Calfskin Everyday Tote Noir', dept: 'Accessories', subcat: 'Tote Bags', onHand: 4, runRate: 0.75, str: 66.0, wos: 5.3, targetSS: 3, unitCost: 1850, gmroi: 3.75, status: 'BALANCED', directive: '✅ OPTIMAL COVER: Velocity healthy. Maintain current replenishment pacing.' },
  { storeCode: 'DXB-TDM-01', storeName: 'The Dubai Mall Flagship', sku: 'RTW-BLZ-LIN-001', prodName: 'Unstructured Linen Blazer Sand', dept: 'Apparel', subcat: 'Tailored Jackets', onHand: 17, runRate: 2.95, str: 58.0, wos: 5.8, targetSS: 12, unitCost: 450, gmroi: 2.85, status: 'BALANCED', directive: '✅ OPTIMAL COVER: High volume flagship line, maintain steady intake.' },
  { storeCode: 'DXB-TDM-01', storeName: 'The Dubai Mall Flagship', sku: 'RTW-TEE-COT-006', prodName: 'Supima Heavyweight Cotton T-Shirt', dept: 'Apparel', subcat: 'T-Shirts', onHand: 46, runRate: 3.68, str: 31.0, wos: 12.5, targetSS: 15, unitCost: 45, gmroi: 3.10, status: 'OVERSTOCK_CASH_TRAP', directive: '🏷️ TIER-2 MARKDOWN (25%): Highly elastic (-2.50). Discount will unlock working capital fast.' },
  { storeCode: 'ECOM-UAE-01', storeName: 'UAE Central DC & Digital Hub', sku: 'FTW-SNK-LTH-003', prodName: 'Heritage Tennis Sneaker White', dept: 'Footwear', subcat: 'Sneakers', onHand: 112, runRate: 6.05, str: 14.5, wos: 18.5, targetSS: 24, unitCost: 180, gmroi: 1.95, status: 'OVERSTOCK_CASH_TRAP', directive: '📦 PUSH INVENTORY: DC surplus 88 units. Allocate 45 units to Dubai Mall Flagship.' },
  { storeCode: 'RUH-KGC-01', storeName: 'Kingdom Centre Flagship Riyadh', sku: 'BTY-EXT-OUD-005', prodName: 'Desert Amber Extrait de Parfum 100ml', dept: 'Beauty', subcat: 'Niche Perfumery', onHand: 14, runRate: 3.50, str: 72.0, wos: 4.0, targetSS: 14, unitCost: 320, gmroi: 5.60, status: 'BALANCED', directive: '✅ OPTIMAL COVER: High fragrance turnover in Riyadh flagship.' },
  { storeCode: 'AUH-GAL-02', storeName: 'The Galleria Al Maryah Island', sku: 'RTW-BLZ-LIN-001', prodName: 'Unstructured Linen Blazer Sand', dept: 'Apparel', subcat: 'Tailored Jackets', onHand: 5, runRate: 11.00, str: 89.8, wos: 0.5, targetSS: 44, unitCost: 450, gmroi: 3.90, status: 'CRITICAL_STOCKOUT_RISK', directive: '⚠️ PULL INVENTORY: Request 39 units from Yas Mall / Regional DC.' }
];
