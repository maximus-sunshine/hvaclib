####################################################################################################################
# weather.py
#
# Streamlit app for visualizing weather data for HVAC applications



####################################################################################################################
# IMPORTS
import pandas as pd

from eatlib import * # import eatlib - the only library you'll ever need
# from pvlib.iotools import epw
import ladybug_pandas as lbp
from ladybug.epw import EPW

####################################################################################################################
# FUNCTIONS

def stringify_path(
    filepath_or_buffer: FilePathOrBuffer[AnyStr],
) -> FilePathOrBuffer[AnyStr]:
    """
    Attempt to convert a path-like object to a string.

    Parameters
    ----------
    filepath_or_buffer : object to be converted

    Returns
    -------
    str_filepath_or_buffer : maybe a string version of the object

    Notes
    -----
    Objects supporting the fspath protocol (python 3.6+) are coerced
    according to its __fspath__ method.

    For backwards compatibility with older pythons, pathlib.Path and
    py.path objects are specially coerced.

    Any other object is passed through unchanged, which includes bytes,
    strings, buffers, or anything else that's not even path-like.
    """
    if hasattr(filepath_or_buffer, "__fspath__"):
        # https://github.com/python/mypy/issues/1424
        return filepath_or_buffer.__fspath__()  # type: ignore
    elif isinstance(filepath_or_buffer, pathlib.Path):
        return str(filepath_or_buffer)
    return _expand_user(filepath_or_buffer)


#####################################################
#   read_epw(epw_file) - read a .epw weather file into a pandas dataframe
#
#   Imports:
#   from pvlib.iotools import epw
#   import pandas as pd
#   import datetime
#   import plotly.graph_objects as go
#
#
#   Inputs:
#
#   epw_file - a .epw weather file (https://energyplus.net/weather)
#
#
#   Outputs:
#
#   load_df - a dataframe representation of the .epw data with slightly modified columns.
#   metadata - the site metadata available in the .epw file
#
#
#   Notes:
#
#   -See (https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.iotools.read_epw.html#pvlib.iotools.read_epw)
#    for more information.
#   -Show interpolated data in a different color
#
#
#   TODO:
#
#   - make column names better
#
#
def read_epw(epw_path):
    # read in a .epw file using ladybug-pandas (https://github.com/ladybug-tools/ladybug-pandas)
    epw = EPW(epw_path)
    epw._import_data()
    df = lbp.DataFrame.from_epw(epw)
    df_ip = df.ladybug.to_ip()

    # drop unwanted columns, & reset the timestamp column
    df_ip.index.name='timestamp'
    # df_ip.reset_index(inplace=True)
    return df_ip
#####################################################


#####################################################
#   plot_epw(epw_df) - plot weather data from a dataframe constructed with read_epw()
#
#   Imports:
#
#   import pandas as pd
#   import plotly.graph_objects as go
#
#
#   Inputs:
#
#   epw_df - a dataframe constructed with read_epw()
#
#
#   Outputs:
#
#   fig - a Plotly figure
#
#
def plot_epw(epw_df):
    # use graph_objects to create the figure
    fig = go.Figure()

    # create traces for all columns vs. timestamps
    for i in range(epw_df.shape[1]):
        fig.add_trace(go.Scatter(x=epw_df.index, y=epw_df.iloc[:, i],
                                 visible='legendonly',
                                 mode='lines',
                                 name=epw_df.columns[i]))

    # layout configuration
    fig.update_layout(showlegend=True)  # force the legend for single-trace plots
    fig.update_layout(legend_title_text='Legend')
    fig.update_layout(hovermode='x')
    return fig



####################################################################################################################
# SCRIPT

# do some housekeeping and create some variables
st.set_page_config(layout="wide")
epw_file_path = './Weather Files/'
fig = go.Figure()

# use triple quotes instead of st.write() for multiline printing using Markdown syntax
# (https://www.markdownguide.org/cheat-sheet/)
"""`Welcome to the party! This is an experimental app. If you run 
into any bugs/errors or have suggestions for additional features/functionality, please use the "Report a bug with 
this app" tool in the drop down menu in the top right corner of this page. Thanks for playing!` 

# Weather Data Visualization App

Quickly visualize weather data to gain engineering insights and make nice-looking graphs to include in 
reports/presentations.

This app is compatible with weather data files saved in the [.epw](https://energyplus.net/weather/sources) EnergyPlus format.

To get started, upload a .epw file - or click "See example"."""

uploaded_file = st.file_uploader("Upload a .epw file", type='epw')

if st.button('See example'):
    # epw_df = read_epw(epw_path + random.choice(os.listdir(epw_path)))  # pick a random example file
    epw_df = read_epw('Weather Files/CZ06RV2.epw')
    fig = plot_epw(epw_df)

    """
    ### Raw Data (example):

    Uploaded file should be in .epw format

    Click "See example" again to see a different example.
    """

    # # this line displays the .csv file in table format, with the index column suppressed to avoid confusion
    # st.dataframe(epw_df.assign(drop_index='').set_index('drop_index'))
    # st.dataframe(epw_df)
    st.write(epw_df.astype('object'))

    """
    ### Point Trend Graph (example):

    Click on point names in the legend to make them visible.

    Pan and zoom with your mouse to get a closer look at the data. Double click inside the graph to reset the axes.

    You can download this graph as a .png by clicking the camera icon in the plot figure menu.
    """

    st.plotly_chart(fig, use_container_width=True)

if uploaded_file is not None:
    bytes = uploaded_file.read()
    epw_df = read_epw(bytes)

    fig = plot_epw(epw_df)

    """
    ### Raw Data:

    Uploaded file should be in .epw format

    Click "See example" again to see a different example, or upload a different file.
    """

    # # this line displays the .csv file in table format, with the index column suppressed to avoid confusion
    # st.dataframe(epw_df.assign(drop_index='').set_index('drop_index'))
    st.dataframe(epw_df)

    """
    ### Point Trend Graph:

    Click on point names in the legend to make them visible.

    Pan and zoom with your mouse to get a closer look at the data. Double click inside the graph to reset the axes.

    You can download this graph as a .png by clicking the camera icon in the plot figure menu.
    """

    st.plotly_chart(fig, use_container_width=True)


