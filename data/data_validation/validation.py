import pandas as pd
import numpy as np
import sys
from pathlib import Path
from dataclasses import dataclass, field  # create constructors automatically for classes
#Think of field() as a way to control how a variable inside a dataclass behaves.
from typing import List, Callable  #Callable means a function that can be passed as an argument.
#List is used to indicate that a variable should contain a list of a specific type.

from utils.logs import section, logger,data_root
from data.raw.data_extraction import   validate_file, load_raw_data
from data.data_inspectation.data_inspectation import data_inspectation



# ════════════════════════════════════════════════════════════
# IMPORTING DATA PATH FUNCTION FROM THE LOGS.PY FILE
# ════════════════════════════════════════════════════════════

section("IMPORTING THE DATASET FROM DATA_EXTRACTION.PY")

DATASET_ROOT = data_root()

DATASET = load_raw_data(validate_file(DATASET_ROOT))

print(DATASET.head(10))

data_inspectation()

# ════════════════════════════════════════════════════════════
# PERFORMING DATA VALIDATION PROCESS
# ════════════════════════════════════════════════════════════



SCHEMA = {
    # column_name : { "dtype": ..., "nullable": bool, "allowed": [...] or None }
    "Date"            : {"dtype": "str",   "nullable": False, "allowed": None},
    "Day"             : {"dtype": "int",   "nullable": False, "allowed": None},
    "Month"           : {"dtype": "str",   "nullable": False, "allowed": [
                            "January","February","March","April","May","June",
                            "July","August","September","October","November","December"
                        ]},
    "Year"            : {"dtype": "int",   "nullable": False, "allowed": list(range(2000, 2031))},
    "Customer_Age"    : {"dtype": "int",   "nullable": False, "allowed": None},
    "Age_Group"       : {"dtype": "str",   "nullable": False, "allowed": [
                            "Youth (<25)", "Young Adults (25-34)",
                            "Adults (35-64)", "Seniors (64+)"
                        ]},
    "Customer_Gender" : {"dtype": "str",   "nullable": False, "allowed": ["M", "F"]},
    "Country"         : {"dtype": "str",   "nullable": False, "allowed": [
                            "United States", "Australia", "Canada",
                            "United Kingdom", "Germany", "France"
                        ]},
    "State"           : {"dtype": "str",   "nullable": False, "allowed": None},
    "Product_Category": {"dtype": "str",   "nullable": False, "allowed": [
                            "Bikes", "Accessories", "Clothing"
                        ]},
    "Sub_Category"    : {"dtype": "str",   "nullable": False, "allowed": None},
    "Product"         : {"dtype": "str",   "nullable": False, "allowed": None},
    "Order_Quantity"  : {"dtype": "int",   "nullable": False, "allowed": None},
    "Unit_Cost"       : {"dtype": "int",   "nullable": False, "allowed": None},
    "Unit_Price"      : {"dtype": "int",   "nullable": False, "allowed": None},
    "Profit"          : {"dtype": "int",   "nullable": False, "allowed": None},
    "Cost"            : {"dtype": "int",   "nullable": False, "allowed": None},
    "Revenue"         : {"dtype": "int",   "nullable": False, "allowed": None},
}


 
NUMERIC_RANGES = {
    # column : (min_value, max_value)
    "Customer_Age"   : (10,  120),
    "Day"            : (1,   31),
    "Year"           : (2000, 2030),
    "Order_Quantity" : (1,   1000),
    "Unit_Cost"      : (1,   100_000),
    "Unit_Price"     : (1,   100_000),
    "Cost"           : (1,   10_000_000),
    "Revenue"        : (1,   10_000_000),
}



 
AGE_GROUP_RULES = {
    # Age_Group label : (min_age, max_age)  inclusive
    "Youth (<25)"         : (10,  24),
    "Young Adults (25-34)": (25,  34),
    "Adults (35-64)"      : (35,  64),
    "Seniors (64+)"       : (65, 120),
}
 
# ════════════════════════════════════════════════════════════
# VALIDATION RESULT DATACLASS
# ════════════════════════════════════════════════════════════
 


VALID_STATUSES = {"PASS", "WARN", "FAIL"}

@dataclass
class ValidationResult:
    rule        : str
    category    : str
    status      : str
    affected    : int = 0
    total       : int = 0
    details     : str = ""

    def __post_init__(self):
        # Guard 1 — status must be a known value
        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{self.status}'. Must be one of {VALID_STATUSES}"
            )
        # Guard 2 — affected cannot be negative
        if self.affected < 0:
            raise ValueError(
                f"'affected' cannot be negative, got {self.affected}"
            )
        # Guard 3 — affected cannot exceed total
        if self.total > 0 and self.affected > self.total:
            raise ValueError(
                f"'affected' ({self.affected}) cannot exceed 'total' ({self.total})"
            )

    @property
    def pct(self) -> float:
        return round(self.affected / self.total * 100, 2) if self.total else 0.0

    @property
    def icon(self) -> str:
        return {"PASS": "✔", "WARN": "⚠", "FAIL": "✖"}.get(self.status, "?")

# ════════════════════════════════════════════════════════════
# VALIDATION REPORT DATACLASS
# ════════════════════════════════════════════════════════════
 

@dataclass
class ValidationReport:
    results: List[ValidationResult] = field(default_factory=list)

    def add(self, result: ValidationResult) -> None:
        # Fix 2 — enforce correct type at insertion
        if not isinstance(result, ValidationResult):
            raise TypeError(
                f"Expected ValidationResult, got {type(result).__name__}"
            )
        self.results.append(result)

    @property
    def passed(self)   -> List[ValidationResult]: return [r for r in self.results if r.status == "PASS"]
    @property
    def warnings(self) -> List[ValidationResult]: return [r for r in self.results if r.status == "WARN"]
    @property
    def failures(self) -> List[ValidationResult]: return [r for r in self.results if r.status == "FAIL"]

    def print_summary(self) -> None:
        section("VALIDATION SUMMARY")
        total = len(self.results)

        # Fix 1 — guard against empty report
        if total == 0:
            print("  ⚠ No validation rules were run.")
            return

        n_pass = len(self.passed)
        n_warn = len(self.warnings)
        n_fail = len(self.failures)

        print(f"\n  Total Rules Checked : {total}")
        print(f"  ✔  Passed           : {n_pass}")
        print(f"  ⚠  Warnings         : {n_warn}")
        print(f"  ✖  Failed           : {n_fail}")

        if n_fail == 0 and n_warn == 0:
            print(f"\n  🎉 Dataset passed ALL validation rules — ready for cleaning & EDA!")
        elif n_fail == 0:
            print(f"\n  ✅ No critical failures. Review {n_warn} warning(s) before proceeding.")
        else:
            print(f"\n  🚨 {n_fail} critical failure(s) detected — fix before analysis!")

        # Fix 3 — warn if any results have unknown status
        accounted = n_pass + n_warn + n_fail
        if accounted != total:
            logger.warning(f"⚠ {total - accounted} result(s) have unrecognised status and were excluded from score")

        score      = round((n_pass + n_warn * 0.5) / total * 100, 1)
        bar_filled = int(score / 5)
        bar        = "█" * bar_filled + "░" * (20 - bar_filled)
        print(f"\n  Data Quality Score  : [{bar}]  {score}%")

    def print_details(self) -> None:
        categories = sorted(set(r.category for r in self.results))
        for cat in categories:
            cat_results = [r for r in self.results if r.category == cat]
            section(f"CATEGORY: {cat}")
            for r in cat_results:
                flag = f"({r.affected:,} rows / {r.pct}%)" if r.affected > 0 else ""
                print(f"  {r.icon}  [{r.status:<4}]  {r.rule:<45} {flag}")
                # Fix 4 — show details for all statuses when present
                if r.details and (r.status != "PASS" or r.affected > 0):
                    for line in r.details.split("\n"):
                        print(f"           → {line}")




# ════════════════════════════════════════════════════════════
# VALIDATION ENGINE
# ════════════════════════════════════════════════════════════


class DataValidator:
    """
    Runs a full suite of validation checks against the
    Sales DataFrame and collects results into a ValidationReport.
    """
 
    def __init__(self, df: pd.DataFrame):
        self.df     = df.copy()
        self.n      = len(df)
        self.report = ValidationReport()
 
    def _add(self, rule: str, category: str, affected: int, threshold_warn: float = 0.0,
             threshold_fail: float = 5.0, details: str = "") -> None:
        pct = affected / self.n * 100
        if affected == 0:
            status = "PASS"
        elif pct <= threshold_warn:
            status = "PASS"
        elif pct <= threshold_fail:
            status = "WARN"
        else:
            status = "FAIL"
        self.report.add(ValidationResult(rule, category, status, affected, self.n, details))
 
    # ── 1. Schema Validation ─────────────────────────────────
    def validate_schema(self) -> None:
        logger.info("Running schema validation ...")
 
        # 1A. Required columns present
        missing_cols = [c for c in SCHEMA if c not in self.df.columns]
        self._add(
            rule     = "All required columns present",
            category = "1. Schema",
            affected = len(missing_cols),
            threshold_fail = 0,
            details  = f"Missing: {missing_cols}" if missing_cols else ""
        )
 
        # 1B. No unexpected extra columns
        extra_cols = [c for c in self.df.columns if c not in SCHEMA]
        self._add(
            rule     = "No unexpected extra columns",
            category = "1. Schema",
            affected = len(extra_cols),
            threshold_warn = 0,
            threshold_fail = 0,
            details  = f"Extra columns: {extra_cols}" if extra_cols else ""
        )
 
    # ── 2. Missing Values ────────────────────────────────────
    def validate_missing(self) -> None:
        logger.info("Running missing value validation ...")
        for col, rules in SCHEMA.items():
            if col not in self.df.columns:
                continue
            null_count = self.df[col].isnull().sum()
            self._add(
                rule     = f"No nulls in '{col}'",
                category = "2. Missing Values",
                affected = int(null_count),
                threshold_warn = 0.1,
                threshold_fail = 1.0,
            )
 
    # ── 3. Data Types ────────────────────────────────────────
    def validate_dtypes(self) -> None:
        logger.info("Running data type validation ...")
 
        # Date parseable
        try:
            parsed = pd.to_datetime(self.df["Date"], dayfirst=True, errors="coerce")
            invalid = int(parsed.isnull().sum())
        except Exception:
            invalid = self.n
        self._add(
            rule     = "'Date' column is parseable as datetime",
            category = "3. Data Types",
            affected = invalid,
            threshold_fail = 0.5
        )
 
        # Integer columns contain numeric values
        int_cols = ["Day","Year","Customer_Age","Order_Quantity",
                    "Unit_Cost","Unit_Price","Profit","Cost","Revenue"]
        for col in int_cols:
            if col not in self.df.columns:
                continue
            non_numeric = self.df[col].apply(
                lambda x: not str(x).lstrip("-").isdigit()
            ).sum()
            self._add(
                rule     = f"'{col}' contains only numeric values",
                category = "3. Data Types",
                affected = int(non_numeric),
                threshold_fail = 0
            )
 
    # ── 4. Allowed Values ────────────────────────────────────
    def validate_allowed_values(self) -> None:
        logger.info("Running allowed value validation ...")
        for col, rules in SCHEMA.items():
            if rules["allowed"] is None or col not in self.df.columns:
                continue
            invalid_mask = ~self.df[col].astype(str).isin(
                [str(v) for v in rules["allowed"]]
            )
            invalid_vals = self.df.loc[invalid_mask, col].unique()[:5].tolist()
            self._add(
                rule     = f"'{col}' contains only allowed values",
                category = "4. Allowed Values",
                affected = int(invalid_mask.sum()),
                threshold_fail = 0.5,
                details  = f"Sample invalid: {invalid_vals}" if invalid_vals else ""
            )
 
    # ── 5. Numeric Range Checks ──────────────────────────────
    def validate_ranges(self) -> None:
        logger.info("Running numeric range validation ...")
        for col, (lo, hi) in NUMERIC_RANGES.items():
            if col not in self.df.columns:
                continue
            out_of_range = ((self.df[col] < lo) | (self.df[col] > hi)).sum()
            self._add(
                rule     = f"'{col}' within range [{lo:,} – {hi:,}]",
                category = "5. Numeric Ranges",
                affected = int(out_of_range),
                threshold_warn = 0.5,
                threshold_fail = 2.0
            )
 
    # ── 6. Business Logic Checks ─────────────────────────────
    def validate_business_rules(self) -> None:
        logger.info("Running business rule validation ...")
        df = self.df
 
        # Revenue = Cost + Profit
        if all(c in df.columns for c in ["Revenue","Cost","Profit"]):
            mismatch = ((df["Revenue"] - df["Cost"] - df["Profit"]).abs() > 1).sum()
            self._add(
                rule     = "Revenue == Cost + Profit",
                category = "6. Business Logic",
                affected = int(mismatch),
                threshold_fail = 0.1
            )
 
        # Unit_Price >= Unit_Cost
        if all(c in df.columns for c in ["Unit_Price","Unit_Cost"]):
            violations = (df["Unit_Price"] < df["Unit_Cost"]).sum()
            self._add(
                rule     = "Unit_Price >= Unit_Cost",
                category = "6. Business Logic",
                affected = int(violations),
                threshold_warn = 0.1,
                threshold_fail = 1.0
            )
 
        # Negative profit rows
        if "Profit" in df.columns:
            neg_profit = (df["Profit"] < 0).sum()
            self._add(
                rule     = "Profit >= 0 (no loss-making orders)",
                category = "6. Business Logic",
                affected = int(neg_profit),
                threshold_warn = 0.1,
                threshold_fail = 2.0,
                details  = "Negative profit may indicate discounts, returns, or data errors"
            )
 
        # Revenue > 0
        if "Revenue" in df.columns:
            zero_rev = (df["Revenue"] <= 0).sum()
            self._add(
                rule     = "Revenue > 0 for all rows",
                category = "6. Business Logic",
                affected = int(zero_rev),
                threshold_fail = 0
            )
 
        # Order Quantity > 0
        if "Order_Quantity" in df.columns:
            zero_qty = (df["Order_Quantity"] <= 0).sum()
            self._add(
                rule     = "Order_Quantity > 0 for all rows",
                category = "6. Business Logic",
                affected = int(zero_qty),
                threshold_fail = 0
            )
 
    # ── 7. Age Group Consistency ─────────────────────────────
    def validate_age_consistency(self) -> None:
        logger.info("Running age group consistency validation ...")
        if not all(c in self.df.columns for c in ["Customer_Age","Age_Group"]):
            return
 
        inconsistent = 0
        for group, (lo, hi) in AGE_GROUP_RULES.items():
            mask = self.df["Age_Group"] == group
            wrong = mask & ~self.df["Customer_Age"].between(lo, hi)
            inconsistent += wrong.sum()
 
        self._add(
            rule     = "Customer_Age matches Age_Group label",
            category = "7. Consistency",
            affected = int(inconsistent),
            threshold_warn = 0.1,
            threshold_fail = 1.0,
            details  = "Age does not match the assigned age group bucket"
        )
 
        # Day consistent with month (e.g., no Feb 30)
        if all(c in self.df.columns for c in ["Day","Month","Year"]):
            try:
                date_str = (
                    self.df["Year"].astype(str) + "-" +
                    self.df["Month"].astype(str) + "-" +
                    self.df["Day"].astype(str)
                )
                parsed = pd.to_datetime(date_str, format="%Y-%B-%d", errors="coerce")
                invalid_days = parsed.isnull().sum()
                self._add(
                    rule     = "Day/Month/Year form a valid calendar date",
                    category = "7. Consistency",
                    affected = int(invalid_days),
                    threshold_fail = 0.5
                )
            except Exception:
                pass
 
    # ── 8. Duplicate Check ───────────────────────────────────
    def validate_duplicates(self) -> None:
        logger.info("Running duplicate validation ...")
        n_dupes = int(self.df.duplicated().sum())
        self._add(
            rule     = "No fully duplicate rows",
            category = "8. Duplicates",
            affected = n_dupes,
            threshold_warn = 0.1,
            threshold_fail = 1.0,
            details  = "Drop with df.drop_duplicates() in cleaning step"
        )
 
    # ── 9. Date Range Check ──────────────────────────────────
    def validate_date_range(self) -> None:
        logger.info("Running date range validation ...")
        try:
            parsed = pd.to_datetime(self.df["Date"], dayfirst=True, errors="coerce")
 
            # Dates in expected business range
            out_of_range = ((parsed.dt.year < 2011) | (parsed.dt.year > 2016)).sum()
            self._add(
                rule     = "All dates fall within 2011–2016 range",
                category = "9. Date Integrity",
                affected = int(out_of_range),
                threshold_fail = 0.5
            )
 
            # Year column matches Date year
            if "Year" in self.df.columns:
                mismatch = (parsed.dt.year != self.df["Year"]).sum()
                self._add(
                    rule     = "'Year' column matches year in 'Date'",
                    category = "9. Date Integrity",
                    affected = int(mismatch),
                    threshold_fail = 0.1
                )
 
            # Month column matches Date month
            if "Month" in self.df.columns:
                month_map = {
                    1:"January",2:"February",3:"March",4:"April",
                    5:"May",6:"June",7:"July",8:"August",
                    9:"September",10:"October",11:"November",12:"December"
                }
                derived_month = parsed.dt.month.map(month_map)
                mismatch_month = (derived_month != self.df["Month"]).sum()
                self._add(
                    rule     = "'Month' column matches month in 'Date'",
                    category = "9. Date Integrity",
                    affected = int(mismatch_month),
                    threshold_fail = 0.1
                )
 
            # Day column matches Date day
            if "Day" in self.df.columns:
                mismatch_day = (parsed.dt.day != self.df["Day"]).sum()
                self._add(
                    rule     = "'Day' column matches day in 'Date'",
                    category = "9. Date Integrity",
                    affected = int(mismatch_day),
                    threshold_fail = 0.1
                )
        except Exception as e:
            logger.warning(f"Date range validation skipped: {e}")

 
    # ── RUN ALL ──────────────────────────────────────────────
    def run_all(self) -> ValidationReport:
        """Execute all validation checks and return the full report."""
        self.validate_schema()
        self.validate_missing()
        self.validate_dtypes()
        self.validate_allowed_values()
        self.validate_ranges()
        self.validate_business_rules()
        self.validate_age_consistency()
        self.validate_duplicates()
        self.validate_date_range()
        return self.report





# ════════════════════════════════════════════════════════════
# HELPER — FAILED ROWS EXPORT
# ════════════════════════════════════════════════════════════
 
def export_flagged_rows(df: pd.DataFrame, output_path: str = "flagged_rows.csv") -> None:
    """
    Export all rows with known data quality issues to a CSV
    for manual review or downstream fixing.
 
    Parameters
    ----------
    df          : Raw DataFrame
    output_path : Where to save flagged rows
    """
    section("EXPORTING FLAGGED ROWS")
    flags = pd.Series([""] * len(df), index=df.index)
 
    # Negative profit
    mask_neg  = df["Profit"] < 0
    flags[mask_neg] += "negative_profit|"
 
    # Duplicates
    mask_dup  = df.duplicated(keep=False)
    flags[mask_dup] += "duplicate|"
 
    # Revenue ≠ Cost + Profit
    mask_rev  = (df["Revenue"] - df["Cost"] - df["Profit"]).abs() > 1
    flags[mask_rev] += "revenue_mismatch|"
 
    # Age group mismatch
    for group, (lo, hi) in AGE_GROUP_RULES.items():
        m = (df["Age_Group"] == group) & ~df["Customer_Age"].between(lo, hi)
        flags[m] += "age_group_mismatch|"
 
    flagged = df[flags != ""].copy()
    flagged["issue_flags"] = flags[flags != ""].str.rstrip("|")
 
    if flagged.empty:
        logger.info("✔ No flagged rows to export — dataset is clean!")
    else:
        flagged.to_csv(output_path, index=False)
        logger.info(f"⚠ {len(flagged):,} flagged rows exported → '{output_path}'")
        logger.info(f"  Issue breakdown:")
        for issue in ["negative_profit", "duplicate", "revenue_mismatch", "age_group_mismatch"]:
            count = flagged["issue_flags"].str.contains(issue).sum()
            if count:
                logger.info(f"    • {issue:<30} {count:,} rows")





# ════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ════════════════════════════════════════════════════════════
 
def validate_dataset(file_path: str) -> ValidationReport:
    """
    Full dataset validation pipeline.
 
    Parameters
    ----------
    file_path : str
        Path to Sales.csv
 
    Returns
    -------
    ValidationReport
        Complete report with all rule results.
    """
    print(f"\n{'=' * 65}")
    print("   BIKE SALES — PROFESSIONAL DATA VALIDATION PIPELINE")
    print(f"{'=' * 65}")
 
    # Load
    path = Path(file_path)
    if not path.exists():
        logger.critical(f"File not found: {file_path}")
        sys.exit(1)
 
    logger.info(f"Loading dataset: {path.name}")
    df = pd.read_csv(file_path)
    logger.info(f"Loaded {df.shape[0]:,} rows × {df.shape[1]} columns")
 
    # Run validation
    validator = DataValidator(df)
    report    = validator.run_all()
 
    # Print detailed results
    report.print_details()
 
    # Print summary
    report.print_summary()
 
    # Export flagged rows
    flagged_path = "/home/claude/flagged_rows.csv"
    export_flagged_rows(df, output_path=flagged_path)
 
    # Exit with error code if critical failures found
    if report.failures:
        logger.error(f"Validation completed with {len(report.failures)} FAILURE(S)")
    else:
        logger.info("Validation completed successfully ✅")
 
    return report
 


# ════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════
 
if __name__ == "__main__":
    FILE_PATH = "Sales.csv"         # ← Change path if needed
    report = validate_dataset(FILE_PATH)







