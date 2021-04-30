####################################################################################################################
# load_profile.py
#
# testing plotting load profile stuff



####################################################################################################################
# IMPORTS
import numpy as np
import pandas as pd
from eatlib import * # import eatlib - the only library you'll ever need
import plotly.express as px
from plotly.subplots import make_subplots
import openpyxl

####################################################################################################################
# FUNCTIONS



####################################################################################################################
# SCRIPT

# define some variables for reading in data
file_path_in = 'Input Load Profiles/'
file_path_out = 'Output Plots/'
file_name = 'SDSU Heat Load Analysis Multiple Bldgs - Desktop.xlsx'
sheet_name = 'Nasatir'
data_range = 'A:E'
meta_data_range = 'G:H'

# read load data into dataframe and calculate the total load
load_df = pd.read_excel(
    file_path_in + file_name,
    sheet_name=sheet_name,
    usecols=data_range,
    engine='openpyxl'
)
total_load = load_df['Load (MBH)'].sum()
max_load = load_df['Load (MBH)'].max()

# read static inputs & metadata into dataframe
meta_df = pd.read_excel(
    file_path_in + file_name,
    sheet_name=sheet_name,
    header = 1,
    index_col=0,
    usecols=meta_data_range,
    engine='openpyxl'
)
meta_df.dropna(inplace=True)

# read design MBH from spreadsheet and calculate 5% load increment
mbh_design = meta_df.iloc[0,0]
mbh_increment = mbh_design/20

# read GSF from spreadsheet & calculate Btu/sf for design & actual
gsf = meta_df.iloc[0,0]
btu_sf_design = round(1000 * mbh_design / gsf,2)
btu_sf_actual = round(1000 * max_load / gsf,2)

# create bins and axes for plotting
# bins = [str(5*(x+1)) + '%' for x in range(20)]
percent_labels = list(np.zeros(20))
increment_labels = list(np.zeros(20))
labels = list(np.zeros(20))
for i in range(20):
    percent_labels[i] = str(5*(i+1)) + '%'
    increment_labels[i] = '(' + str(round(mbh_increment*i)) + '-' + str(round(mbh_increment*(i+1))) + ' MBH)'
    labels[i] = '<b>' + percent_labels[i] + '</b><br>' + increment_labels[i]

# create some variables
binned_loads = pd.Series(np.zeros(20))
cumulative_loads = pd.Series(np.zeros(20))
cumulative_percent = pd.Series(np.zeros(20))
c_load = 0

# populate variables
for i in range(21):
    binned_loads[i] = load_df[(load_df['Load (MBH)'] >= (i * mbh_increment)) & (load_df['Load (MBH)'] < ((i + 1) * mbh_increment))]['Load (MBH)'].sum()

    c_load += binned_loads[i]

    cumulative_loads[i] = c_load
    cumulative_percent[i] = 100 * cumulative_loads[i]/total_load

# create a figure with a secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# add the bar chart on the primary axis
fig.add_trace(
    go.Bar(
        x=labels,
        y=binned_loads,
        marker = dict(
            color = "#00C496",
        ),
        name = 'Heating output at part load',
        customdata=np.stack([percent_labels, increment_labels]).transpose(),
        hovertemplate=
        '<b>%{y:,} kBtus</b> <extra>@ %{customdata[0]} design capacity %{customdata[1]}</extra>'
    ),
    secondary_y=False
)

# add the cumulative percent line on the secondary axis
fig.add_trace(
    go.Scatter(
        x=labels,
        y=cumulative_percent,
        marker = dict(
            color = "#FB9A2D",
        ),
        name = "Cumulative heating output",
        hovertemplate=
        '<b>%{y:.2f}%</b> <extra>of total heating output</extra>'
    ),
    secondary_y=True
)

# add annotations
fig.add_annotation(
    text= "<b>Design MBH</b>: {:,}<br><b>Design Btu/sf</b>: {:,}<br><br><b>Max. actual MBH</b>: {:,}<br><b>Max. actual \
Btu/sf</b> = {:,}<br>".format(mbh_design,btu_sf_design,max_load,btu_sf_actual),
    align='left',
    showarrow=False,
    bordercolor='black',
    borderwidth= 2,
    xref='paper',
    yref='paper',
    x=0.75,
    y=0.5,
    bgcolor="white",
    borderpad = 10,
    font = dict(size = 18)
)

# configure plot layout
fig.update_xaxes(type='category')

# set axis titles
fig.update_xaxes(title_text='<b>Load as percentage of design capacity</b><br>(100% = ' + str(mbh_design) + ' MBH)')
fig.update_yaxes(
    title_text="<b>Heating output at part load</b><br> (kBtus)",
    color = "#00C496",
    secondary_y=False
)
fig.update_yaxes(
    title_text="<b>Cumulative heating output</b><br> (100% = {:,}".format(round(total_load)) + " kBtus)",
    color = "#FB9A2D",
    secondary_y=True
)

# Set custom axis labels
fig.update_yaxes(ticksuffix='%', secondary_y=True)

# Set figure title
fig.update_layout(title_text = '<b>' + sheet_name + ' Heat Load Distribution</b>')

# customize hover labels
# fig.update_layout(hovermode="x unified")
fig.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
    )
)

# open the figure in a web browser
fig.show()

# write the figure to a shareable .html file
fig.write_html(file_path_out + file_name + '_Plot.html')