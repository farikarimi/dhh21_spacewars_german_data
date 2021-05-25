import pandas as pd
import streamlit as st
import geopandas as gpd
# import plotly.graph_objs as go
import plotly.express as px
import numpy as np
from utils import prepare_dataset, open_file

mapbox_token = '.mapbox_token'
px.set_mapbox_access_token(open(mapbox_token).read())
# gj_file = open('data/arbeiterzeitung_1915.geojson')
# with open('data/arbeiter_zeitung_1915_enriched.csv') as f:

# gj_file =
# az_1915_places = geopandas.read_file(gj_file)
# az_1915_places = gpd.read_file('data/arbeiter_zeitung_1915_enriched.csv')
# az_1915_places = pd.read_csv('data/arbeiter_zeitung_1915_enriched.csv')
geo_df = open_file('data/arbeiter_zeitung_1915_enriched.csv')
## Preparing the data
geo_df = prepare_dataset(geo_df)

## Sidebar Layout
st.sidebar.title('DHH21 Space Wars')
st.sidebar.markdown('Prototype map: Named Entities from the **1915** issues of the **Arbeiter-Zeitung**')
# st.sidebar.text('The textual information can be shown here.')



entry_slider = st.sidebar.slider('Number of entities selected', 100, len(geo_df))
filtered_df = geo_df.iloc[:entry_slider]

start_date = st.sidebar.date_input('Start date', geo_df['date'].iloc[0],
                           min_value = geo_df['date'].iloc[0],
                           max_value = geo_df['date'].iloc[-1])

end_date = st.sidebar.date_input('End date', geo_df['date'].iloc[-1],
                           min_value = geo_df['date'].iloc[0],
                           max_value = geo_df['date'].iloc[-1])

filtered_df = filtered_df[
    (filtered_df['date'] >= np.datetime64(start_date))
    & (filtered_df['date'] <= np.datetime64(end_date))
]
# print(len(fi))


##  Plotting
fig = px.scatter_mapbox(filtered_df, lat='lat', lon='lon', #data and col. to use for plotting
                        # hover_data = ['mention'],
                        labels = 'mention',
                        size = 'freq', # sets the size of each points on the values in the frequencies col.
                        # title = ''
                        mapbox_style = 'carto-positron', # mapstyle used
                        center = dict(lat=49, lon=16), #centers the map on specific coordinates
                        zoom = 3, # zooms on these coordinates
                        width=1000, height=700, # width and height of the plot
                        )

st.plotly_chart(fig)


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

