import logging

logging.basicConfig(

level = logging.INFO,
format = "%(asctime)s  [%(levelname)s]  %(message)s",
datefmt = "%Y-%m-%d %H:%M:%S"

)

logger = logging.getLogger(__name__)




def section(title: str) -> None:
    SEPARATOR = "=" * 65
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


