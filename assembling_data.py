import os
import csv
import math
import json
from shapely import wkt
from timeit import default_timer as timer
import pandas as pd

# TODO: change data path
# DATA_PATH = '/Volumes/Untitled/DHH21/export_hackathon/1915/arbeiter_zeitung'
DATA_PATH = 'arbeiter_zeitung'
# header of Oleg's enriched csv file:  ,id,link,type,mention,start_idx,end_idx,stance,date,address,freq,geometry


def get_missing_info():
    dict_dict = {}
    for filename in os.listdir(DATA_PATH):
        with open(os.path.join(DATA_PATH, filename), 'r') as json_file:
            json_obj = json.load(json_file)
            for article in json_obj['articles']:
                if article['named_entities']:
                    for ne in article['named_entities']:
                        if ne['type'] == 'LOC':
                            dict_dict[ne['id']] = {'article_id': article['id'],
                                                   'fulltext': article['full_text'],
                                                   'issue_id': json_obj['issue']['id'],
                                                   'lang': json_obj['issue']['language']}
    return dict_dict


def get_coordinates(geometry):
    if geometry:
        geo_as_string = wkt.loads(geometry)
        lat = geo_as_string.centroid.y
        lon = geo_as_string.centroid.x
        return lat, lon


def get_context(fulltext, start_idx, end_idx):
    return fulltext[:int(start_idx)], fulltext[int(end_idx):]


def combine_csv_and_json(dict_dict):
    dict_list = []
    with open('data/arbeiter_zeitung_1915_enriched.csv', 'r', newline='', ) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            mention_dict = {
                'mention_id': row[1],
                'mention': row[4],
                'start_idx': row[5],
                'end_idx': row[6],
                # TODO: add right and left context text (solve problem with special characters)
#                 'left_context': 'left_context_placeholder',
                'left_context': get_context(dict_dict[row[1]]['fulltext'], row[5], row[6])[0],
#                 'right_context': 'right_context_placeholder',
                'right_context': get_context(dict_dict[row[1]]['fulltext'], row[5], row[6])[1],
                'article_id': dict_dict[row[1]]['article_id'],
                'issue_id': dict_dict[row[1]]['issue_id'],
                'date': row[8],
                'lang': dict_dict[row[1]]['lang'],
                'wikidata_link': row[2],
                'address': row[9],
                'lat': get_coordinates(row[11])[0] if get_coordinates(row[11]) else '',
                'lon': get_coordinates(row[11])[1] if get_coordinates(row[11]) else ''
            }
            dict_list.append(mention_dict)
    return dict_list


def write_csv(path, dict_list):
    with open(path, 'w', newline='') as assembled_csv:
        fieldnames = ['mention_id', 'mention', 'start_idx', 'end_idx', 'left_context', 'right_context',
                      'article_id', 'issue_id', 'date', 'lang', 'wikidata_link', 'address', 'lat', 'lon']
        writer = csv.DictWriter(assembled_csv, fieldnames=fieldnames)   # quotechar='§', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for diction in dict_list:
            writer.writerow(diction)


if __name__ == '__main__':
    print('running assembling_data.py...')
    start = timer()
    missing_info = get_missing_info()
    combined_data = combine_csv_and_json(missing_info)
    df = pd.DataFrame.from_dict(combined_data)
    savepath = 'data/pandas_az_1915.csv'
    df.to_csv(savepath)
#     write_csv('data/test_1915_az.csv', combine_csv_and_json(get_missing_info()))
    end = timer()
    print('time elapsed:', math.ceil((end - start) / 60), 'minutes')

