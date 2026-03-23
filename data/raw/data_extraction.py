
#  uv run python data/raw/data_extraction.py  IF YOU WANNA RUN THE CODE USE THIS COMMAND 
import pandas as pd
from utils.logs import section,logger,data_root
from pathlib import Path
import time


# ════════════════════════════════════════════════════════════
# STEP 1 — VALIDATE FILE EXISTS
# ════════════════════════════════════════════════════════════

def validate_file(file_path: str) -> Path:
    section("STEP 1 — FILE VALIDATION")
    path = Path(file_path).resolve()

    # Check existence
    if not path.exists():
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(f" File not found: {path}")    # fix this add logger error
    logger.info(f" File found      : {path.name}")

    # Check extension
    if path.suffix.lower() != ".csv":
        raise ValueError(f" Expected a .csv file, got: '{path.suffix}'")       # fix this add logger error
    logger.info(f" File extension  : {path.suffix}")


    # Check file size
    size_kb = path.stat().st_size / 1024
    size_mb = size_kb / 1024
    logger.info(f" File size       : {size_mb:.2f} MB ({size_kb:,.1f} KB)")
    if path.stat().st_size == 0:
        raise ValueError(" File is empty (0 bytes).")     # fix this add logger error

    logger.info(f" Full path       : {path}")

    return path

# ════════════════════════════════════════════════════════════
# STEP 2 — LOAD RAW DATA
# ════════════════════════════════════════════════════════════

def load_raw_data(path: Path) -> pd.DataFrame:

    section("STEP 2 — LOADING DATA")
    logger.info("Reading CSV file ...")

    start = time.time()

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        logger.error("The file is empty or has no columns.")  # ADD LOGGER EXCEPTION & HANDLER TO FILE.log
        raise
    except pd.errors.ParserError as e:
        logger.error(f"CSV parsing error: {e}")   # ADD LOGGER EXCEPTION & HANDLER TO FILE.log
        raise
    elapsed = time.time() - start

    logger.info(f"Loaded in        : {elapsed:.2f} seconds")
    logger.info(f" Rows            : {df.shape[0]:,}")
    logger.info(f" Columns         : {df.shape[1]}")
    logger.info(f" Memory usage    : {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    logger.info(f" Column names    : {df.columns.tolist()}")

    return df



# ════════════════════════════════════════════════════════════
# AFTER WE EXTRACT THE DATA WE WILL TRANSFORM IT IN THE  data/interim/data_transformation.py FILE  
# ════════════════════════════════════════════════════════════





