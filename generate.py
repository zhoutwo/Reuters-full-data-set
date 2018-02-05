import os
import re
import pickle
from datetime import timedelta, date, datetime

import bs4
import requests


def get_soup_from_link(link):
    if not link.startswith('http://www.reuters.com'):
        link = 'http://www.reuters.com' + link
    # print(link)
    response = requests.get(link)
    assert response.status_code == 200
    return bs4.BeautifulSoup(response.content, 'html.parser')


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def run_full():
    today = datetime.now()
    output_dir = 'output_' + today.strftime('%Y-%m-%d-%HH%MM')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print('Generating the Full dataset in : {}'.format(output_dir))
    start_date = date(2016, 1, 1)
    end_date = today.date()
    iterations = 0

    forbidden_terms = [
        'PRESS DIGEST'
    ]
    reuters_label = '(Reuters) - '

    for single_date in date_range(start_date, end_date):
        output = []
        string_date = single_date.strftime("%Y%m%d")
        link = 'http://www.reuters.com/resources/archive/us/{}.html'.format(string_date)
        try:
            soup = get_soup_from_link(link)
            targets = soup.find_all('div', {'class': 'headlineMed'})
            for target in targets:
                try:
                    timestamp = str(string_date) + str(target.contents[1])
                except Exception:
                    timestamp = None
                    # print('EXCEPTION RAISED. Timestamp set to None. Resuming.')

                title = str(target.contents[0].contents[0])

                forbidden = False
                for forbidden_term in forbidden_terms:
                    if forbidden_term in title:
                        forbidden = True
                        break

                if forbidden:
                    continue

                title = re.sub('GLOBAL ECONOMY.*-', '', title)
                title = re.sub('FACTBOX.*-', '', title)
                title = re.sub('CORRECTED.*-', '', title)
                title = title.replace('Factbox:', '')
                title = re.sub('CANADA STOCKS.*-', '', title)
                title = re.sub('US STOCKS SNAPSHOT.*-', '', title)
                title = re.sub('FOREX.*-', '', title)
                title = re.sub('WRAPUP.*-', '', title)
                title = re.sub('PRECIOUS.*-', '', title)
                title = re.sub('GLOBAL MARKETS.*-', '', title)
                title = re.sub('RPT.*-', '', title)
                title = re.sub('MIDEAST STOCKS.*-', '', title)
                title = re.sub('INTERVIEW.*-', '', title)
                title = title.replace('Exclusive:', '')
                title = re.sub('UPDATE.*-', '', title)
                title = re.sub(' -.*', '', title)
                title = title.replace('-source', '')
                title = title.replace('-sources', '')
                title = title.replace(': sources', '')
                title = title.replace('- sources', '')
                title = title.replace(': source', '')
                title = title.replace('- source', '')
                title = title[:-8] + re.sub(' - .*', '', title[-8:])
                title = title.strip()
                if len(title) < 20 or title[0].islower() or len(title.split()) < 5:
                    continue
                title = title.encode('UTF-8')

                href = str(target.contents[0].attrs['href'])
                try:
                    article_soup = get_soup_from_link(href)
                    body_sentences = article_soup.select('div.StandardArticleBody_body_1gnLA > p')
                    for body_sentence in body_sentences:
                        body_sentence = str(body_sentence)
                        body_sentence = body_sentence.strip('</p>')

                        if reuters_label in body_sentence:
                            body_sentence = body_sentence[body_sentence.find(reuters_label)+len(reuters_label):]
                            body_sentence = re.sub('\(.*\) ', '', body_sentence)
                            body_sentence = re.sub('\[.*\] ', '', body_sentence)

                            if len(body_sentence) < len(title):
                                continue

                            sentence_ending = '. '
                            if sentence_ending in body_sentence:
                                body_sentence = body_sentence.strip()
                                body_sentence = body_sentence.encode('UTF-8')

                                print('iterations = {}, t = {}, h = {}, fl = {}'.format(str(iterations).zfill(9), title, href, body_sentence))
                                output.append({'ts': timestamp, 'title': title, 'href': href, 'first_line': body_sentence})
                                iterations += 1
                                break

                except Exception:
                    pass
                    # print('EXCEPTION RAISED. Could not download link : {}. Skipping.'.format(href))

            output_filename = os.path.join(output_dir, string_date + '.pkl').format(output_dir, string_date)
            with open(output_filename, 'wb') as w:
                pickle.dump(output, w)
            print('-> written dump to {}'.format(output_filename))
        except Exception:
            pass
            # print('EXCEPTION RAISED. Could not download link : {}. Skipping.'.format(link))


if __name__ == '__main__':
    run_full()
