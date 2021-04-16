####################################################################################################################
# weather.py
#
# Streamlit app for visualizing weather data for HVAC applications



####################################################################################################################
# IMPORTS
import pandas as pd

from eatlib import * # import eatlib - the only library you'll ever need
from epw import epw


####################################################################################################################
# FUNCTIONS

# read .epw files into plottable dataframes
def read_epw(epw_file):
    # read in a .epw file using the epw library (https://github.com/building-energy/epw)
    weather = epw()
    weather.read(epw_file)

    # convert to a pandas dataframe, drop unwanted columns, & reset the timestamp column
    df=weather.dataframe
    df.drop(columns=['Year', 'Month', 'Day', 'Hour', 'Minute', 'Data Source and Uncertainty Flags'], inplace=True)
    timestamps = pd.date_range(start='1998-01-01 01:00:00', end='1999-01-01 00:00:00', freq='1H')
    df.insert(0,'Timestamp',timestamps)
    return df

# plot weather data from a dataframe constructed with read_epw()
def plot_epw(epw_df):
    # use graph_objects to create the figure
    fig = go.Figure()

    # create traces for all columns vs. timestamps
    for i in range(epw_df.shape[1] - 1):
        fig.add_trace(go.Scatter(x=epw_df['Timestamp'], y=epw_df.iloc[:, i + 1],
                                 visible='legendonly',
                                 mode='lines',
                                 name=epw_df.columns[i + 1]))

    # layout configuration
    fig.update_layout(showlegend=True)  # force the legend for single-trace plots
    fig.update_layout(legend_title_text='Legend')
    fig.update_layout(hovermode='x')
    return fig



####################################################################################################################
# SCRIPT

# do some housekeeping and create some variables
st.set_page_config(layout="wide")
weather_file_path = './Weather Files/'
epw_df=[]
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

uploaded_file = st.file_uploader("Upload a .epw file")

if st.button('See example'):
    epw_df = read_epw(weather_file_path + random.choice(os.listdir(weather_file_path)))  # pick a random example file
    fig = plot_epw(epw_df)

    """
    ### Raw Data (example):

    Uploaded file should be in .epw format

    Click "See example" again to see a different example.
    """

    # this line displays the .csv file in table format, with the index column suppressed to avoid confusion
    st.dataframe(epw_df.assign(drop_index='').set_index('drop_index'))

    """
    ### Point Trend Graph (example):

    Click on point names in the legend to make them visible.

    Pan and zoom with your mouse to get a closer look at the data. Double click inside the graph to reset the axes.

    You can download this graph as a .png by clicking the camera icon in the plot figure menu.
    """

    st.plotly_chart(fig, use_container_width=True)

if uploaded_file is not None:
    epw_df = read_epw(uploaded_file)

    fig = plot_epw(epw_df)

    """
    ### Raw Data:

    Uploaded file should be in .epw format

    Click "See example" again to see a different example, or upload a different file.
    """

    # this line displays the .csv file in table format, with the index column suppressed to avoid confusion
    st.dataframe(epw_df.assign(drop_index='').set_index('drop_index'))

    """
    ### Point Trend Graph:

    Click on point names in the legend to make them visible.

    Pan and zoom with your mouse to get a closer look at the data. Double click inside the graph to reset the axes.

    You can download this graph as a .png by clicking the camera icon in the plot figure menu.
    """

    st.plotly_chart(fig, use_container_width=True)


