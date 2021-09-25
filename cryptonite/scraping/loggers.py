import logging
import sys


def setup_loggers(start_date, end_date, publisher, output_dir):
    start_date = start_date.replace('/', '-')
    end_date = end_date.replace('/', '-')

    logger = logging.getLogger(publisher)
    logger.setLevel(logging.INFO)

    logging_path = output_dir.joinpath(f'{publisher}-{start_date}-{end_date}.log')
    fh = logging.FileHandler(logging_path)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.WARNING)
    logger.addHandler(ch)
