from ast import literal_eval
import html

import pandas as pd

from cryptonite.preprocessing.common import (
    invalid_answer_pattern, standard_apostrophe, alternative_apostrophes, standard_quotation_mark,
    alternative_quotation_marks, standard_ellipsis, alternative_ellipses, standardize_punctuation,
    load_scraped_df, save_df_as_jsonl, standard_date_format
)


def standardize_html(df):
    """ For the reasoning behind this implementation, see the `the-times_standardize_html` notebook
    """
    df['clue'] = df['clue'].apply(html.unescape).apply(html.unescape)
    df['answer'] = df['answer'].apply(html.unescape)
    return df


def standardize_enumeration(df):
    """ For the reasoning behind this implementation, see the `the-times_enumeration` notebook
    """
    df['enumeration'] = df['enumeration'].str.replace(' ', '')
    df['enumeration'] = df['enumeration'].str.replace('-', ',')
    df['enumeration'] = '(' + df['enumeration'] + ')'
    df['enumeration'] = df['enumeration'].str.replace(',,', ',')
    df['enumeration'] = df['enumeration'].str.replace(',\)', ')')

    return df


def validate_enumeration(df):
    """ For the reasoning behind this implementation, see the `the-times_enumeration` notebook
    """
    return df


def standardize_orientation(df):
    """ For the reasoning behind this implementation, see the `the-times_orientation` notebook
    """
    df['orientation'] = df['orientation'].str.lower()

    return df


def validate_orientation(df):
    """ For the reasoning behind this implementation, see the `the-times_orientation` notebook
    """
    # I'm writing this line even if currently all the orientations are valid
    df = df[(df['orientation'] == 'across') | (df['orientation'] == 'down')]

    return df


def standardize_answers(df):
    """ For the reasoning behind this implementation, see the `the-times_standardize_answer` notebook
    """
    df['answer'] = df['answer'].str.lower()
    df['answer'] = df['answer'].str.replace(' ', '')
    df['answer'] = df['answer'].str.replace('-', '')

    return df


def validate_answers(df):
    """ For the reasoning behind this implementation, see the `the-times_validate_answers` notebook
    """
    # only allow certain characters in answer
    df = df[~df['answer'].str.contains(invalid_answer_pattern)]

    # assume enumeration was validated

    # remove entries with answers that do not match the enumeration
    df['tmp_enumeration'] = df['enumeration'].str.replace(')', ',)')
    df['tmp_enumeration'] = df['tmp_enumeration'].apply(literal_eval)

    df['chars_in_answer'] = df['tmp_enumeration'].apply(sum)
    df = df[df['answer'].str.len() == df['chars_in_answer']]
    df = df.drop('chars_in_answer', axis='columns')

    # add spaces to answer
    def add_spaces_to_answer(answer, enumeration):
        if len(enumeration) > 1:
            word_start = 0
            answer_words = []
            for word_length in enumeration:
                answer_words.append(answer[word_start: word_start + word_length])
                word_start += word_length
            answer = ' '.join(answer_words)
        return answer

    df['answer'] = df.apply(lambda x: add_spaces_to_answer(x['answer'], x['tmp_enumeration']), axis=1)
    df = df.drop('tmp_enumeration', axis='columns')

    return df


def standardize_clues(df):
    """ For the reasoning behind this implementation, see the `telegraph_standardize_clues` notebook
    """
    # make lowercase
    df['clue'] = df['clue'].str.lower()

    # standardize apostrophes
    df['clue'] = df['clue'].apply(standardize_punctuation,
                                  args=(standard_apostrophe, alternative_apostrophes))

    # normalize quotation marks
    df['clue'] = df['clue'].apply(standardize_punctuation,
                                  args=(standard_quotation_mark, alternative_quotation_marks))

    # normalize ellipses
    df['clue'] = df['clue'].apply(standardize_punctuation,
                                  args=(standard_ellipsis, alternative_ellipses))

    return df


def validate_clues(df):
    """ For the reasoning behind this implementation, see the `the-times_validate_clues` notebook
    """
    # assume clues were validated

    # remove multi-part clues
    df = df[~df['clue'].str.contains('^& \d+')]
    df = df[~df['clue'].str.contains('^see \d+')]
    df = df[~df['clue'].str.contains('^and \d+')]
    df = df[~df['clue'].str.contains('^with \d+')]

    # remove direct reference clues
    df = df[~df['clue'].str.contains('\d+ across')]
    df = df[~df['clue'].str.contains('\d+ down')]

    return df


def assign_quickness(df):
    """ For the reasoning behind this implementation, see the `the-times_quickness` notebook
    """
    df['quick'] = df['title'].str.contains("Quick")

    return df


def assign_publisher(df):
    """ For the reasoning behind this implementation, see the `the-times_publisher` notebook
    """
    df['sub_publisher'] = df['publisher']
    df['publisher'] = "Times"

    return df


def standardize_dates(df):
    """ For the reasoning behind this implementation, see the `the-times_standardize_dates` notebook
    """
    df['date'] = pd.to_datetime(df['date'], format=standard_date_format)
    return df


def preprocess(input_path, output_path=None):
    """For now I'm keeping the logic of the Telegraph and Times preprocess seperate, even thought it
    is almost the same, and can be easily made identical"""

    df = load_scraped_df('the-times', input_path=input_path)
    num_entries_before_preprocessing = len(df)
    print(f'num entries in {input_path} -- {num_entries_before_preprocessing}')

    df = standardize_html(df)
    df = standardize_enumeration(df)
    df = validate_enumeration(df)
    df = standardize_orientation(df)
    df = validate_orientation(df)
    df = standardize_answers(df)
    df = validate_answers(df)
    df = standardize_clues(df)
    df = validate_clues(df)
    df = assign_quickness(df)
    df = assign_publisher(df)
    df = standardize_dates(df)

    print(f'num entries after preprocessing -- {len(df)}')
    print(f'percentage of entries remaining: {len(df) / num_entries_before_preprocessing * 100:.2f}')

    if output_path is not None:
        print(f'saving in {output_path}...')
        save_df_as_jsonl(df, output_path)
        print(f'successfully saved!')

    return df
