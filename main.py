import json

# with open('/Volumes/Untitled/DHH21/export_hackathon/'
#           '1913/arbeiter_zeitung/arbeiter_zeitung_aze19130101.json', 'r') as json_file:
with open('/Volumes/Untitled/DHH21/export_hackathon/'
          '1915/arbeiter_zeitung/arbeiter_zeitung_aze19150102.json', 'r') as json_file:
    json_dict = json.load(json_file)

loc_names = []

for issue in json_dict['issue']:
    for ne in json_dict['issue']['named_entities']:
        if ne['type'] == 'LOC':
            loc_names.append(ne['mention'])
            print(ne['mention'])

print('\n', len(loc_names), ' location names found\n', sep='')

loc_freq = {}

for name in loc_names:
    if name in loc_freq:
        loc_freq[name] += 1
    else:
        loc_freq[name] = 1

print(sorted(loc_freq.items()))

# LOC: location
# PER: person
# ORG: organization
