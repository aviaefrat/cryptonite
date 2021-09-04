import html
import logging
import json
from datetime import datetime

from bs4 import BeautifulSoup

from cryptonite.scraping.the_times.client import client


logger = logging.getLogger('the-times')


def fetch_raw_crossword_page(page_id):
    url = f'https://www.thetimes.co.uk/puzzleclub/crosswordclub/play/crossword/{page_id}'
    params = {'header': 'false'}
    return client.get(url, params=params)


def extract_raw_crossword_page_data(raw_page):
    soup = BeautifulSoup(raw_page, features='html.parser')
    scripts = soup.find_all('script')
    data_script = scripts[-3].contents[0]
    data_line_prefix = 'oApp.puzzle_json = '
    assert data_line_prefix in data_script
    data_script_lines = data_script.split('\n')
    data_line = None
    for line in data_script_lines:
        line = line.strip()
        if line.startswith(data_line_prefix):
            data_line = line
            break
    if not data_line:
        raise RuntimeError('Format changed. Need to reverse engineer it again')
    data_line = data_line[len(data_line_prefix):]
    if data_line.endswith(';'):
        data_line = data_line[:-1]
    return json.loads(data_line)


def clean_and_extract_raw_page_data(puzzle_url, raw_page_data):
    copy = raw_page_data['data']['copy']
    # the "id" field is not the crossword_id we want
    # we want the unique number at the end of the puzzle url.
    # yes it is specific to the way the times built their site, but as I don't know what the "id"
    # field is based on, I'd rather go with something unique _plus_ visible on the site.
    puzzle_id = puzzle_url.split('/')[-1]
    # the title is important as it contains (among other things) when the crossword is "quick".
    title = copy['title']
    author = copy.get('byline') or ''  # 'setter' field seems to include the same value
    # 'setter' seems to include the same information as 'byline'.
    # but in case it doesn't, let's keep both and wait for analysis.
    setter = copy.get('setter')
    publisher = copy['publisher']
    raw_publish_date = copy['date-publish-analytics'].split(' ')[0]  # '2020/04/10 00:00 friday'
    publish_date = datetime.strptime(raw_publish_date, '%Y/%m/%d').strftime('%d/%m/%Y')
    result = []
    all_entries = copy['clues']
    for entries_by_orientation_dict in all_entries:
        orientation = entries_by_orientation_dict['title']
        entries_by_orientation = entries_by_orientation_dict['clues']
        for entry in entries_by_orientation:
            try:
                number = int(entry['number'])
                clue = entry['clue']
                answer = entry['answer']
                demarcation = entry.get('demarcation')
                # there seems to be an inconsistency w.r.t enumeration format.
                # i saw two formats:
                # 1) 2-3
                # 2) 2,3
                # remember that when analyzing
                enumeration = entry['format']
                # the length is supposed to be the sum of the numbers in the enumeration.
                # so it is supposedly redundant to keep it, but I'll keep it anyway for analysis,
                # as I remember that the length of the answer string and the enumeration data do not
                # always match
                length = entry['length']

                result.append({
                    'url': puzzle_url,
                    # TODO there are two entries in the scraped data with an odd urls.
                    #  https://www.thetimes.co.uk/puzzleclub/crosswordclub/puzzles/crossword/history38822
                    #  https://www.thetimes.co.uk/puzzleclub/crosswordclub/puzzles/crossword/history38850
                    #  Understand and fix
                    'publisher': publisher,
                    'crossword_id': puzzle_id,
                    'date': publish_date,
                    'title': title,
                    'author': author,
                    'setter': setter,
                    'number': number,
                    'orientation': orientation,
                    'clue': clue,
                    'answer': answer,
                    'demarcation': demarcation,
                    'enumeration': enumeration,
                    'length': length
                })
            except Exception:  # TODO yes this is too broad. I just what to see what happens for now
                logger.info(f"ENTRY problem found in: {puzzle_url}\n"
                            f"{orientation} {int(entry['number'])} --- "
                            f"CLUE: {entry['clue']} "
                            f"ANSWER: {entry['answer']}\n",
                            exc_info=True)
    return result


def fetch_crossword_entries(puzzle_url):
    page_id = puzzle_url.split('/')[-1]
    raw_page = fetch_raw_crossword_page(page_id)
    raw_page_data = extract_raw_crossword_page_data(raw_page)
    return clean_and_extract_raw_page_data(puzzle_url, raw_page_data)


def main():
    puzzle_url = 'https://www.thetimes.co.uk/puzzleclub/crosswordclub/puzzles/crossword/41395'
    data = fetch_crossword_entries(puzzle_url)
    import pprint
    pprint.pprint(data)


if __name__ == '__main__':
    main()
