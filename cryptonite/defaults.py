from pathlib import Path

CRYPTONITE_ROOT_DIR = Path(__file__).parent.joinpath("..").resolve()
CONFIG_DIR = CRYPTONITE_ROOT_DIR.joinpath("configs")
DATA_DIR = CRYPTONITE_ROOT_DIR.joinpath("data")

SCRAPED_TELEGRAPH_PATH = DATA_DIR.joinpath("the_telegraph-26-11-2001-31-10-2020.jsonl")
SCRAPED_TIMES_PATH = DATA_DIR.joinpath("the_times-16-10-2000-31-10-2020.jsonl")

DATASET_FILENAME = "cryptonite_v1.jsonl"
DATASET_PATH = DATA_DIR.joinpath(DATASET_FILENAME)
DATASET_WITHOUT_ENUMERATION_FILENAME = "cryptonite_v1_non_enumerated.jsonl"
DATASET_WITHOUT_ENUMERATION_PATH = DATA_DIR.joinpath(DATASET_WITHOUT_ENUMERATION_FILENAME)

V1_CONFIGURATION_PATH = CONFIG_DIR.joinpath("scraping/cryptonite_v1.json")
