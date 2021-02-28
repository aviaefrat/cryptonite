from ast import literal_eval
import html

import pandas as pd

from cryptonite.preprocessing.common import (
    valid_enumeration_pattern, invalid_answer_pattern, standard_apostrophe, alternative_apostrophes,
    standard_quotation_mark, alternative_quotation_marks, standardize_punctuation, load_scraped_df,
    save_df_as_jsonl, standard_date_format
)


def standardize_html(df):

    df['clue'] = df['clue'].apply(html.unescape)

    return df


def standardize_enumeration(df):

    df['enumeration'] = df['enumeration'].str.replace('-', ',')
    df['enumeration'] = df['enumeration'].str.replace('{', '(')
    df['enumeration'] = df['enumeration'].str.replace('}', ')')

    return df


def validate_enumeration(df):

    df = df[df['enumeration'].str.contains(valid_enumeration_pattern)]

    return df


def standardize_orientation(df):

    df['orientation'] = df['orientation'].str.lower()

    return df


def validate_orientation(df):

    # I'm writing this line even if currently all the orientations are valid
    df = df[(df['orientation'] == 'across') | (df['orientation'] == 'down')]

    return df


def standardize_answers(df):

    none_answers_df = df[df['answer'].isna()]
    for index in none_answers_df.index:
        df.at[index, 'answer'] = 'None'

    df['answer'] = df['answer'].str.lower()
    df['answer'] = df['answer'].str.replace(' ', '')

    return df


def validate_answers(df):

    # only allow certain characters in answer
    df = df[~df['answer'].str.contains(invalid_answer_pattern)]

    # assume enumeration was validated

    # remove entries with answers that do not match the enumeration
    df['tmp_enumeration'] = df['enumeration']
    df['tmp_enumeration'] = df['tmp_enumeration'].str.replace(')', ',)')
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

    # make lowercase
    df['clue'] = df['clue'].str.lower()

    # standardize apostrophes
    df['clue'] = df['clue'].apply(standardize_punctuation,
                                  args=(standard_apostrophe, alternative_apostrophes))

    # normalize quotation marks
    df['clue'] = df['clue'].apply(standardize_punctuation,
                                  args=(standard_quotation_mark, alternative_quotation_marks))

    return df


def validate_clues(df):

    # assume clues were validated

    # remove multi-part clues
    df = df[~df['clue'].str.contains('^& \d+')]
    df = df[~df['clue'].str.contains('^see \d+')]
    df = df[~df['clue'].str.contains('^and \d+')]

    # remove direct reference clues
    df = df[~df['clue'].str.contains('\d+ across')]
    df = df[~df['clue'].str.contains('\d+ down')]

    return df


def assign_quickness(df):
    """ There are no quick crosswords in the telegraph """
    df['quick'] = False

    return df


def assign_publisher(df):

    return df


def standardize_dates(df):

    df['date'] = pd.to_datetime(df['date'], format=standard_date_format)
    return df


def preprocess(input_path, output_path=None):
    """For now the logic of the Telegraph and Times preprocessing is separate, even though it
    is almost the same, and could be easily made identical"""

    df = load_scraped_df('telegraph', input_path=input_path)
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


if __name__ == '__main__':
    preprocess(None, output_path='../data/telegraph_preprocessed.jsonl')
