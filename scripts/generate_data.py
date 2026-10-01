"""
GCC Omnichannel Retail & Markdown Elasticity Control Tower
High-Performance Synthetic Data Generation Engine
Generates 100,000+ realistic retail POS transactions & inventory snapshots
Conforming strictly to Kimball Star Schema DDL specification
Output: 5 relational CSVs + 1 Disconnected Parameter CSV in data/
"""

import sys
import os
import math
import random
from datetime import date, datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
from faker import Faker

# Set seeds for reproducible statistical realism
np.random.seed(42)
random.seed(42)
fake = Faker("en_US")
Faker.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("GCC OMNICHANNEL RETAIL CONTROL TOWER - DATA GENERATION ENGINE")
print("Target: Kimball Star Schema (100,000+ Transactions & Periodic Snapshots)")
print("Output Directory:", DATA_DIR)
print("=" * 80)

# ==============================================================================
# 1. DIM_DATE GENERATOR (2025-01-01 to 2026-12-31 + Unknown Row)
# ==============================================================================
print("\n[1/6] Generating Dim_Date (731 rows)...")

start_date = date(2025, 1, 1)
end_date = date(2026, 12, 31)
date_range = pd.date_range(start_date, end_date, freq="D")

date_records = []

# Include -1 Unknown Member
date_records.append({
    "DateKey": -1,
    "FullDate": "1900-01-01",
    "FiscalYear": 1900,
    "FiscalQuarter": "Unknown",
    "FiscalMonthNum": -1,
    "FiscalMonthName": "Unknown",
    "RetailWeekNum": -1,
    "DayOfWeekName": "Unknown",
    "DayOfWeekNum": -1,
    "IsWeekendGCC": False,
    "IsRetailPeakSeason": False
})

for d in date_range:
    dt = d.date()
    date_key = dt.year * 10000 + dt.month * 100 + dt.day
    fiscal_year = dt.year
    fiscal_q = f"Q{(dt.month - 1) // 3 + 1}"
    month_num = dt.month
    month_name = dt.strftime("%B")
    
    # NRF 4-5-4 retail calendar week approximation
    week_num = int(dt.strftime("%U")) + 1
    if week_num > 52:
        week_num = 52
        
    day_name = dt.strftime("%A")
    day_num = dt.isoweekday() # 1=Mon .. 7=Sun
    
    # GCC commercial retail weekend: Friday, Saturday, Sunday
    is_weekend_gcc = day_name in ["Friday", "Saturday", "Sunday"]
    
    # GCC Retail Peak Seasons:
    # DSF (Dubai Shopping Festival): Dec 15 to Jan 31
    # Ramadan & Eid al-Fitr:
    #   2025: Feb 28 to Apr 3
    #   2026: Feb 17 to Mar 24
    # Eid al-Adha:
    #   2025: Jun 5 to Jun 10
    #   2026: May 26 to May 31
    # White Friday / Cyber Week: Nov 20 to Nov 30
    # National Days (UAE: Dec 1-3, Saudi: Sep 22-24)
    is_peak = False
    m, day = dt.month, dt.day
    y = dt.year
    
    if (m == 12 and day >= 15) or (m == 1):
        is_peak = True
    elif (m == 11 and day >= 20):
        is_peak = True
    elif y == 2025 and ((m == 2 and day >= 28) or (m == 3) or (m == 4 and day <= 4)):
        is_peak = True
    elif y == 2026 and ((m == 2 and day >= 17) or (m == 3 and day <= 25)):
        is_peak = True
    elif y == 2025 and (m == 6 and 5 <= day <= 10):
        is_peak = True
    elif y == 2026 and (m == 5 and 26 <= day <= 31):
        is_peak = True
    elif (m == 9 and 22 <= day <= 24) or (m == 12 and 1 <= day <= 3):
        is_peak = True
        
    date_records.append({
        "DateKey": date_key,
        "FullDate": dt.strftime("%Y-%m-%d"),
        "FiscalYear": fiscal_year,
        "FiscalQuarter": fiscal_q,
        "FiscalMonthNum": month_num,
        "FiscalMonthName": month_name,
        "RetailWeekNum": week_num,
        "DayOfWeekName": day_name,
        "DayOfWeekNum": day_num,
        "IsWeekendGCC": is_weekend_gcc,
        "IsRetailPeakSeason": is_peak
    })

df_date = pd.DataFrame(date_records)
df_date.to_csv(DATA_DIR / "Dim_Date.csv", index=False)
print(f"  -> Dim_Date.csv written: {len(df_date)} rows")


# ==============================================================================
# 2. DIM_STORE GENERATOR
# ==============================================================================
print("\n[2/6] Generating Dim_Store (9 stores)...")

stores_data = [
    {
        "StoreKey": -1,
        "StoreCode": "UNKNOWN",
        "StoreName": "Unknown / Unassigned",
        "Channel": "Unknown",
        "Emirate": "Unknown",
        "Country": "Unknown",
        "GrossLeasableAreaSqFt": 0,
        "ClusterTier": "Unknown",
        "HubFulfillmentEligible": False
    },
    {
        "StoreKey": 1,
        "StoreCode": "DXB-TDM-01",
        "StoreName": "The Dubai Mall Flagship",
        "Channel": "Physical Flagship",
        "Emirate": "Dubai",
        "Country": "United Arab Emirates",
        "GrossLeasableAreaSqFt": 14500,
        "ClusterTier": "Flagship",
        "HubFulfillmentEligible": True
    },
    {
        "StoreKey": 2,
        "StoreCode": "DXB-MOE-02",
        "StoreName": "Mall of the Emirates Boutique",
        "Channel": "Physical Boutique",
        "Emirate": "Dubai",
        "Country": "United Arab Emirates",
        "GrossLeasableAreaSqFt": 7200,
        "ClusterTier": "Boutique",
        "HubFulfillmentEligible": True
    },
    {
        "StoreKey": 3,
        "StoreCode": "AUH-YAS-01",
        "StoreName": "Yas Mall Abu Dhabi",
        "Channel": "Physical Boutique",
        "Emirate": "Abu Dhabi",
        "Country": "United Arab Emirates",
        "GrossLeasableAreaSqFt": 6800,
        "ClusterTier": "Boutique",
        "HubFulfillmentEligible": True
    },
    {
        "StoreKey": 4,
        "StoreCode": "DXB-OUT-01",
        "StoreName": "Dubai Outlet Mall Clearance",
        "Channel": "Physical Outlet",
        "Emirate": "Dubai",
        "Country": "United Arab Emirates",
        "GrossLeasableAreaSqFt": 4500,
        "ClusterTier": "Outlet",
        "HubFulfillmentEligible": False
    },
    {
        "StoreKey": 5,
        "StoreCode": "ECOM-UAE-01",
        "StoreName": "UAE Central DC & Digital Hub",
        "Channel": "Digital E-Commerce",
        "Emirate": "Dubai",
        "Country": "United Arab Emirates",
        "GrossLeasableAreaSqFt": 55000,
        "ClusterTier": "Fulfillment Hub",
        "HubFulfillmentEligible": True
    },
    {
        "StoreKey": 6,
        "StoreCode": "AUH-GAL-02",
        "StoreName": "The Galleria Al Maryah Island",
        "Channel": "Physical Flagship",
        "Emirate": "Abu Dhabi",
        "Country": "United Arab Emirates",
        "GrossLeasableAreaSqFt": 9500,
        "ClusterTier": "Flagship",
        "HubFulfillmentEligible": True
    },
    {
        "StoreKey": 7,
        "StoreCode": "JED-RSM-01",
        "StoreName": "Red Sea Mall Flagship Jeddah",
        "Channel": "Physical Flagship",
        "Emirate": "Makkah Region",
        "Country": "Saudi Arabia",
        "GrossLeasableAreaSqFt": 11000,
        "ClusterTier": "Flagship",
        "HubFulfillmentEligible": True
    },
    {
        "StoreKey": 8,
        "StoreCode": "RUH-KGC-01",
        "StoreName": "Kingdom Centre Flagship Riyadh",
        "Channel": "Physical Flagship",
        "Emirate": "Riyadh Province",
        "Country": "Saudi Arabia",
        "GrossLeasableAreaSqFt": 12000,
        "ClusterTier": "Flagship",
        "HubFulfillmentEligible": True
    }
]

df_store = pd.DataFrame(stores_data)
df_store.to_csv(DATA_DIR / "Dim_Store.csv", index=False)
print(f"  -> Dim_Store.csv written: {len(df_store)} rows")


# ==============================================================================
# 3. DIM_PRODUCT GENERATOR (Preserves 101-106 + 100+ Luxury/Premium SKUs)
# ==============================================================================
print("\n[3/6] Generating Dim_Product (120 SKUs)...")

products_data = [
    {
        "ProductKey": -1,
        "SKU": "UNKNOWN",
        "ProductName": "Unknown / Unassigned",
        "Department": "Unknown",
        "Category": "Unknown",
        "SubCategory": "Unknown",
        "Brand": "Unknown",
        "BrandTier": "Unknown",
        "BaseUnitCostAED": 0.0,
        "BaseRetailPriceAED": 0.0,
        "ElasticityCoefficient": -1.0
    },
    # Preserved Core Benchmark SKUs (Matching Unit Tests)
    {
        "ProductKey": 101,
        "SKU": "RTW-BLZ-LIN-001",
        "ProductName": "Unstructured Linen Blazer Sand",
        "Department": "Apparel",
        "Category": "Menswear",
        "SubCategory": "Tailored Jackets",
        "Brand": "Private Label Atelier",
        "BrandTier": "Bridge Luxury",
        "BaseUnitCostAED": 450.0,
        "BaseRetailPriceAED": 1450.0,
        "ElasticityCoefficient": -1.80
    },
    {
        "ProductKey": 102,
        "SKU": "LEA-TOT-GLD-002",
        "ProductName": "Grain Calfskin Everyday Tote Noir",
        "Department": "Accessories",
        "Category": "Leather Goods",
        "SubCategory": "Tote Bags",
        "Brand": "Maison Rivoli",
        "BrandTier": "Ultra-Luxury",
        "BaseUnitCostAED": 1850.0,
        "BaseRetailPriceAED": 5200.0,
        "ElasticityCoefficient": -0.65
    },
    {
        "ProductKey": 103,
        "SKU": "FTW-SNK-LTH-003",
        "ProductName": "Heritage Tennis Sneaker White",
        "Department": "Footwear",
        "Category": "Menswear",
        "SubCategory": "Sneakers",
        "Brand": "AeroSport Milano",
        "BrandTier": "Mass Premium",
        "BaseUnitCostAED": 180.0,
        "BaseRetailPriceAED": 650.0,
        "ElasticityCoefficient": -2.20
    },
    {
        "ProductKey": 104,
        "SKU": "DRS-SLK-EVN-004",
        "ProductName": "Bias-Cut Silk Evening Gown Emerald",
        "Department": "Apparel",
        "Category": "Womenswear",
        "SubCategory": "Dresses",
        "Brand": "Private Label Atelier",
        "BrandTier": "Bridge Luxury",
        "BaseUnitCostAED": 620.0,
        "BaseRetailPriceAED": 2100.0,
        "ElasticityCoefficient": -1.40
    },
    {
        "ProductKey": 105,
        "SKU": "BTY-EXT-OUD-005",
        "ProductName": "Desert Amber Extrait de Parfum 100ml",
        "Department": "Beauty",
        "Category": "Fragrance",
        "SubCategory": "Niche Perfumery",
        "Brand": "Sultanate Parfums",
        "BrandTier": "Ultra-Luxury",
        "BaseUnitCostAED": 320.0,
        "BaseRetailPriceAED": 1150.0,
        "ElasticityCoefficient": -0.45
    },
    {
        "ProductKey": 106,
        "SKU": "RTW-TEE-COT-006",
        "ProductName": "Supima Heavyweight Cotton T-Shirt",
        "Department": "Apparel",
        "Category": "Menswear",
        "SubCategory": "T-Shirts",
        "Brand": "Basics Lab",
        "BrandTier": "Mass Premium",
        "BaseUnitCostAED": 45.0,
        "BaseRetailPriceAED": 195.0,
        "ElasticityCoefficient": -2.50
    }
]

# Catalog generation taxonomy
departments_taxonomy = {
    "Apparel": [
        ("Menswear", "Tailored Jackets", "Atelier Sartorial", "Bridge Luxury", 400, 1500, -1.75),
        ("Menswear", "Cashmere Sweaters", "Maison Al-Sharq", "Ultra-Luxury", 650, 2400, -0.85),
        ("Menswear", "Chino Trousers", "Basics Lab", "Mass Premium", 80, 295, -2.10),
        ("Menswear", "Casual Linen Shirts", "Riviera Heritage", "Bridge Luxury", 120, 450, -1.65),
        ("Womenswear", "Cocktail Dresses", "Atelier Sartorial", "Bridge Luxury", 550, 1950, -1.35),
        ("Womenswear", "Silk Blouses", "Maison Rivoli", "Ultra-Luxury", 420, 1600, -0.90),
        ("Womenswear", "Pleated Midi Skirts", "Riviera Heritage", "Bridge Luxury", 210, 750, -1.50),
        ("Womenswear", "High-Rise Tailored Pants", "Atelier Sartorial", "Bridge Luxury", 260, 890, -1.45),
        ("Womenswear", "Trench Coats", "Maison Al-Sharq", "Ultra-Luxury", 980, 3600, -0.70)
    ],
    "Leather Goods": [
        ("Fine Leather", "Crossbody Pouches", "Maison Rivoli", "Ultra-Luxury", 950, 3200, -0.60),
        ("Fine Leather", "Bespoke Briefcases", "Oryx Studio", "Ultra-Luxury", 1400, 4800, -0.55),
        ("Leather Accessories", "Bifold Wallets", "Maison Rivoli", "Ultra-Luxury", 280, 950, -0.80),
        ("Leather Accessories", "Signature Belts", "Oryx Studio", "Bridge Luxury", 190, 680, -1.25),
        ("Fine Leather", "Travel Duffle Bags", "Riviera Heritage", "Bridge Luxury", 580, 1950, -1.15)
    ],
    "Footwear": [
        ("Mens Footwear", "Italian Penny Loafers", "Atelier Sartorial", "Bridge Luxury", 380, 1350, -1.30),
        ("Mens Footwear", "Minimalist Court Trainers", "AeroSport Milano", "Mass Premium", 160, 580, -2.15),
        ("Womens Footwear", "Slingback Pumps", "Maison Rivoli", "Ultra-Luxury", 620, 2200, -0.75),
        ("Womens Footwear", "Strappy Metallic Sandals", "Atelier Sartorial", "Bridge Luxury", 320, 1100, -1.40),
        ("Womens Footwear", "Suede Ankle Boots", "Riviera Heritage", "Bridge Luxury", 450, 1550, -1.20)
    ],
    "Accessories": [
        ("Eyewear", "Titanium Sunglasses", "Optique Privée", "Bridge Luxury", 240, 850, -1.10),
        ("Silk & Scarves", "Printed Silk Carré", "Maison Al-Sharq", "Ultra-Luxury", 290, 1100, -0.65),
        ("Timepieces & Jewelry", "Minimalist Chronograph", "Atelier Horlogerie", "Bridge Luxury", 850, 2900, -0.80),
        ("Silk & Scarves", "Cashmere Stoles", "Maison Al-Sharq", "Ultra-Luxury", 420, 1500, -0.75)
    ],
    "Beauty & Fragrance": [
        ("Haute Parfumerie", "Royal Oud Absolu 100ml", "Sultanate Parfums", "Ultra-Luxury", 380, 1450, -0.40),
        ("Haute Parfumerie", "Taif Rose & Musk 50ml", "Sultanate Parfums", "Ultra-Luxury", 240, 920, -0.50),
        ("Skincare Prestige", "Caviar Renewal Serum", "Laboratoire Suisse", "Ultra-Luxury", 410, 1600, -0.55),
        ("Home Ambiance", "Prestige Bakhoor & Diffuser", "Sultanate Parfums", "Bridge Luxury", 140, 480, -1.20)
    ]
}

colors = ["Noir", "Sand", "Blanc", "Emerald", "Navy", "Burgundy", "Camel", "Slate", "Cognac", "Olive"]
materials = ["Linen", "Silk", "Cashmere", "Calfskin", "Wool", "Suede", "Cotton", "Saffiano"]

current_key = 107
for dept, items in departments_taxonomy.items():
    for cat, subcat, brand, tier, min_cost, min_retail, base_elast in items:
        for i in range(4): # 4 SKU variants per subcategory
            color = colors[(current_key + i) % len(colors)]
            mat = materials[(current_key + i * 2) % len(materials)]
            sku = f"{dept[:3].upper()}-{subcat[:3].upper()}-{mat[:3].upper()}-{current_key:03d}"
            name = f"{brand} {mat} {subcat[:-1] if subcat.endswith('s') else subcat} {color}"
            
            cost = round(min_cost * (1.0 + (i * 0.15) - 0.1), 2)
            retail = round(min_retail * (1.0 + (i * 0.15) - 0.1), 2)
            # Add small jitter to elasticity
            elast = round(base_elast + (np.random.uniform(-0.15, 0.15)), 2)
            
            products_data.append({
                "ProductKey": current_key,
                "SKU": sku,
                "ProductName": name,
                "Department": dept,
                "Category": cat,
                "SubCategory": subcat,
                "Brand": brand,
                "BrandTier": tier,
                "BaseUnitCostAED": cost,
                "BaseRetailPriceAED": retail,
                "ElasticityCoefficient": elast
            })
            current_key += 1

df_product = pd.DataFrame(products_data)
df_product.to_csv(DATA_DIR / "Dim_Product.csv", index=False)
print(f"  -> Dim_Product.csv written: {len(df_product)} rows")


# ==============================================================================
# 4. FACT_POS_TRANSACTIONS GENERATOR (100,000+ realistic transactions)
# ==============================================================================
TARGET_TXN_ROWS = 115000
print(f"\n[4/6] Generating Fact_POS_Transactions ({TARGET_TXN_ROWS:,} rows)...")

valid_dates = df_date[df_date["DateKey"] > 0]
valid_stores = df_store[df_store["StoreKey"] > 0]
valid_prods = df_product[df_product["ProductKey"] > 0]

# Store traffic weights (Dubai Mall & E-Commerce carry highest omnichannel volume)
store_weights = {
    1: 0.28,  # Dubai Mall Flagship
    2: 0.14,  # MOE Boutique
    3: 0.11,  # Yas Mall Abu Dhabi
    4: 0.05,  # Dubai Outlet Mall
    5: 0.22,  # UAE Central DC / E-Commerce
    6: 0.08,  # Galleria Al Maryah
    7: 0.06,  # Red Sea Mall Jeddah
    8: 0.06   # Kingdom Centre Riyadh
}

# Payment types distribution
payment_types = ["CreditCard", "ApplePay", "Tabby_BNPL", "Tamara_BNPL", "Cash"]
payment_weights = [0.42, 0.30, 0.14, 0.09, 0.05]

# Seasonal traffic multipliers
# Calculate date selection probability based on GCC Weekend & Peak Seasons
date_weights = np.ones(len(valid_dates), dtype=np.float64)
for idx, (_, row) in enumerate(valid_dates.iterrows()):
    weight = 1.0
    if row["IsWeekendGCC"]:
        weight *= 1.45
    if row["IsRetailPeakSeason"]:
        weight *= 1.85
    date_weights[idx] = weight
date_weights /= date_weights.sum()

# Sample dates, stores, products
sampled_date_indices = np.random.choice(len(valid_dates), size=TARGET_TXN_ROWS, p=date_weights)
sampled_date_keys = valid_dates.iloc[sampled_date_indices]["DateKey"].values

sampled_stores = np.random.choice(
    list(store_weights.keys()),
    size=TARGET_TXN_ROWS,
    p=list(store_weights.values())
)

# Product popularity: Mass Premium & Bridge Luxury have higher transaction velocity than Ultra-Luxury
prod_weights = []
for _, row in valid_prods.iterrows():
    if row["BrandTier"] == "Mass Premium":
        prod_weights.append(3.5)
    elif row["BrandTier"] == "Bridge Luxury":
        prod_weights.append(2.0)
    else: # Ultra-Luxury
        prod_weights.append(0.7)
prod_weights = np.array(prod_weights)
prod_weights /= prod_weights.sum()

sampled_prod_indices = np.random.choice(len(valid_prods), size=TARGET_TXN_ROWS, p=prod_weights)
sampled_prod_records = valid_prods.iloc[sampled_prod_indices]

sampled_payments = np.random.choice(payment_types, size=TARGET_TXN_ROWS, p=payment_weights)

# Basket generation: group transactions into realistic baskets (~1.4 items per basket)
num_baskets = int(TARGET_TXN_ROWS / 1.35)
basket_ids = [f"BSK-{1000000 + i}" for i in range(num_baskets)]
assigned_baskets = np.random.choice(basket_ids, size=TARGET_TXN_ROWS)

# Units sold: 1 unit (82%), 2 units (13%), 3 units (4%), 4 units (1%)
units_sold = np.random.choice([1, 2, 3, 4], size=TARGET_TXN_ROWS, p=[0.82, 0.13, 0.04, 0.01])

# Vectorized Financial calculations
base_retail = sampled_prod_records["BaseRetailPriceAED"].values
base_cost = sampled_prod_records["BaseUnitCostAED"].values
elasticity = sampled_prod_records["ElasticityCoefficient"].values
prod_keys = sampled_prod_records["ProductKey"].values

gross_sales = np.round(units_sold * base_retail, 2)

# Discount rates:
# Full price (no discount): 68%
# VIP / Loyalty (5-10%): 18%
# Promotional Markdown (15-30%): 11%
# Clearance (40-50%): 3% (higher in Outlet Mall)
discount_rates = np.zeros(TARGET_TXN_ROWS, dtype=np.float64)
rand_disc = np.random.rand(TARGET_TXN_ROWS)

for i in range(TARGET_TXN_ROWS):
    store_k = sampled_stores[i]
    r = rand_disc[i]
    if store_k == 4: # Dubai Outlet Mall has higher clearance
        if r < 0.20:
            discount_rates[i] = 0.20
        elif r < 0.60:
            discount_rates[i] = 0.30
        elif r < 0.85:
            discount_rates[i] = 0.40
        else:
            discount_rates[i] = 0.50
    else:
        if r < 0.68:
            discount_rates[i] = 0.00
        elif r < 0.86:
            discount_rates[i] = np.random.choice([0.05, 0.10])
        elif r < 0.97:
            discount_rates[i] = np.random.choice([0.15, 0.20, 0.25])
        else:
            discount_rates[i] = np.random.choice([0.30, 0.40])

discount_amt = np.round(gross_sales * discount_rates, 2)
net_sales = np.round(gross_sales - discount_amt, 2)
extended_cost = np.round(units_sold * base_cost, 2)
tax_amt = np.round(net_sales * 0.05, 2) # 5% UAE/GCC standard VAT

# Prepend the 8 verified seed transactions from sql/03_seed_mock_data.sql for test continuity
seed_txns = [
    {"TransactionLineKey": 1001, "DateKey": 20260313, "StoreKey": 1, "ProductKey": 101, "BasketID": "BSK-DXB-0001", "PaymentType": "ApplePay", "UnitsSold": 1, "GrossSalesAmt": 1450.0, "DiscountAmt": 0.0, "NetSalesAmt": 1450.0, "ExtendedCostAmt": 450.0, "TaxAmtAED": 72.5},
    {"TransactionLineKey": 1002, "DateKey": 20260313, "StoreKey": 1, "ProductKey": 103, "BasketID": "BSK-DXB-0001", "PaymentType": "ApplePay", "UnitsSold": 1, "GrossSalesAmt": 650.0, "DiscountAmt": 0.0, "NetSalesAmt": 650.0, "ExtendedCostAmt": 180.0, "TaxAmtAED": 32.5},
    {"TransactionLineKey": 1003, "DateKey": 20260313, "StoreKey": 2, "ProductKey": 102, "BasketID": "BSK-MOE-0002", "PaymentType": "CreditCard", "UnitsSold": 1, "GrossSalesAmt": 5200.0, "DiscountAmt": 0.0, "NetSalesAmt": 5200.0, "ExtendedCostAmt": 1850.0, "TaxAmtAED": 260.0},
    {"TransactionLineKey": 1004, "DateKey": 20260314, "StoreKey": 5, "ProductKey": 104, "BasketID": "BSK-ECM-0003", "PaymentType": "Tabby_BNPL", "UnitsSold": 1, "GrossSalesAmt": 2100.0, "DiscountAmt": 210.0, "NetSalesAmt": 1890.0, "ExtendedCostAmt": 620.0, "TaxAmtAED": 94.5},
    {"TransactionLineKey": 1005, "DateKey": 20260314, "StoreKey": 5, "ProductKey": 105, "BasketID": "BSK-ECM-0003", "PaymentType": "Tabby_BNPL", "UnitsSold": 2, "GrossSalesAmt": 2300.0, "DiscountAmt": 0.0, "NetSalesAmt": 2300.0, "ExtendedCostAmt": 640.0, "TaxAmtAED": 115.0},
    {"TransactionLineKey": 1006, "DateKey": 20260315, "StoreKey": 3, "ProductKey": 101, "BasketID": "BSK-YAS-0004", "PaymentType": "ApplePay", "UnitsSold": 2, "GrossSalesAmt": 2900.0, "DiscountAmt": 435.0, "NetSalesAmt": 2465.0, "ExtendedCostAmt": 900.0, "TaxAmtAED": 123.25},
    {"TransactionLineKey": 1007, "DateKey": 20260315, "StoreKey": 1, "ProductKey": 106, "BasketID": "BSK-DXB-0005", "PaymentType": "Cash", "UnitsSold": 4, "GrossSalesAmt": 780.0, "DiscountAmt": 78.0, "NetSalesAmt": 702.0, "ExtendedCostAmt": 180.0, "TaxAmtAED": 35.10},
    {"TransactionLineKey": 1008, "DateKey": 20260315, "StoreKey": 5, "ProductKey": 103, "BasketID": "BSK-ECM-0006", "PaymentType": "CreditCard", "UnitsSold": 3, "GrossSalesAmt": 1950.0, "DiscountAmt": 195.0, "NetSalesAmt": 1755.0, "ExtendedCostAmt": 540.0, "TaxAmtAED": 87.75}
]

df_seed_txns = pd.DataFrame(seed_txns)

df_generated_txns = pd.DataFrame({
    "TransactionLineKey": np.arange(10000, 10000 + TARGET_TXN_ROWS, dtype=np.int64),
    "DateKey": sampled_date_keys,
    "StoreKey": sampled_stores,
    "ProductKey": prod_keys,
    "BasketID": assigned_baskets,
    "PaymentType": sampled_payments,
    "UnitsSold": units_sold,
    "GrossSalesAmt": gross_sales,
    "DiscountAmt": discount_amt,
    "NetSalesAmt": net_sales,
    "ExtendedCostAmt": extended_cost,
    "TaxAmtAED": tax_amt
})

df_pos = pd.concat([df_seed_txns, df_generated_txns], ignore_index=True)
df_pos.to_csv(DATA_DIR / "Fact_POS_Transactions.csv", index=False)
print(f"  -> Fact_POS_Transactions.csv written: {len(df_pos):,} rows")


# ==============================================================================
# 5. FACT_DAILY_INVENTORY GENERATOR (Periodic Store Snapshots)
# ==============================================================================
print("\n[5/6] Generating Fact_Daily_Inventory (Periodic Closing Snapshots)...")

# We create daily snapshots across the focus operational window (e.g. 60 days ending 2026-03-31)
# Across all stores (1..8) and all SKUs (101..226)
snapshot_dates = pd.date_range("2026-02-01", "2026-03-31", freq="D")
inv_records = []

# Include seed inventory records from sql/03_seed_mock_data.sql for test consistency
seed_inv = [
    {"InventorySnapshotKey": 5001, "SnapshotDateKey": 20260314, "StoreKey": 1, "ProductKey": 101, "OnHandUnits": 18, "InTransitUnits": 5, "ReservedUnits": 2, "AvailableUnits": 16, "UnitCostSnapshotAmt": 450.0, "InventoryCostValueAmt": 8100.0},
    {"InventorySnapshotKey": 5002, "SnapshotDateKey": 20260314, "StoreKey": 1, "ProductKey": 102, "OnHandUnits": 4, "InTransitUnits": 0, "ReservedUnits": 1, "AvailableUnits": 3, "UnitCostSnapshotAmt": 1850.0, "InventoryCostValueAmt": 7400.0},
    {"InventorySnapshotKey": 5003, "SnapshotDateKey": 20260314, "StoreKey": 2, "ProductKey": 101, "OnHandUnits": 10, "InTransitUnits": 2, "ReservedUnits": 0, "AvailableUnits": 10, "UnitCostSnapshotAmt": 450.0, "InventoryCostValueAmt": 4500.0},
    {"InventorySnapshotKey": 5004, "SnapshotDateKey": 20260314, "StoreKey": 2, "ProductKey": 102, "OnHandUnits": 3, "InTransitUnits": 0, "ReservedUnits": 0, "AvailableUnits": 3, "UnitCostSnapshotAmt": 1850.0, "InventoryCostValueAmt": 5550.0},
    {"InventorySnapshotKey": 5005, "SnapshotDateKey": 20260314, "StoreKey": 5, "ProductKey": 101, "OnHandUnits": 85, "InTransitUnits": 20, "ReservedUnits": 15, "AvailableUnits": 70, "UnitCostSnapshotAmt": 450.0, "InventoryCostValueAmt": 38250.0},
    {"InventorySnapshotKey": 5006, "SnapshotDateKey": 20260314, "StoreKey": 5, "ProductKey": 102, "OnHandUnits": 25, "InTransitUnits": 5, "ReservedUnits": 4, "AvailableUnits": 21, "UnitCostSnapshotAmt": 1850.0, "InventoryCostValueAmt": 46250.0},
    {"InventorySnapshotKey": 5007, "SnapshotDateKey": 20260315, "StoreKey": 1, "ProductKey": 101, "OnHandUnits": 17, "InTransitUnits": 5, "ReservedUnits": 1, "AvailableUnits": 16, "UnitCostSnapshotAmt": 450.0, "InventoryCostValueAmt": 7650.0},
    {"InventorySnapshotKey": 5008, "SnapshotDateKey": 20260315, "StoreKey": 1, "ProductKey": 102, "OnHandUnits": 4, "InTransitUnits": 0, "ReservedUnits": 0, "AvailableUnits": 4, "UnitCostSnapshotAmt": 1850.0, "InventoryCostValueAmt": 7400.0},
    {"InventorySnapshotKey": 5009, "SnapshotDateKey": 20260315, "StoreKey": 1, "ProductKey": 106, "OnHandUnits": 46, "InTransitUnits": 10, "ReservedUnits": 2, "AvailableUnits": 44, "UnitCostSnapshotAmt": 45.0, "InventoryCostValueAmt": 2070.0},
    {"InventorySnapshotKey": 5010, "SnapshotDateKey": 20260315, "StoreKey": 2, "ProductKey": 101, "OnHandUnits": 10, "InTransitUnits": 2, "ReservedUnits": 0, "AvailableUnits": 10, "UnitCostSnapshotAmt": 450.0, "InventoryCostValueAmt": 4500.0},
    {"InventorySnapshotKey": 5011, "SnapshotDateKey": 20260315, "StoreKey": 3, "ProductKey": 101, "OnHandUnits": 8, "InTransitUnits": 4, "ReservedUnits": 1, "AvailableUnits": 7, "UnitCostSnapshotAmt": 450.0, "InventoryCostValueAmt": 3600.0},
    {"InventorySnapshotKey": 5012, "SnapshotDateKey": 20260315, "StoreKey": 5, "ProductKey": 101, "OnHandUnits": 85, "InTransitUnits": 20, "ReservedUnits": 12, "AvailableUnits": 73, "UnitCostSnapshotAmt": 450.0, "InventoryCostValueAmt": 38250.0},
    {"InventorySnapshotKey": 5013, "SnapshotDateKey": 20260315, "StoreKey": 5, "ProductKey": 103, "OnHandUnits": 112, "InTransitUnits": 30, "ReservedUnits": 8, "AvailableUnits": 104, "UnitCostSnapshotAmt": 180.0, "InventoryCostValueAmt": 20160.0}
]

# Track existing seed keys to avoid duplicates
existing_keys = set()
for r in seed_inv:
    existing_keys.add((r["SnapshotDateKey"], r["StoreKey"], r["ProductKey"]))

inv_snapshot_id = 60000
inv_rows = list(seed_inv)

# To model realistic omnichannel inventory dynamics:
# Store 1 (Dubai Mall) has high sell-through and low on-hand (stockout risk on hero items)
# Store 3 (Yas Mall) and Store 5 (DC) have surplus stock (rebalance source)
active_prods = valid_prods.to_dict("records")
active_stores = valid_stores.to_dict("records")

# Generate weekly/daily snapshots for the operational window
for s_date in snapshot_dates:
    s_dt = s_date.date()
    s_date_key = s_dt.year * 10000 + s_dt.month * 100 + s_dt.day
    
    # Take snapshots for every store and product
    for st in active_stores:
        s_key = st["StoreKey"]
        is_dc = (s_key == 5)
        is_flagship = (s_key in [1, 7, 8])
        
        for pr in active_prods:
            p_key = pr["ProductKey"]
            if (s_date_key, s_key, p_key) in existing_keys:
                continue
                
            cost = pr["BaseUnitCostAED"]
            
            # Base stock allocation
            if is_dc:
                on_hand = int(np.random.normal(75, 20))
                on_hand = max(20, on_hand)
                in_transit = int(np.random.choice([0, 10, 25, 50], p=[0.4, 0.3, 0.2, 0.1]))
                reserved = int(min(on_hand, np.random.poisson(8)))
            elif is_flagship:
                # Dubai Mall / Flagship sells fast -> tighter stock
                on_hand = int(np.random.normal(16, 6))
                on_hand = max(2, on_hand)
                in_transit = int(np.random.choice([0, 4, 8], p=[0.6, 0.3, 0.1]))
                reserved = int(min(on_hand, np.random.poisson(2)))
            else: # Boutiques & Outlets
                on_hand = int(np.random.normal(9, 4))
                on_hand = max(1, on_hand)
                in_transit = int(np.random.choice([0, 2, 4], p=[0.7, 0.2, 0.1]))
                reserved = int(min(on_hand, np.random.poisson(1)))
                
            avail = on_hand - reserved
            cost_val = round(on_hand * cost, 2)
            
            inv_rows.append({
                "InventorySnapshotKey": inv_snapshot_id,
                "SnapshotDateKey": s_date_key,
                "StoreKey": s_key,
                "ProductKey": p_key,
                "OnHandUnits": on_hand,
                "InTransitUnits": in_transit,
                "ReservedUnits": reserved,
                "AvailableUnits": avail,
                "UnitCostSnapshotAmt": cost,
                "InventoryCostValueAmt": cost_val
            })
            inv_snapshot_id += 1

df_inv = pd.DataFrame(inv_rows)
df_inv.to_csv(DATA_DIR / "Fact_Daily_Inventory.csv", index=False)
print(f"  -> Fact_Daily_Inventory.csv written: {len(df_inv):,} rows")


# ==============================================================================
# 6. MARKDOWN_SCENARIO (Disconnected Parameter Table)
# ==============================================================================
print("\n[6/6] Generating Markdown_Scenario (11 scenarios)...")

scenarios = [
    {"ScenarioDiscountPct": 0.00, "DiscountDisplayLabel": "0% (Full Price)", "SimulationSortOrder": 0},
    {"ScenarioDiscountPct": 0.05, "DiscountDisplayLabel": "5% Off", "SimulationSortOrder": 1},
    {"ScenarioDiscountPct": 0.10, "DiscountDisplayLabel": "10% Off", "SimulationSortOrder": 2},
    {"ScenarioDiscountPct": 0.15, "DiscountDisplayLabel": "15% Off", "SimulationSortOrder": 3},
    {"ScenarioDiscountPct": 0.20, "DiscountDisplayLabel": "20% Off", "SimulationSortOrder": 4},
    {"ScenarioDiscountPct": 0.25, "DiscountDisplayLabel": "25% Off", "SimulationSortOrder": 5},
    {"ScenarioDiscountPct": 0.30, "DiscountDisplayLabel": "30% Off", "SimulationSortOrder": 6},
    {"ScenarioDiscountPct": 0.35, "DiscountDisplayLabel": "35% Off", "SimulationSortOrder": 7},
    {"ScenarioDiscountPct": 0.40, "DiscountDisplayLabel": "40% Off", "SimulationSortOrder": 8},
    {"ScenarioDiscountPct": 0.45, "DiscountDisplayLabel": "45% Off", "SimulationSortOrder": 9},
    {"ScenarioDiscountPct": 0.50, "DiscountDisplayLabel": "50% Off", "SimulationSortOrder": 10},
]

df_scenario = pd.DataFrame(scenarios)
df_scenario.to_csv(DATA_DIR / "Markdown_Scenario.csv", index=False)
print(f"  -> Markdown_Scenario.csv written: {len(df_scenario)} rows")

print("\n" + "=" * 80)
print("SYNTHETIC DATA GENERATION COMPLETE: 6 Star Schema CSVs Generated in data/")
print("=" * 80)
