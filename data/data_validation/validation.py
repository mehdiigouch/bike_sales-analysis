import pandas as pd
import numpy as np
import sys
from pathlib import Path
from dataclasses import dataclass, field  # create constructors automatically for classes
#Think of field() as a way to control how a variable inside a dataclass behaves.
from typing import List, Callable  #Callable means a function that can be passed as an argument.
#List is used to indicate that a variable should contain a list of a specific type.

from utils.logs import section, logger
from data.raw.data_extraction import  DATASET_ROOT, validate_file, load_raw_data



DATASET = load_raw_data(validate_file(DATASET_ROOT))

print(DATASET.head(5))











print("This is the dathere after we have transformed it in the")









