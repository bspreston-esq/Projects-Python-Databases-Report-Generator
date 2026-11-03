# Report Generator

**Category:** Databases

## Problem

Create a utility that generates a report based on some tables in a database. Generates a sales reports based on the order/order details tables or sums up the days current database activity.

## Solution

Runs three aggregate queries (monthly revenue/orders, product ranking, category totals) against the orders/order_details/products schema, then writes a formatted text report and a machine-readable CSV. A sample database is created automatically for the demo.

## How to run

Requires Python 3.8+ and no third-party packages.

```bash
python3 main.py --db sales.db --output reports/
python3 main.py --demo
```

## Example

```text
Monthly revenue:
  2026-01: $    478.98  (2 orders)
  2026-02: $    207.99  (2 orders)
  2026-03: $    374.00  (1 order)
Top products:
  Monitor        display      2 units  $    498.00
```

## Attribution

The problem statement is from [karan/Projects](https://github.com/karan/Projects), a list of practical projects that anyone can solve in any programming language (MIT License, Copyright (c) 2013 Karan Goel). The Python solution in this repository was implemented by [bspreston-esq](https://github.com/bspreston-esq).

This repository is part of the [Projects-Python-All](https://github.com/bspreston-esq/Projects-Python-All) collection.
