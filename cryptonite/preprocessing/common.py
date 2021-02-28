import re

import pandas as pd

scraping_paths = {
    'telegraph': '../../data/telegraph-raw.jsonl',
    'the-times': '../../data/the-times-raw.jsonl'
}

standard_date_format = '%d/%m/%Y'
valid_enumeration_pattern = re.compile("^\(\d+(?:,\d+)*\)$")
invalid_answer_pattern = re.compile("[^a-z]")

standard_apostrophe = "'"
alternative_apostrophes = ["`", "ʻ", "ʼ", "ʽ", "‘", "’", "′", "‵", "＇"]
standard_quotation_mark = '"'
alternative_quotation_marks = ["«", "»", "“", "”", "„", "‟", "''"]
standard_ellipsis = '...'
alternative_ellipses = ['\u2026']

default_dtypes = {'clue': pd.StringDtype(),
                  'answer': pd.StringDtype(),
                  'enumeration': pd.StringDtype()}


def load_scraped_df(name, input_path=None, dtypes=None):

    path = scraping_paths[name]

    # late addition, didn't make `name` keyword argument because I don't want to go over all the
    # preprocessing notebooks and change stuff right now.
    if input_path is not None:
        path = input_path

    if dtypes is None:
        dtypes = default_dtypes

    return pd.read_json(path,
                        orient='columns',
                        convert_dates=False,
                        dtype=dtypes,
                        lines=True)


def save_df_as_jsonl(df, output_path):
    df.to_json(output_path, orient='records', lines=True)


def standardize_punctuation(s, standard, alternatives):
    for alternative in alternatives:
        s = s.replace(alternative, standard)
    return s
