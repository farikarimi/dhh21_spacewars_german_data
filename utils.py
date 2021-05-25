
def prepare_dataset(geodf):
    """

    """
    geodf = geodf.dropna()
    list_lat, list_long = [], []
    for point in geodf['geometry']:
        lat = point.centroid.y
        long = point.centroid.x
        list_lat.append(lat)
        list_long.append(long)
    #     print(point.centroid.y)
    geodf['lat'] = list_lat
    geodf['long'] = list_long
    return geodf
