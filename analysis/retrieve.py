import pandas as pd
import re
import numpy as np
from clients import arxiv
from clients import ieeexplore
from clients import springer
from clients import elsevier
from clients import core
from analysis import util
from os.path import exists

fr = 'utf-8'


def get_papers(domains, interests, keywords, synonyms, fields, types):
    for domain in domains:
        print("Requesting ArXiv for " + domain + " related papers...")
        arxiv.get_papers(domain, interests, keywords, synonyms, fields, types)

        print("Requesting Springer for " + domain + " related papers...")
        springer.get_papers(domain, interests, keywords, synonyms, fields, types)

        #print("Requesting IEEE Xplore for " + domain + " related papers...")
        #ieeexplore.get_papers(domain, interests, keywords, synonyms, fields, types)

        print("Requesting Elsevier for " + domain + " related papers...")
        elsevier.get_papers(domain, interests, keywords, synonyms, fields, types)
        # 2.1 Getting abstracts from elsevier
        print('2.1 Getting abstracts from Sciencedirect...')
        get_abstracts_elsevier(domains)

        print("Requesting CORE for " + domain + " related papers...")
        core.get_papers(domain, interests, keywords, synonyms, fields, types)


def get_abstracts_elsevier(domains):
    for domain in domains:
        print('Domain: ' + domain)
        elsevier.process_raw_papers(domain)


def preprocess(domains, databases):
    papers = pd.DataFrame()
    for domain in domains:
        for database in databases:
            file_name = './papers/domains/'+domain.lower().replace(' ', '_') + '_' + database + '.csv'
            if exists(file_name):
                print(file_name)
                df = pd.read_csv(file_name)
                if database == 'ieeexplore':
                    df = df.drop_duplicates(subset=['doi'])
                    dates = df['publication_date']
                    df['publication_date'] = parse_dates(dates)
                    papers_ieee = pd.DataFrame(
                        {'doi': df['doi'], 'type': df['content_type'],
                        'publication': df['publication_title'], 'publisher': df['publisher'],
                        'publication_date': df['publication_date'], 'database': df['database'],
                        'title': df['title'], 'url': df['html_url'], 'abstract': df['abstract']}
                    )
                    papers_ieee['domain'] = domain
                    papers = papers.append(papers_ieee)
                if database == 'springer':
                    df = df.drop_duplicates(subset=['doi'])
                    dates = df['publicationDate']
                    df['publication_date'] = parse_dates(dates)
                    papers_springer = pd.DataFrame(
                        {'doi': df['doi'], 'type': df['contentType'],
                        'publication': df['publicationName'], 'publisher': df['publisher'],
                        'publication_date': df['publication_date'], 'database': df['database'],
                        'title': df['title'], 'url': df['url'], 'abstract': df['abstract']}
                    )
                    papers_springer['domain'] = domain
                    papers = papers.append(papers_springer)
                if database == 'arxiv':
                    df = df.drop_duplicates(subset=['id'])
                    dates = df['published']
                    df['publication_date'] = parse_dates(dates)
                    papers_arxiv = pd.DataFrame(
                        {'doi': df['id'], 'type': df['database'], 'publication': df['database'],
                        'publisher': df['database'], 'publication_date': df['publication_date'],
                        'database': df['database'], 'title': df['title'], 'url': df['id'],
                        'abstract': df['summary']}
                    )
                    papers_arxiv['domain'] = domain
                    papers = papers.append(papers_arxiv)
                if database == 'sciencedirect':
                    df = df.drop_duplicates(subset=['id'])
                    papers_sciencedirect = pd.DataFrame(
                        {'doi': df['id'], 'type': df['type'], 'publication': df['publication'],
                        'publisher': df['publisher'], 'publication_date': df['publication_date'],
                        'database': df['database'], 'title': df['title'], 'url': df['url'],
                        'abstract': df['abstract']}
                    )
                    papers_sciencedirect['domain'] = domain
                    papers = papers.append(papers_sciencedirect)
                if database == 'scopus':
                    df = df.drop_duplicates(subset=['id'])
                    papers_scopus = pd.DataFrame(
                        {'doi': df['id'], 'type': df['type'], 'publication': df['publication'],
                        'publisher': df['publisher'], 'publication_date': df['publication_date'],
                        'database': df['database'], 'title': df['title'], 'url': df['url'],
                        'abstract': df['abstract']}
                    )
                    papers_scopus['domain'] = domain
                    papers = papers.append(papers_scopus)
                if database == 'core':
                    df = df.drop_duplicates(subset=['id'])
                    dates = df['datePublished']
                    df['publication_date'] = parse_dates(dates)
                    df[id] = getIds(df)
                    papers_core = pd.DataFrame(
                        {'doi': df['id'], 'type': df['database'], 'publication': df['journals'],
                         'publisher': df['publisher'], 'publication_date': df['publication_date'],
                         'database': df['database'], 'title': df['title'], 'url': df['downloadUrl'],
                         'abstract': df['description']}
                    )
                    papers_core['domain'] = domain
                    papers = papers.append(papers_core)
    papers = papers.drop_duplicates(subset=['doi', 'title'])
    papers['type'] = 'preprocessed'
    papers['abstract'].replace('', np.nan, inplace=True)
    papers.dropna(subset=['abstract'], inplace=True)
    with open('./papers/preprocessed_papers.csv', 'a', newline='', encoding=fr) as f:
        papers.to_csv(f, encoding=fr, index=False, header=f.tell() == 0)


def getIds(df):
    ids = []
    for index, row in df.iterrows():
        if len(str(row['doi']).strip()) > 0:
            ids.append(str(row['doi']))
        else:
            ids.append(str(row['id']))
    return ids


def parse_dates(dates):
    new_dates = []
    for date in dates:
        date = str(date)
        if date == '1 Aug1, 2021':
            print('')
        if len(date) == 4:
            date = '01/Jan/' + date
        if re.match('[A-z]+-[A-z]+ [0-9]+', date):
            date = '01/' + date.split('-')[0] + '/' + date.split(' ')[1]
        if re.match('[A-z]+.-[A-z]+. [0-9]+', date):
            date = date.replace('.', '')
            date = '01/' + date.split('-')[0] + '/' + date.split(' ')[1]
        if re.match('[A-z]+. [0-9]+', date):
            if '.' in date:
                date = '01/' + date.split('.')[0] + '/' + date.split('.')[1].replace(' ', '')
            else:
                date = '01/' + date.split(' ')[0] + '/' + date.split(' ')[1].replace(' ', '')
        if re.match('[A-z]+-[0-9]+', date):
            date = '01/' + date.split('-')[0] + '/' + date.split('-')[1]
        if re.match('[0-9]+-[0-9]+ [A-z]+. [0-9]+', date):
            date = date.split('-')[1]
            date = date.split(' ')[0] + '/' + date.split(' ')[1].split('.')[0] + '/' + date.split(' ')[2]
        if re.match('[0-9]+-[0-9]+ [A-z]+ [0-9]+', date):
            date = date.split('-')[1]
            date = date.split(' ')[0] + '/' + date.split(' ')[1] + '/' + date.split(' ')[2]
        if re.match('[0-9]+ [A-z]+-[0-9]+ [A-z]+. [0-9]+', date):
            date = date.split('-')[1].split(' ')[0] + '/' + date.split('-')[1].split(' ')[1] + '/' + \
                   date.split('-')[1].split(' ')[2]
        if re.match('[0-9]+ [A-z]+.-[0-9]+ [A-z]+. [0-9]+', date):
            date = date.split('-')[1].split(' ')[0] + '/' + date.split('-')[1].split(' ')[1] + '/' + \
                   date.split('-')[1].split(' ')[2]
        if re.match('[0-9]+ [A-z]+-[A-z]+. [0-9]+', date):
            date = '01/' + date.split('-')[1].split(' ')[0] + '/' + date.split('-')[1].split(' ')[1]
        if re.match('[0-9]+ [A-z]+.-[A-z]+. [0-9]+', date):
            date = '01/' + date.split('-')[1].split(' ')[0] + '/' + date.split('-')[1].split(' ')[1]
        if re.match('[0-9]+ [A-z]+[0-9]+, [0-9]+', date):
            sub = date.split(' ')[1]
            sub = sub.replace(',', '')
            r = re.sub('[0-9]+', '', sub)
            date = date.split(' ')[0] + '/' + r + '/' + date.split(' ')[2]
        if re.match('[0-9] [A-z]+[0-9], [0-9]+', date):
            sub = date.split(' ')[1]
            sub = sub.replace(',', '')
            r = re.sub('[0-9]+', '', sub)
            date = date.split(' ')[0] + '/' + r + '/' + date.split(' ')[2]
        if re.match('[0-9]+ [A-z]+[0-9]+, [0-9]+', date):
            sub = date.split(' ')[1]
            sub = sub.replace(',', '')
            r = re.sub('[0-9]+', '', sub)
            date = date.split(' ')[0] + '/' + r + '/' + date.split(' ')[2]
        if 'Firstquarter' in date:
            date = '01/Mar/' + date.split(' ')[1]
        if 'Secondquarter' in date:
            if '/Secondquarter/' in date:
                date = date.replace('Secondquarter', 'Jun')
            else:
                date = '01/Jun/' + date.split(' ')[1]
        if 'Thirdquarter' in date:
            date = '01/Sep/' + date.split(' ')[1]
        if 'thirdquarter' in date:
            date = date.replace('thirdquarter', 'Sep')
        if 'Fourthquarter' in date:
            if '/Fourthquarter/' in date:
                date = date.replace('Fourthquarter', 'Dec')
            else:
                date = '01/Dec/' + date.split(' ')[1]
        date = date.replace('.', '')
        if date == 'First Quarter 2013':
            print('here')
        date = pd.to_datetime(date)
        new_dates.append(date)
    return new_dates


def filter_papers(keywords):
    preprocessed_papers = pd.read_csv('./papers/preprocessed_papers.csv')
    filtered_papers = filter_by_keywords(preprocessed_papers, keywords)
    filtered_papers['type'] = 'filtered'
    util.save('filtered_papers.csv', filtered_papers, fr)


def filter_by_field(papers, field, keywords):
    papers[field].replace('', np.nan, inplace=True)
    papers.dropna(subset=[field], inplace=True)
    filtered_papers = []
    for keyword in keywords:
        if len(filtered_papers) == 0:
            filtered_papers = papers[papers[field].str.contains(keyword)]
        else:
            filtered_papers = filtered_papers.append(papers[papers[field].str.contains(keyword)])
    if len(filtered_papers) > 0:
        filtered_papers = filtered_papers.drop_duplicates(subset=['doi'])
    return filtered_papers


def filter_by_keywords(papers, keywords):
    filtered_papers = []
    for keyword in keywords:
        for key, terms in keyword.items():
            boolean_series = papers['abstract'].str.find(key) != -1
            key_papers = papers[boolean_series]
            term_papers = []
            for term in terms:
                boolean_series = key_papers['abstract'].str.find(term) != -1
                if len(term_papers) == 0:
                    term_papers = key_papers[boolean_series]
                else:
                    term_papers = term_papers.append(key_papers[boolean_series])
            if len(filtered_papers) == 0:
                filtered_papers = term_papers
            else:
                filtered_papers = filtered_papers.append(term_papers)
        filtered_papers = filtered_papers.drop_duplicates(subset=['doi', 'title'])
    return filtered_papers
