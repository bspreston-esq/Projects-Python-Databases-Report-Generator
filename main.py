#!/usr/bin/env python3
"""Generate sales reports from a SQLite database as text and CSV."""
import argparse
import csv
import os
import sqlite3
import tempfile

SCHEMA = """
CREATE TABLE orders (id INTEGER PRIMARY KEY, order_date TEXT NOT NULL);
CREATE TABLE order_details (order_id INTEGER, product_id INTEGER, quantity INTEGER, unit_price REAL);
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT);
"""

def build_sample(path: str) -> None:
    connection = sqlite3.connect(path)
    connection.executescript(SCHEMA)
    connection.executemany("INSERT INTO products VALUES (?,?,?)",
                           [(1, "Keyboard", "input"), (2, "Monitor", "display"), (3, "Cable", "input"),
                            (4, "Webcam", "video")])
    connection.executemany("INSERT INTO orders VALUES (?,?)",
                           [(1, "2026-01-05"), (2, "2026-01-19"), (3, "2026-02-02"),
                            (4, "2026-02-21"), (5, "2026-03-04")])
    connection.executemany("INSERT INTO order_details VALUES (?,?,?,?)",
                           [(1, 1, 2, 89.99), (1, 3, 4, 12.50), (2, 2, 1, 249.00),
                            (3, 1, 1, 89.99), (4, 4, 2, 59.00), (5, 2, 1, 249.00), (5, 3, 10, 12.50)])
    connection.commit(); connection.close()

def query_monthly(connection):
    return connection.execute("""
        SELECT substr(o.order_date,1,7) AS month,
               ROUND(SUM(d.quantity*d.unit_price),2) AS revenue,
               COUNT(DISTINCT o.id) AS orders
        FROM orders o JOIN order_details d ON d.order_id=o.id
        GROUP BY month ORDER BY month""").fetchall()

def query_products(connection):
    return connection.execute("""
        SELECT p.name, p.category, SUM(d.quantity) AS units,
               ROUND(SUM(d.quantity*d.unit_price),2) AS revenue
        FROM order_details d JOIN products p ON p.id=d.product_id
        GROUP BY p.id ORDER BY revenue DESC""").fetchall()

def query_categories(connection):
    return connection.execute("""
        SELECT p.category, ROUND(SUM(d.quantity*d.unit_price),2) AS revenue
        FROM order_details d JOIN products p ON p.id=d.product_id
        GROUP BY p.category ORDER BY revenue DESC""").fetchall()

def generate(db_path: str, output_dir: str = "."):
    connection = sqlite3.connect(db_path)
    monthly, products, categories = query_monthly(connection), query_products(connection), query_categories(connection)
    connection.close()
    total = sum(row[1] for row in monthly)
    lines = ["Sales Report", "=" * 40, "", "Monthly revenue:"]
    lines += [f"  {month}: ${revenue:>10,.2f}  ({orders} order{'s' if orders != 1 else ''})" for month, revenue, orders in monthly]
    lines += ["", "Top products:"]
    lines += [f"  {name:<14} {category:<9} {units:>4} units  ${revenue:>10,.2f}" for name, category, units, revenue in products]
    lines += ["", "Revenue by category:"]
    lines += [f"  {category:<10} ${revenue:>10,.2f}" for category, revenue in categories]
    lines += ["", f"Grand total: ${total:,.2f}"]
    report_path = os.path.join(output_dir, "report.txt")
    csv_path = os.path.join(output_dir, "report.csv")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["section", "label", "value"])
        for month, revenue, orders in monthly:
            writer.writerow(["monthly", month, revenue])
        for name, category, units, revenue in products:
            writer.writerow(["product", name, revenue])
    return report_path, csv_path, "\n".join(lines)

def demo() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "sales.db")
        build_sample(db_path)
        report_path, csv_path, text = generate(db_path, tmp)
        print(text)
        print("\nfiles:", os.path.basename(report_path), os.path.getsize(report_path), "bytes,",
              os.path.basename(csv_path), os.path.getsize(csv_path), "bytes")

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db")
    parser.add_argument("--output", default=".")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.demo or not args.db:
        demo(); return
    try:
        report_path, csv_path, text = generate(args.db, args.output)
    except (OSError, sqlite3.Error) as exc:
        raise SystemExit(f"Error: {exc}")
    print(text)
    print("report:", report_path, "| csv:", csv_path)

if __name__ == "__main__":
    main()
