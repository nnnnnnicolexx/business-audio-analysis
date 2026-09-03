#!/usr/bin/env python3
"""Print workbook structure and a bounded sample of populated cells."""

from __future__ import annotations

import argparse
from pathlib import Path

from openpyxl import load_workbook


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect spreadsheet evidence for business minutes.")
    parser.add_argument("xlsx", type=Path)
    parser.add_argument("--rows", type=int, default=20)
    parser.add_argument("--cols", type=int, default=30)
    args = parser.parse_args()

    workbook = load_workbook(args.xlsx.expanduser().resolve(), data_only=False, read_only=True)
    print("sheets:", workbook.sheetnames)
    for sheet in workbook.worksheets:
        print(f"\nSHEET {sheet.title} max {sheet.max_row} {sheet.max_column}")
        for row in sheet.iter_rows(
            min_row=1,
            max_row=min(sheet.max_row, args.rows),
            min_col=1,
            max_col=min(sheet.max_column, args.cols),
        ):
            values = [f"{cell.coordinate}={cell.value}" for cell in row if cell.value is not None]
            if values:
                print("; ".join(values))


if __name__ == "__main__":
    main()

