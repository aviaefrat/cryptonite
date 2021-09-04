import logging
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup

from cryptonite.scraping.telegraph.client import client


logger = logging.getLogger('telegraph')


def fetch_raw_crossword_pages(puzzle_id):
    # use the print version
    # with the same url you can one time get the clue and by setting the param "action"
    # to be "solution" you get the answers
    url = 'https://puzzles.telegraph.co.uk/print_crossword'
    params = {'id': puzzle_id}
    clues_text = client.get(url, params=params)
    answers_text = client.get(url, params={**params, 'action': 'solution'})
    return clues_text, answers_text


def extract_entires_from_raw_pages(puzzle_url, puzzle_id, clues_raw_page, answers_raw_page):
    # arbitrarily use the clues raw page for the shared fields (like title),
    # it would probably be the same if we use the answers page
    header_soup = BeautifulSoup(clues_raw_page, 'html.parser')
    title_cell = header_soup.find_all('td', class_='telegraph')[0]
    title = title_cell.contents[2].split(' ', 1)[1]
    date_cell = list(title_cell.next_siblings)[1]
    raw_date = date_cell.contents[0].strip()
    date = datetime.strptime(raw_date, '%a %d %b %y').strftime('%d/%m/%Y')

    def extract_table(table):
        # TODO do I handle that obscure case where one answer is "null" or something and then pandas
        #  parses it as Nan or None or something?
        df = pd.read_html(str(table))[0]
        df.columns = ['number', 'other']
        df.set_index = 'number'
        records = df.to_dict('records')
        return sorted(records, key=lambda r: r['number'])

    def extract_tables(text):
        table_soup = BeautifulSoup(text, 'html.parser')
        all_tables = table_soup.find_all('table')
        # hopefully it will remain 4 and 5, for now we keep this hacky extraction
        across_table, down_table = all_tables[4], all_tables[5]
        return {
            'Across': extract_table(across_table),
            'Down': extract_table(down_table),
        }

    clues_raw_data = extract_tables(clues_raw_page)
    answers_raw_data = extract_tables(answers_raw_page)

    result = []
    for orientation, answer_records in answers_raw_data.items():
        clue_records = clues_raw_data[orientation]
        for clue_record, ans_record in zip(clue_records, answer_records):
            try:
                number = clue_record['number']
                clue_other = clue_record['other']
                clue, enumeration = clue_other.rsplit(' ', 1)
                answer = ans_record['other']
                result.append({
                    'url': puzzle_url,
                    'publisher': 'Telegraph',
                    'crossword_id': puzzle_id,
                    'date': date,
                    'title': title,
                    # TODO look for an author or setter more closely
                    'number': number,
                    'orientation': orientation,
                    'clue': clue,
                    'answer': answer,
                    'enumeration': enumeration
                })
            except Exception:  # TODO yes this is too broad. I just what to see what happens for now
                logger.info(f"PAIR problem found in: {puzzle_url}\n"
                            f"{orientation} {clue_record['number']} --- "
                            f"CLUE: {clue_record['other']} "
                            f"ANSWER: {ans_record['other']}\n",
                            exc_info=True)
    return result


def fetch_crossword_entries(puzzle_url):
    # we build the final url so we know that puzzle url contains a single query parameter: puzzle_id
    puzzle_id = puzzle_url.split('=')[-1]
    clues_raw_page, answers_raw_page = fetch_raw_crossword_pages(puzzle_id)
    return extract_entires_from_raw_pages(
        puzzle_url=puzzle_url,
        puzzle_id=puzzle_id,
        clues_raw_page=clues_raw_page,
        answers_raw_page=answers_raw_page,
    )


def main():
    puzzle_id = '40870'
    puzzle_url = f'https://puzzles.telegraph.co.uk/puzzle?puzzle_id={puzzle_id}'
    data = fetch_crossword_entries(puzzle_url)
    import pprint
    pprint.pprint(data)


if __name__ == '__main__':
    main()
