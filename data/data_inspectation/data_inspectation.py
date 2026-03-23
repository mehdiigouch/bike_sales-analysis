import pandas as pd
import numpy as np
from utils.logs import section, logger,data_root
from data.raw.data_extraction import   validate_file, load_raw_data


def data_inspectation():
    section("INSPECTING THE DATASET")
    # ════════════════════════════════════════════════════════════
    # 1. LOAD DATA
    # ════════════════════════════════════════════════════════════

    section("LOAD DATASET FROM DATA_ROOT FUNCTION")


    DATASET_ROOT = data_root()

    df = load_raw_data(validate_file(DATASET_ROOT))

    print(df.head(10))



    # ════════════════════════════════════════════════════════════
    # 2. SHAPE & MEMORY
    # ════════════════════════════════════════════════════════════


    section("2. SHAPE & MEMORY USAGE")
    print(f"  Rows       : {df.shape[0]:,}")
    print(f"  Columns    : {df.shape[1]}")
    total_cells = df.shape[0] * df.shape[1]
    print(f"  Total Cells: {total_cells:,}")
    mem_mb = df.memory_usage(deep=True).sum() / 1024 ** 2
    print(f"  Memory     : {mem_mb:.2f} MB")


    # ════════════════════════════════════════════════════════════
    # 3. FIRST & LAST ROWS
    # ════════════════════════════════════════════════════════════

    section("3. FIRST 5 ROWS (Head)")
    print(df.head().to_string())
    
    section("3. LAST 5 ROWS (Tail)")
    print(df.tail().to_string())

    # ════════════════════════════════════════════════════════════
    # 4. COLUMN DATA TYPES
    # ════════════════════════════════════════════════════════════
    section("4. COLUMN DATA TYPES")
    dtype_df = pd.DataFrame({
        "Column"       : df.columns,
        "Dtype"        : df.dtypes.values,
        "Suggested Type": [
            "datetime" if "date" in c.lower()
            else "category" if df[c].nunique() < 20 and df[c].dtype == object
            else str(df[c].dtype)
            for c in df.columns
        ]
    })
    print(dtype_df.to_string(index=False))
    
    
    # ════════════════════════════════════════════════════════════
    # 5. MISSING VALUES
    # ════════════════════════════════════════════════════════════
    section("5. MISSING VALUES ANALYSIS")
    missing_count = df.isnull().sum()
    missing_pct   = (missing_count / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        "Column"       : df.columns,
        "Missing Count": missing_count.values,
        "Missing %"    : missing_pct.values,
        "Status"       : ["✔ Complete" if v == 0 else "⚠ Has Nulls" for v in missing_count.values]
    })
    print(missing_df.to_string(index=False))
    total_missing = missing_count.sum()
    print(f"\n  → Total missing cells : {total_missing:,}")
    print(f"  → Overall completeness: {100 - (total_missing / total_cells * 100):.2f}%")



    # ════════════════════════════════════════════════════════════
    # 6. DUPLICATE ROWS
    # ════════════════════════════════════════════════════════════
    section("6. DUPLICATE ROWS")
    r_dupes = df.duplicated().sum()
    dupe_pct = round(r_dupes / len(df) * 100, 2)
    print(f"  Total Duplicates : {r_dupes:,}")
    print(f"  Duplicate %      : {dupe_pct}%")
    print(f"  Recommendation   : {'⚠ Drop duplicates before analysis' if r_dupes > 0 else '✔ No duplicates found'}")

    section("6. DUPLICATE COLUMNS")
    c_dupes = df.columns.duplicated().sum()
    dupe_pct = round(c_dupes / len(df.columns) * 100, 2)
    print(f"  Total Duplicates : {c_dupes:,}")
    print(f"  Duplicate %      : {dupe_pct}%")
    print(f"  Recommendation   : {'⚠ Drop duplicates before analysis' if c_dupes > 0 else '✔ No duplicates found'}")


    # ════════════════════════════════════════════════════════════
    # 7. UNIQUE VALUES PER COLUMN
    # ════════════════════════════════════════════════════════════
    section("7. UNIQUE VALUES PER COLUMN")
    unique_df = pd.DataFrame({
        "Column"        : df.columns,
        "Unique Values" : [df[c].nunique() for c in df.columns],
        "Sample Values" : [str(df[c].unique()[:3].tolist()) for c in df.columns]
    })
    print(unique_df.to_string(index=False))



    # ════════════════════════════════════════════════════════════
    # 8. STATISTICAL SUMMARY — NUMERIC COLUMNS
    # ════════════════════════════════════════════════════════════
    section("8. STATISTICAL SUMMARY — NUMERIC COLUMNS")
    num_df = df.select_dtypes(include="number")
    summary = num_df.describe().T
    summary["range"]    = summary["max"] - summary["min"]
    summary["cv%"]      = (summary["std"] / summary["mean"] * 100).round(2)  # Coefficient of variation
    print(summary.round(2).to_string())


    # ════════════════════════════════════════════════════════════
    # 9. STATISTICAL SUMMARY — CATEGORICAL COLUMNS
    # ════════════════════════════════════════════════════════════
    section("9. STATISTICAL SUMMARY — CATEGORICAL COLUMNS")
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        print(f"\n  ── {col} ──")
        vc = df[col].value_counts()
        top5 = vc.head(5)
        for val, cnt in top5.items():
            pct = round(cnt / len(df) * 100, 1)
            bar = "█" * int(pct / 2)
            print(f"    {str(val):<30} {cnt:>7,}  ({pct:>5.1f}%)  {bar}")
        if len(vc) > 5:
            print(f"    ... and {len(vc) - 5} more unique values")
    



