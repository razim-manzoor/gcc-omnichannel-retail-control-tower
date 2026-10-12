"""
Parquet Storage & Compression Benchmark Layer for GCC Omnichannel Retail Control Tower.
Converts production CSV files to Snappy-compressed Parquet and benchmarks storage efficiency and DuckDB query throughput.
"""
import os
import time
import json
import duckdb

def format_bytes(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def convert_and_benchmark():
    data_dir = "data"
    parquet_dir = os.path.join(data_dir, "parquet")
    os.makedirs(parquet_dir, exist_ok=True)

    csv_files = [
        "Fact_POS_Transactions.csv",
        "Fact_Daily_Inventory.csv",
        "Dim_Date.csv",
        "Dim_Store.csv",
        "Dim_Product.csv",
        "Markdown_Scenario.csv"
    ]

    con = duckdb.connect()

    print("=" * 80)
    print("PARQUET CONVERSION & STORAGE COMPRESSION BENCHMARK")
    print("=" * 80)

    storage_stats = []
    total_csv_bytes = 0
    total_parquet_bytes = 0

    for fname in csv_files:
        csv_path = os.path.join(data_dir, fname)
        table_name = os.path.splitext(fname)[0]
        parquet_path = os.path.join(parquet_dir, f"{table_name}.parquet")

        if not os.path.exists(csv_path):
            print(f"[WARN] File not found: {csv_path}")
            continue

        # Convert to Snappy-compressed Parquet
        con.execute(f"""
            COPY (SELECT * FROM read_csv_auto('{csv_path}'))
            TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION SNAPPY)
        """)

        csv_size = os.path.getsize(csv_path)
        parquet_size = os.path.getsize(parquet_path)
        reduction_pct = ((csv_size - parquet_size) / csv_size) * 100
        row_count = con.execute(f"SELECT COUNT(*) FROM '{parquet_path}'").fetchone()[0]

        total_csv_bytes += csv_size
        total_parquet_bytes += parquet_size

        storage_stats.append({
            "table": table_name,
            "row_count": row_count,
            "csv_bytes": csv_size,
            "parquet_bytes": parquet_size,
            "reduction_pct": reduction_pct
        })

        print(f"  Converted {fname:<28} | Rows: {row_count:>8,d} | {format_bytes(csv_size):>9} -> {format_bytes(parquet_size):>8} (-{reduction_pct:.1f}%)")

    overall_reduction = ((total_csv_bytes - total_parquet_bytes) / total_csv_bytes) * 100
    print("-" * 80)
    print(f"  TOTAL STORAGE: {format_bytes(total_csv_bytes)} (CSV) -> {format_bytes(total_parquet_bytes)} (Parquet) | Space Saved: {overall_reduction:.1f}%")
    print("=" * 80)

    # Analytical Query Throughput Benchmarks
    print("\nQUERY THROUGHPUT BENCHMARK (DuckDB Columnar Execution: CSV vs Parquet)")
    print("=" * 80)

    pos_csv = os.path.join(data_dir, "Fact_POS_Transactions.csv").replace("\\", "/")
    pos_pq = os.path.join(parquet_dir, "Fact_POS_Transactions.parquet").replace("\\", "/")

    benchmark_queries = [
        {
            "name": "Full Table Aggregation (3 Measures)",
            "description": "SUM(UnitsSold), SUM(NetSalesAmt), SUM(ExtendedCostAmt)",
            "sql_csv": f"SELECT SUM(UnitsSold), SUM(NetSalesAmt), SUM(ExtendedCostAmt) FROM '{pos_csv}'",
            "sql_pq": f"SELECT SUM(UnitsSold), SUM(NetSalesAmt), SUM(ExtendedCostAmt) FROM '{pos_pq}'"
        },
        {
            "name": "Column-Pruned Scan (Single Column)",
            "description": "SUM(NetSalesAmt) with column pruning",
            "sql_csv": f"SELECT SUM(NetSalesAmt) FROM '{pos_csv}'",
            "sql_pq": f"SELECT SUM(NetSalesAmt) FROM '{pos_pq}'"
        },
        {
            "name": "Filtered Commercial Slice",
            "description": "SUM(NetSalesAmt) WHERE StoreKey = 1 AND DateKey >= 20260101",
            "sql_csv": f"SELECT SUM(NetSalesAmt) FROM '{pos_csv}' WHERE StoreKey = 1 AND DateKey >= 20260101",
            "sql_pq": f"SELECT SUM(NetSalesAmt) FROM '{pos_pq}' WHERE StoreKey = 1 AND DateKey >= 20260101"
        }
    ]

    query_results = []
    iterations = 5

    for bq in benchmark_queries:
        # Benchmark CSV
        times_csv = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            con.execute(bq["sql_csv"]).fetchall()
            times_csv.append((time.perf_counter() - t0) * 1000)
        avg_csv = sum(times_csv) / len(times_csv)

        # Benchmark Parquet
        times_pq = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            con.execute(bq["sql_pq"]).fetchall()
            times_pq.append((time.perf_counter() - t0) * 1000)
        avg_pq = sum(times_pq) / len(times_pq)

        speedup = avg_csv / avg_pq if avg_pq > 0 else 1.0

        query_results.append({
            "name": bq["name"],
            "avg_csv_ms": avg_csv,
            "avg_pq_ms": avg_pq,
            "speedup": speedup
        })

        print(f"Query: {bq['name']}")
        print(f"       CSV Time:     {avg_csv:>6.2f} ms")
        print(f"       Parquet Time: {avg_pq:>6.2f} ms")
        print(f"       Speedup:      {speedup:>6.2f}x faster with Parquet")
        print("-" * 80)

    # Save benchmark summary
    summary_path = os.path.join(parquet_dir, "benchmark_summary.json")
    summary_data = {
        "storage": {
            "total_csv_bytes": total_csv_bytes,
            "total_parquet_bytes": total_parquet_bytes,
            "savings_pct": overall_reduction,
            "tables": storage_stats
        },
        "query_performance": query_results
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print(f"\n[PASS] Benchmark summary written to {summary_path}")
    print("=" * 80)

if __name__ == "__main__":
    convert_and_benchmark()
