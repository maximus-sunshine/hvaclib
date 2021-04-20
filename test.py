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
#   df - a dataframe representation of the .epw data with slightly modified columns.
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
def read_epw(epw_file):
    # read in a .epw file using ladybug-pandas (https://github.com/ladybug-tools/ladybug-pandas)
    epw = EPW(epw_path)
    epw._import_data()
    df = lbp.DataFrame.from_epw(epw)
    df_ip = df.ladybug.to_ip()

    # drop unwanted columns, & reset the timestamp column
    df_ip.index.name='timestamp'
    df_ip.reset_index(inplace=True)
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
    for i in range(epw_df.shape[1] - 1):
        fig.add_trace(go.Scatter(x=epw_df.index, y=epw_df.iloc[:, i+1],
                                 visible='legendonly',
                                 mode='lines',
                                 name=epw_df.columns[i+1]))

    # layout configuration
    fig.update_layout(showlegend=True)  # force the legend for single-trace plots
    fig.update_layout(legend_title_text='Legend')
    fig.update_layout(hovermode='x')
    return fig



####################################################################################################################
# SCRIPT

# do some housekeeping and create some variables
epw_path = './Weather Files/USA_CA_San.Diego-Lindbergh.Field.722900_TMY3.epw'
epw_df = read_epw(epw_path)

fig = plot_epw(epw_df)
fig.show()


