import pandas as pd
import streamlit as st
import geopandas as gpd
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
from shapely import wkt
import contextily as ctx

epsg = 4326

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

@st.cache(allow_output_mutation=True)
def open_file(filepath):
    """
    If filepath direct ot GeoJSON file, just opens and reads it
    If its a CSV file, opens it and converts it to GeoJSON. The CSV
    needs to have a least a geometry column with Point(x,y) as values
    """
    if filepath.endswith('csv'):
        df = pd.read_csv(filepath)
        for col in df.columns:
            if col.startswith('Unnamed'):
                del df[col]
        df['date'] = pd.to_datetime(df['date'])

        # geometry = []
        # for x in df['geometry']:
        #     if isinstance(x, str):
        #         geometry.append(wkt.loads(x))
        #     else:
        #         geometry.append(None)

        geometry = []
        for y, x in zip(df['lat'].values, df['lon'].values):
            geometry.append(f"{y} {x}")
            # if isinstance(y, str):
        df['geometry'] = geometry

        # 2263
        # crs = {'init': f'epsg:{epsg}'}  # http://www.spatialreference.org/ref/epsg/2263/
        # geo_df = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
        crs = {'init': f'epsg:{epsg}'}  # http://www.spatialreference.org/ref/epsg/2263/
        geo_df = gpd.GeoDataFrame(df, crs=crs)

    else:
        geo_df = gpd.read_file(filepath)
        geo_df.set_crs(epsg=epsg)

    return geo_df

@st.cache(allow_output_mutation=True)
def open_battle_file(filepath):
    """
    Specific function to open DataFrame containing battle related data
    """
    df = pd.read_csv(filepath)
    for col in df.columns:
        if col.startswith('Unnamed'):
            del df[col]
    df['displaydate'] = pd.to_datetime(df['displaydate'])
    df['displaystart'] = pd.to_datetime(df['displaystart'])
    df['displayend'] = pd.to_datetime(df['displayend'])

    df['coordinates'] = df['coordinates'].str.replace('\(\(', '(')
    df['coordinates'] = df['coordinates'].str.replace('\)\)', ')')

    ## "entity" in the URL is automatically converted to "wiki" when searching the URL in a browser
    ## like in the wikidata links from NewsEye
    ## I'll just change the URL so they can both match
    df['subject'] = df['subject'].str.replace('entity', 'wiki')
    df['location'] = df['location'].str.replace('entity', 'wiki')
    df['is_in_radius'] = False

    geometry = []
    for x in df['coordinates']:
        if isinstance(x, str):
            geometry.append(wkt.loads(x))
        else:
            geometry.append(None)
    # 2263
    crs = {'init': f'epsg:{epsg}'}  # http://www.spatialreference.org/ref/epsg/2263/
    geo_df = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
    del geo_df['coordinates']
    return geo_df

mapbox_token = '.mapbox_token'
px.set_mapbox_access_token(open(mapbox_token).read())
# gj_file = open('data/arbeiterzeitung_1915.geojson')


# az_1915_places = geopandas.read_file(gj_file)
# geo_df = open_file('data/arbeiter_zeitung_1915_enriched.csv')
geo_df = open_file('data/pandas_az_1915.csv')
battles = open_battle_file('data/WestFront.csv')
battles = prepare_dataset(battles)
print(battles)
## Preparing the data
# geo_df = prepare_dataset(geo_df)

# geoborders = open_file('data/borders_1914/b    text=locations_name,orders1914.json')



## Sidebar Layout
st.sidebar.title('DHH21 Space Wars')
st.sidebar.markdown('Prototype map: Named Entities from the **1915** issues of the **Arbeiter-Zeitung**')
# st.sidebar.text('The textual information can be shown here.')

lg_select = st.sidebar.multiselect('Choose a language:',
                                   geo_df['lang'].unique().tolist(),
                                    geo_df['lang'].unique().tolist()
                                   )

filtered_df = geo_df[geo_df['lang'].isin(lg_select)]

## TODO: Make sure that if we select fr, only the French newspapers appear, and vice-versa
newspapers_select = st.sidebar.selectbox('Choose a newspapers:',
                                         ['XXX', 'XXX']
                                         )


# ## TODO: Make sure that if we select fr, only the French newspapers appear, and vice-versa
# entity_select = st.sidebar.multiselect('Choose a location:',
#                                      geo_df['mention'].unique().tolist(),
#                                      geo_df['mention'].unique().tolist()
#                                      )


# entry_slider = st.sidebar.slider('Number of entities selected', 0, len(geo_df), 2000)
# filtered_df = geo_df.iloc[:entry_slider]

start_date = st.sidebar.date_input('Start date', geo_df['date'].iloc[0],
                           min_value = geo_df['date'].iloc[0],
                           max_value = geo_df['date'].iloc[-1])

end_date = st.sidebar.date_input('End date', geo_df['date'].iloc[-1],
                           min_value = geo_df['date'].iloc[0],
                           max_value = geo_df['date'].iloc[-1])

map_style = st.sidebar.selectbox('Choose a map style:',
                                 # these a free maps that do not require a mapbox token
                         ["open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain",
                          "stamen-toner", "stamen-watercolor", 'white-bg'])


filtered_df = filtered_df[
    (filtered_df['date'] >= np.datetime64(start_date))
    & (filtered_df['date'] <= np.datetime64(end_date))
]
# print(px.data.gapminder()['year'])
filtered_df['year'] = pd.DatetimeIndex(filtered_df['date']).year

## calculating frequency on the fly
## maps the value of the column geometry with their value counts
## then groups by geometry / data point
filtered_df['freq'] = filtered_df['geometry'].map(filtered_df['geometry'].value_counts())

freq_slider = st.sidebar.slider('Location frequencies',
                                0, int(filtered_df['freq'].max()),
                                (500, 1000)
                                )
# print(freq_slider)
filtered_df = filtered_df[
    (filtered_df['freq'] >= freq_slider[0])
    & (filtered_df['freq'] <= freq_slider[1])
]
# start_freq_slider, end_freq_slider = st.sidebar.select_slider('Frequency range',
#                                                               filtered_df['freq'].unique().tolist(),
#                                                               )

## THIS IS DUMMY DATA TO TEST ANIMATION YEAR OPTION
# filtered_df.loc[300: 500 , 'year'] = 1916
# filtered_df.loc[501: 800 , 'year'] = 1917
# filtered_df.loc[801:  , 'year'] = 1918
## for some reason, the value for animation frame must be str...
filtered_df['year'] = filtered_df['year'].astype(str)
# filtered_df.to_csv('filtered.csv')

groupby_data = filtered_df.groupby('geometry')
map_df = groupby_data.first()

# map_df.to_csv('test.csv')

##  Plotting
fig = px.scatter_mapbox(map_df, lat='lat', lon='lon', #data and col. to use for plotting
                        hover_name = 'mention',
                        hover_data = ['freq', 'wikidata_link'],
                        # hover_data = ['mention'],
                        # labels = 'mention',
                        size = 'freq', # sets the size of each points on the values in the frequencies col.
                        # title = ''
                        animation_frame = 'year',
                        mapbox_style = map_style, # mapstyle used
                        center = dict(lat=49, lon=16), #centers the map on specific coordinates
                        zoom = 4, # zooms on these coordinates
                        width=1000, height=700, # width and height of the plot
                        )


fig.add_trace(go.Scattermapbox(
        lat=battles['lat'],
        lon=battles['lon'],
        mode='markers',
        # marker=go.scattermapbox.Marker(
        #     size=17,
        #     color='rgb(255, 0, 0)',
        #     opacity=0.7
        # ),
        # text=locations_name,
        # hoverinfo='text'
    ))# if we want to use other map style that are not provided by Mapbox or Plotly,
# we need to specify the path ourselves. It has to be done by updating the layout apparently
# https://holypython.com/how-to-create-map-charts-in-python-w-plotly-mapbox/
# fig.update_layout(
#     mapbox_style = map_style,
#     mapbox_layers=[
#         {
#             "below": 'traces',
#             "sourcetype": "raster",
#             "source": [
#                 # "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
#                 "https://tile.opentopomap.org/{z}/{x}/{y}.png"
#                 # "http://tile.stamen.com/terrain/{z}/{y}/{x}.png"
#             ]
#         }
#       ])

col1,col2 = st.beta_columns(2)

st.plotly_chart(fig)

page_slider = st.slider(
    'Select entities mention',
    0, len(geo_df), 50
)
# ,mention_id,mention,start_idx,end_idx,,,article_id,issue_id,date,lang,wikidata_link,address,lat,lon
df_page = filtered_df.iloc[page_slider:page_slider + 50]
st.write(df_page[['article_id', 'wikidata_link','date', 'left_context', 'mention', 'right_context']])
# #
# print(geoborders)
#
# fig2 = px.scatter_geo(
#     filtered_df, lat='lat', lon='lon',
#     # geojson = geoborders.geometry,
#     # featureidkey = "AREA",
#     animation_frame = 'year',
#     projection='natural earth',
#     # projection = 'mercator',
#     width=1000, height=700,  # width and height of the plot
#
# )
# fig2.update_geos(fitbounds="locations", visible=True)
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

