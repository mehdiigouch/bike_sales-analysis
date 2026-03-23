import logging
from pathlib import Path


# ════════════════════════════════════════════════════════════
# CREATING LOGGING FUNCTIONALITY
# ════════════════════════════════════════════════════════════

logging.basicConfig(

level = logging.INFO,
format = "%(asctime)s  [%(levelname)s]  %(message)s",
datefmt = "%Y-%m-%d %H:%M:%S",

)

logger = logging.getLogger(__name__)




# ════════════════════════════════════════════════════════════
# CREATING  SECTION FUNCTIONALITY
# ════════════════════════════════════════════════════════════

def section(title: str) -> None:
    SEPARATOR = "=" * 65
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)



# ════════════════════════════════════════════════════════════
# CREATING  DATASET PATH FUNCTIONALITY
# ════════════════════════════════════════════════════════════


def data_root() -> Path:
 PATH_ROOT  = Path.cwd().parent
 DATASET_ROOT = PATH_ROOT /"Sales.csv"
 return DATASET_ROOT




