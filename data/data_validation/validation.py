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
 



@dataclass
class ValidationResult:
    rule        : str
    category    : str
    status      : str          
    affected    : int = 0
    total       : int = 0
    details     : str = ""
 
    @property
    def pct(self) -> float:
        return round(self.affected / self.total * 100, 2) if self.total else 0.0
 
    @property
    def icon(self) -> str:
        return {"PASS": "✔", "WARN": "⚠", "FAIL": "✖"}[self.status]
 















