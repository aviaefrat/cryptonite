import logging
import os
import sys


def setup_loggers(p_from, p_to, publisher, output_dir):
    p_from = p_from.replace('/', '-')
    p_to = p_to.replace('/', '-')

    logger = logging.getLogger(publisher)
    logger.setLevel(logging.INFO)

    logging_path = os.path.join(output_dir, f'{publisher}-{p_from}-{p_to}.log')
    fh = logging.FileHandler(logging_path)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.WARNING)
    logger.addHandler(ch)
