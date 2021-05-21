import pickle
import wikipediaapi
# import wikipedia
from bs4 import BeautifulSoup
import lxml
import ssl
import urllib.request
import urllib.error
from geojson import Feature, FeatureCollection, Point, dump

# URL: https://en.wikipedia.org/wiki/List_of_military_engagements_of_World_War_I

# Ignore SSL certificate errors
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def pickle_obj(obj, path):
    """Pickles the given object and saves the pickle file at the given path."""
    with open(path, 'wb') as f:
        pickle.dump(obj, f)


def unpickle_obj(path):
    """Unpickles the object at the given path and returns it."""
    with open(path, 'rb') as pf:
        return pickle.load(pf)


def get_battle_links():
    wiki = wikipediaapi.Wikipedia('en')
    battles_page = wiki.page('List of military engagements of World War I')
    if battles_page.exists():
        print(f'"{battles_page.title}" page exists.\n')
    links_dict = {}
    for key, value in battles_page.links.items():
        try:
            if 'battle' in key.lower() or 'offensive' in key.lower():
                # print('key: ', key, '\nvalue: ', value.__dict__, '\n')
                links_dict[key] = value.fullurl
        except KeyError as e:
            print(f'Wikipedia page: {value}\nError: {e}\n')
            # raise e
    pickle_obj(links_dict, 'pickles/battle_links.pickle')
    return links_dict


def get_infobox(url):
    page_resp = urllib.request.urlopen(url, context=CTX)
    page_soup = BeautifulSoup(page_resp, 'lxml')
    return page_soup.find("table", {"class": "infobox"})


def get_battle_dates(infobox):
    battle_date = infobox.find("th", string="Date").next_sibling.text
    split_date = battle_date.split('–')
    return split_date
    # TODO: split date into start and end date and return in correct format (date data type for GeoJSON?)
    #  also see message from Axel


def get_battle_loc_name(infobox):
    loc_div_a = infobox.find("div", {"class": "location"}).a
    # TODO: fix KeyError: 'title'
    if loc_div_a is not None and loc_div_a['title']:
        return loc_div_a['title']


def get_battle_coordinates(infobox):
    battle_location_coordinates = infobox.find("div", {"class": "location"})
    # TODO: get coordinates in correct format


def create_geojson():
    for title, battle_link in unpickle_obj('pickles/battle_links.pickle').items():
        battle_title = title
        battle_infobox = get_infobox(battle_link)
        if battle_infobox:
            print(battle_title)
            print(get_battle_dates(battle_infobox))
            # battle_start_date = get_battle_dates(battle_infobox)
            # battle_end_date = get_battle_dates()[1]
            battle_location = get_battle_loc_name(battle_infobox)
            if battle_location is not None:
                print(battle_location)
            print('\n')
            # battle_coordinates = get_battle_coordinates(battle_infobox)
            # TODO: complete and save data in GeoJSON file


if __name__ == '__main__':
    print('\nRunning wikipedia_extraction.py...')
    # this is for testing:
    baranovichi_offensive = 'https://en.wikipedia.org/wiki/Baranovichi_offensive'
    create_geojson()
