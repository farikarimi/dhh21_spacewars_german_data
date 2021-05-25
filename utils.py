import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import re
from shapely import wkt

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
    geodf['lon'] = list_long
    return geodf

def open_file(filepath):
    """

    """
    if filepath.endswith('csv'):
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])

        geometry = []
        for x in df['geometry']:
            if isinstance(x, str):
                geometry.append(wkt.loads(x))
                # search_point = re.search(re_point, x)
                # # if search_point:
                # group = search_point.group(0).split()
                # x = float(group[0][1:])
                # y = float(group[1][:-1])
                # # print(x, y)
                # geometry.append(Point(x, y))
            # else:

            else:
                geometry.append(None)

        crs = {'init': 'epsg:2263'}  # http://www.spatialreference.org/ref/epsg/2263/
        geo_df = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)

        # geo_df.to_file(driver='ESRI Shapefile', filename='data.shp')
    else:
        geo_df = gpd.read_file(filepath)

    return geo_df