import pandas as pd
import streamlit as st
import geopandas as gpd
# import plotly.graph_objs as go
import plotly.express as px
import numpy as np
from shapely import wkt
import contextily as ctx

@st.cache
def prepare_dataset(geodf):
    """
    Adds a lat and a lon column to the GeoDF to be used
    with the mapping
    """
    geodf = geodf.dropna()
    list_lat, list_long = [], []
    for point in geodf['geometry']:
        lat = point.centroid.y
        long = point.centroid.x
        list_lat.append(lat)
        list_long.append(long)
    geodf['lat'] = list_lat
    geodf['lon'] = list_long
    return geodf

@st.cache
def open_file(filepath):
    """
    If filepath direct ot GeoJSON file, just opens and reads it
    If its a CSV file, opens it and converts it to GeoJSON. The CSV
    needs to have a least a geometry column with Point(x,y) as values
    """
    if filepath.endswith('csv'):
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])

        geometry = []
        for x in df['geometry']:
            if isinstance(x, str):
                geometry.append(wkt.loads(x))
            else:
                geometry.append(None)
# 2263
        crs = {'init': 'epsg:3857'}  # http://www.spatialreference.org/ref/epsg/2263/
        geo_df = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)

    else:
        geo_df = gpd.read_file(filepath)

    return geo_df

mapbox_token = '.mapbox_token'
px.set_mapbox_access_token(open(mapbox_token).read())
# gj_file = open('data/arbeiterzeitung_1915.geojson')


# az_1915_places = geopandas.read_file(gj_file)
geo_df = open_file('data/arbeiter_zeitung_1915_enriched.csv')

## Preparing the data
geo_df = prepare_dataset(geo_df)

## Sidebar Layout
st.sidebar.title('DHH21 Space Wars')
st.sidebar.markdown('Prototype map: Named Entities from the **1915** issues of the **Arbeiter-Zeitung**')
# st.sidebar.text('The textual information can be shown here.')


entry_slider = st.sidebar.slider('Number of entities selected', 0, len(geo_df), 2000)
filtered_df = geo_df.iloc[:entry_slider]

start_date = st.sidebar.date_input('Start date', geo_df['date'].iloc[0],
                           min_value = geo_df['date'].iloc[0],
                           max_value = geo_df['date'].iloc[-1])

end_date = st.sidebar.date_input('End date', geo_df['date'].iloc[-1],
                           min_value = geo_df['date'].iloc[0],
                           max_value = geo_df['date'].iloc[-1])

map_style = st.sidebar.selectbox('Choose a map style:',
                                 # these a free maps that do not require a mapbox token
                         ["open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner", "stamen-watercolor", 'white-bg'])

filtered_df = filtered_df[
    (filtered_df['date'] >= np.datetime64(start_date))
    & (filtered_df['date'] <= np.datetime64(end_date))
]
# print(px.data.gapminder()['year'])
filtered_df['year'] = pd.DatetimeIndex(filtered_df['date']).year

## THIS IS DUMMY DATA TO TEST ANIMATION YEAR OPTION
filtered_df.loc[300: 500 , 'year'] = 1916
filtered_df.loc[501: 800 , 'year'] = 1917
filtered_df.loc[801:  , 'year'] = 1918
## for some reason, the value for animation frame must be str...
filtered_df['year'] = filtered_df['year'].astype(str)

# print(filtered_df['year'])
##  Plotting
fig = px.scatter_mapbox(filtered_df, lat='lat', lon='lon', #data and col. to use for plotting
                        hover_name = 'mention',
                        hover_data = ['freq', 'type', 'link'],
                        # hover_data = ['mention'],
                        # labels = 'mention',
                        size = 'freq', # sets the size of each points on the values in the frequencies col.
                        # title = ''
                        animation_frame = 'year',
                        # mapbox_style = map_style, # mapstyle used
                        center = dict(lat=49, lon=16), #centers the map on specific coordinates
                        zoom = 3, # zooms on these coordinates
                        width=1000, height=700, # width and height of the plot
                        )
# if we want to use other map style that are not provided by Mapbox or Plotly,
# we need to specify the path ourselves. It has to be done by updating the layout apparently
# https://holypython.com/how-to-create-map-charts-in-python-w-plotly-mapbox/
fig.update_layout(
    mapbox_style = map_style,
    mapbox_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "source": [
                # "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                "https://tile.opentopomap.org/{z}/{x}/{y}.png"
                # "http://tile.stamen.com/terrain/{z}/{y}/{x}.png"
            ]
        }
      ])

st.plotly_chart(fig)

st.write(filtered_df)
# #
# fig2 = px.scatter_geo(
#     filtered_df, lat='lat', lon='lon',
#     animation_frame = 'year', projection='natural earth'
# )
# st.plotly_chart(fig2)

# further useful methods:
# st.header(body, anchor=None)
# st.subheader(body, anchor=None)
# st.text(body)
# st.markdown(body, unsafe_allow_html=False)
# st.code(body, language='python')
# st.write()
# st.dataframe(data=None, width=None, height=None) --> interactive
# st.table(data=None) --> static
# str.image(image, caption=None, width=None, use_column_width=None, clamp=False, channels='RGB', output_format='auto')
# https://docs.streamlit.io/en/stable/api.html#streamlit.pydeck_chart
# https://docs.streamlit.io/en/stable/api.html#display-interactive-widgets
# https://docs.streamlit.io/en/stable/api.html#streamlit.map

