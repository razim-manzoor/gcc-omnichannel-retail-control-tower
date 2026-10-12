"""
Unit and integration tests for FastAPI Retail Control Tower Analytical Microservice.
Verifies all REST endpoints, contract schemas, and calculation parity against verified Kimball Star Schema.
"""
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "GCC Omnichannel Retail Control Tower API" in data["title"]
    assert data["docs_url"] == "/docs"

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["verified_pos_records"] == 115008

def test_kpis_aggregate():
    response = client.get("/api/kpis")
    assert response.status_code == 200
    data = response.json()
    assert data["units_sold"] == 142664
    assert round(data["gross_sales_aed"], 2) == 205230433.50
    assert round(data["net_revenue_aed"], 2) == 192726717.08
    assert round(data["gross_margin_pct"], 2) == 69.73
    assert round(data["markdown_depth_pct"], 2) == 6.09
    assert round(data["aur_aed"], 2) == 1350.91

def test_kpis_filtered_by_store():
    response = client.get("/api/kpis?store_code=DXB-TDM-01")
    assert response.status_code == 200
    data = response.json()
    assert data["units_sold"] > 0
    assert data["net_revenue_aed"] > 0
    assert data["gross_margin_pct"] > 60.0

def test_stockout_alerts():
    response = client.get("/api/inventory/stockouts?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    for alert in data:
        assert alert["weeks_of_supply"] < 2.5
        assert "PULL INVENTORY" in alert["rebalance_directive"]

def test_markdown_simulation():
    payload = {"discount_pct": 0.15}
    response = client.post("/api/simulation/markdown", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["discount_pct"] == 0.15
    assert data["simulated_volume_lift_pct"] > 0
    assert data["simulated_units"] > data["baseline_units"]
    assert "verdict" in data

def test_stores_list():
    response = client.get("/api/stores")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 8  # 8 GCC physical and digital locations
    store_codes = [s["store_code"] for s in data]
    assert "DXB-TDM-01" in store_codes
    assert "DXB-MOE-02" in store_codes
    assert "AUH-YAS-01" in store_codes
    assert "RUH-KGC-01" in store_codes
