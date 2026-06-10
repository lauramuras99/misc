"""
Plot phyphox Sonar CSV exports.

Usage:
    python plot_phyphox_sonar.py "C:\\path\\to\\parent_folder"

Folder structure:
    parent_folder/
       mesasurement1/
            Echo location.csv
        mesasurement2/
            Echo location.csv
        ...
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def read_echo_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=None, engine="python")


def find_column(df: pd.DataFrame, words):
    for col in df.columns:
        low = col.lower()
        if all(w.lower() in low for w in words):
            return col
    return None


def get_distance_column(df: pd.DataFrame):
    col = find_column(df, ["distance"])
    if col is None:
        col = df.columns[0]
    return col


def get_crosscorrelation_columns(df: pd.DataFrame):
    cols = []
    for col in df.columns:
        low = col.lower()
        if "crosscorrelation" in low and "normalized" not in low:
            cols.append(col)
    if not cols:
        raise ValueError("No crosscorrelation columns found.")
    return cols


def plot_echo_file(echo_file: Path, output_folder: Path):
    df = read_echo_csv(echo_file)

    x_col = get_distance_column(df)
    y_cols = get_crosscorrelation_columns(df)

    output_folder.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 4.8))

    for i, col in enumerate(y_cols):
        label = "current" if i == 0 else f"history {i}"
        plt.plot(df[x_col], df[col], linewidth=1.1, label=label)

    plt.xlabel("Distance (cm)")
    plt.ylabel("Echo signal (crosscorrelation)")
    plt.title(echo_file.parent.name)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=8)
    plt.tight_layout()

    out = output_folder / f"{echo_file.parent.name}_echo_plot.png"
    plt.savefig(out, dpi=200)
    plt.close()

    return out


def main():
    if len(sys.argv) > 1:
        parent = Path(sys.argv[1])
    else:
        parent = Path(input("Parent folder: ").strip().strip('"'))

    if not parent.exists():
        raise FileNotFoundError(parent)

    output_folder = parent / "plots"
    echo_files = sorted(parent.glob("*/Echo location.csv"))

    if not echo_files:
        raise FileNotFoundError("No 'Echo location.csv' files found in subfolders.")

    print(f"Found {len(echo_files)} measurement folders.")

    for echo_file in echo_files:
        out = plot_echo_file(echo_file, output_folder)
        print(f"Saved: {out}")

    print("Done.")


if __name__ == "__main__":
    main()
