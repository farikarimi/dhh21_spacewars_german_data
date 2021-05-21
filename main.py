import json
import geocoder
from pandas import DataFrame

newspaper_dir = '/Volumes/Untitled/DHH21/export_hackathon/1915/arbeiter_zeitung'

# with open('/Volumes/Untitled/DHH21/export_hackathon/'
#           '1913/arbeiter_zeitung/arbeiter_zeitung_aze19130101.json', 'r') as json_file:
# with open('/Volumes/Untitled/DHH21/export_hackathon/'
#           '1915/arbeiter_zeitung/arbeiter_zeitung_aze19150102.json', 'r') as json_file:
# with open('/Volumes/Untitled/DHH21/export_hackathon/'
#           '1915/neue_freie_presse/neue_freie_presse_nfp19150330.json', 'r') as json_file:
with open('/Volumes/Untitled/DHH21/export_hackathon/'
          '1915/innsbrucker_nachrichten/innsbrucker_nachrichten_ibn19150331.json', 'r') as json_file:
# with open('/Volumes/Untitled/DHH21/export_hackathon/'
#           '1915/arbeiter_zeitung/arbeiter_zeitung_aze19150331.json', 'r') as json_file:
    json_dict = json.load(json_file)

loc_names = []
loc_links = {}

for ne in json_dict['issue']['named_entities']:
    if ne['type'] == 'LOC':
        if ne['link'] is not None:
            loc_links[ne['mention']] = ne['link']
            # print(ne['link'])
        loc_names.append(ne['mention'])
        print(ne['mention'])

print(loc_links, '\n\n')

frame = DataFrame(loc_names)
print(frame[0].value_counts())

# manually counting the occurrences of each name
loc_freq = {}

for name in loc_names:
    if name in loc_freq:
        loc_freq[name] += 1
    else:
        loc_freq[name] = 1

# print(sorted(loc_freq.items()))

print('\n', len(loc_names), ' location names found', sep='')
print(len(loc_links.values()), 'locations with Wikidata links')
print(len(loc_freq.keys()), 'unique location names')

