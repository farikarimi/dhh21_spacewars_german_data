import pandas as pd
import streamlit as st
import geopandas
import plotly.graph_objs as go

gj_file = open('data/arbeiterzeitung_1915.geojson')
az_1915_places = geopandas.read_file(gj_file)
# az_1915_places.set_crs('EPSG:4326')
lat_lon_dict1 = {point.y: point.x for point in az_1915_places.geometry[:100].centroid if point is not None}
lat_lon_dict2 = {point.y: point.x for point in az_1915_places.geometry[101:200].centroid if point is not None}
lat_lon_df = pd.DataFrame(lat_lon_dict1.items(), columns=['lat', 'lon'])

st.set_page_config(layout='wide')
st.title('DHH21 Space Wars')
st.markdown('Prototype map: Named Entities from the **1915** issues of the **Arbeiter-Zeitung**')
st.sidebar.text('The textual information can be shown here.')
# st.map(lat_lon_df)

mapbox_token = 'mapbox token'

scatter_map = go.Scattermapbox(lat=list(lat_lon_dict1.keys()), lon=list(lat_lon_dict1.values()), below='False',
                               marker=dict(size=12, color='rgb(56, 44, 100)'))
scatter_map2 = go.Scattermapbox(lat=list(lat_lon_dict2.keys()), lon=list(lat_lon_dict2.values()), below='False',
                                marker=dict(size=12, color='rgb(56, 44, 100)'))
layout = go.Layout(width=1000, height=700,
                   mapbox=dict(center=dict(lat=49, lon=16), accesstoken=mapbox_token, zoom=3, style="stamen-terrain"))
layer_selector = st.multiselect('Layer Selection', [scatter_map, scatter_map2],
                                format_func=lambda x: 'first 100 places' if x == scatter_map else 'second 100 places')
fig = go.Figure(data=layer_selector, layout=layout)
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

