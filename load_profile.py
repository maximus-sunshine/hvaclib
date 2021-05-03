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
file_name = 'SDSU Heat Load Analysis Multiple Bldgs.xlsx'
sheet_name = 'EISC'
data_range = 'A:I'
meta_data_range = 'K:L'

# read load data into dataframe and calculate the total load
load_df = pd.read_excel(
    file_path_in + file_name,
    sheet_name=sheet_name,
    usecols=data_range,
    engine='openpyxl'
)
start = load_df['Timestamp'].iloc[0]
end = load_df['Timestamp'].iloc[-1]
td_in_hrs = round((load_df['Timestamp'].iloc[1] - load_df['Timestamp'].iloc[0]).seconds/3600,2)
total_hrs = len(load_df)*td_in_hrs
total_op_hrs = len(load_df['Heating Load (MBH)'][load_df['Heating Load (MBH)'] > 0])*td_in_hrs
total_load = load_df['Heating Load (MBH)'].sum()
max_load = round(load_df['Heating Load (MBH)'].max(),2)
neg_loads = load_df['Heating Load (MBH)'][load_df['Heating Load (MBH)'] < 0]

# read static inputs & metadata into dataframe
meta_df = pd.read_excel(
    file_path_in + file_name,
    sheet_name=sheet_name,
    index_col=0,
    usecols=meta_data_range,
    engine='openpyxl'
)
meta_df.dropna(inplace=True)

# read design MBH from spreadsheet and calculate 5% load increment
mbh_design = round(meta_df.iloc[0,0],2)
mbh_increment = mbh_design/20

# read GSF from spreadsheet & calculate Btu/sf for design & actual
gsf = meta_df.iloc[1,0]
btu_sf_design = round(1000 * mbh_design / gsf,2)
btu_sf_actual = round(1000 * max_load / gsf,2)

# create bins and axes for plotting
# bins = [str(5*(x+1)) + '%' for x in range(20)]
decimal_labels = list(np.zeros(20))
increment_labels = list(np.zeros(20))
labels = list(np.zeros(20))
for i in range(20):
    decimal_labels[i] = str(5*(i+1)/100) + 'x'
    increment_labels[i] = '(' + str(round(mbh_increment*i)) + '-' + str(round(mbh_increment*(i+1))) + ' MBH)'
    # labels[i] = '<b>' + percent_labels[i] + '</b><br>' + increment_labels[i]
    labels[i] = '<b>' + decimal_labels[i] + '</b><br>' + increment_labels[i]

# create some variables
binned_loads = [0] * 20
cumulative_loads = [0] * 20
cumulative_percent = [0] * 20
c_load = 0
cumulative_hours = [0] * 20
c_hours = 0
# bins and variables for hours histogram
# counts, bin_edges = np.histogram(load_df['Heating Load (MBH)'][load_df['Heating Load (MBH)'] > 0], bins=20, range=(0,mbh_design))
counts = [0] * 20

# populate variables
for i in range(20):
    binned_loads[i] = load_df['Heating Load (MBH)'][(load_df['Heating Load (MBH)'] > (i * mbh_increment)) & (load_df['Heating Load (MBH)'] <= ((i + 1) * mbh_increment))].sum()
    counts[i] = load_df['Heating Load (MBH)'][(load_df['Heating Load (MBH)'] > (i * mbh_increment)) & (load_df['Heating Load (MBH)'] <= ((i + 1) * mbh_increment))].count()

    c_load += binned_loads[i]
    c_hours += counts[i] * td_in_hrs

    cumulative_loads[i] = c_load
    cumulative_percent[i] = 100 * cumulative_loads[i]/total_load

    cumulative_hours[i] = c_hours

# create a figure with a secondary y-axis
fig = make_subplots(
    rows = 2,
    cols = 1,
    vertical_spacing=0.05,
    specs=[[{"secondary_y": True}],[{"secondary_y": True}]]
)

# Set figure title
title = '<b>Heating Load Distribution</b> from {} to {}'.format(start.strftime('%B %-d, %Y'),end.strftime('%B %-d, %Y'))
for i in range(len(meta_df)-2):
    title += '<br>' + meta_df.index[i+2] + ': ' + str(meta_df.iloc[i+2,0])
fig.update_layout(
    autosize=True,
    title = dict(
        text = title,
        xanchor = 'left',
        yanchor = 'top',
        y = 0.95,
        font = dict(color='black')
    )
)

# row 1
# add the hours bar chart on the primary axis
fig.add_trace(
    go.Bar(
        x=labels,
        y=[x/sum(counts)*100 for x in counts],
        marker=dict(
            color = "#3B6D89"
        ),
        customdata=np.stack([decimal_labels, increment_labels]).transpose(),
        hovertemplate='<b>%{y:.2f}% of total operating hours</b> <extra>@ %{customdata[0]} design capacity</extra>'
    ),
    secondary_y=False,
    row = 1,
    col = 1
)

# add the cumulative percent line on the secondary axis
fig.add_trace(
    go.Scatter(
        x=labels,
        y=[x/total_op_hrs*100 for x in cumulative_hours],
        mode='lines+markers',
        marker = dict(
            color = "#FB9A2D",
        ),
        customdata=np.stack([decimal_labels, increment_labels]).transpose(),
        hovertemplate=
        '<b>%{y:.2f}% of total operating hours</b> <extra>@ ≤%{customdata[0]} design capacity</extra>'
    ),
    secondary_y=True,
    row=1,
    col=1
)

# row 2
# add the load bar chart on the primary axis
fig.add_trace(
    go.Bar(
        x=labels,
        y=[round(x/total_load*100,2) for x in binned_loads],
        marker = dict(
            color = "#00C496",
        ),
        customdata=np.stack([decimal_labels, increment_labels]).transpose(),
        hovertemplate=
        '<b>%{y:,}% of total heating output</b> <extra>@ %{customdata[0]} design capacity</extra>'
    ),
    secondary_y=False,
    row=2,
    col=1,
)
fig.update_yaxes(
    ticksuffix='%'
)

# add the cumulative percent line on the secondary axis
fig.add_trace(
    go.Scatter(
        x=labels,
        y=cumulative_percent,
        mode='lines+markers',
        marker = dict(
            color = "#FB9A2D",
        ),
        customdata=np.stack([decimal_labels, increment_labels]).transpose(),
        hovertemplate=
        '<b>%{y:.2f}% of total heating output</b> <extra>@ ≤%{customdata[0]} design capacity</extra>'
    ),
    secondary_y=True,
    row=2,
    col=1
)

# add annotations
fig.add_annotation(
    text= "<b>Design MBH</b>: {:,}<br><b>Design Btu/sf</b>: {:,}<br><br><b>Max. actual MBH</b>: {:,}<br><b>Max. actual \
Btu/sf</b>: {:,}<br>".format(mbh_design,btu_sf_design,max_load,btu_sf_actual),
    align='left',
    showarrow=False,
    bordercolor='black',
    borderwidth= 2,
    xref='paper',
    yref='paper',
    xanchor = 'right',
    yanchor = 'bottom',
    x=0.94,
    y=1.05,
    bgcolor="white",
    borderpad = 10,
    font = dict(size = 14, color='black')
)
# throw a warning if input data contains negative loads
if len(neg_loads) > 0:
    fig.add_annotation(
        text="<b>WARNING</b>:<br>Input file contains negative load data-<br> # of negative data points: {} of {}<br> \
total negative kBtus: {}".format(len(neg_loads),len(load_df),round(sum(neg_loads)*td_in_hrs,2)),
        align='left',
        showarrow=False,
        bordercolor='red',
        borderwidth=2,
        xref='paper',
        yref='paper',
        xanchor='right',
        yanchor='bottom',
        x=0.7,
        y=1.05,
        bgcolor="white",
        borderpad=10,
        font=dict(size=14, color='red')
    )
    # counts.insert(0, len(neg_loads))
    # binned_loads.insert(0, load_df['Heating Load (MBH)'][(load_df['Heating Load (MBH)'] < 0)].sum())
    # cumulative_loads.insert(0, 0)
    # cumulative_percent.insert(0, 0)
    # cumulative_hours.insert(0, 0)
    # labels.insert(0,'<b>!!!</b><br>Negative Load<br>(check inputs)')
    # decimal_labels.insert(0, 'negative')
    # increment_labels.insert(0, 'negative')

# configure plot layout
fig.update_xaxes(type='category')

# set row 1 axis titles
fig.update_xaxes(
    title_text='',
    showticklabels=False,
    showline=True,
    linewidth=2,
    linecolor='black',
    mirror=True,
    row=1
)
fig.update_yaxes(
    title_text="<b>Operating hours</b>",
    color = "#3B6D89",
    showline=True,
    linewidth=2,
    linecolor='black',
    secondary_y=False,
    nticks=4,
    row=1
)
fig.update_yaxes(
    title_text="<b>Cumulative</b><br>(100% = {:,}".format(int(sum(counts)*td_in_hrs)) + " hours)",
    color = "#FB9A2D",
    showline=True,
    linewidth=2,
    linecolor='black',
    secondary_y=True,
    showgrid=False,
    range=[0,105],
    nticks=2,
    row=1
)

# set row 2 axis titles
fig.update_xaxes(
    title_text='<b>Part load operating point</b><br>(1.0x = design capacity, ' + str(mbh_design) + ' MBH)',
    showline=True,
    linewidth=2,
    linecolor='black',
    mirror=True,
    row=2
)
fig.update_yaxes(
    title_text="<b>Heating output</b>",
    color = "#00C496",
    showline=True,
    linewidth=2,
    linecolor='black',
    secondary_y=False,
    nticks=4,
    row=2
)
fig.update_yaxes(
    title_text="<b>Cumulative</b><br>(100% = {:,}".format(round(total_load)) + " kBtus)",
    color = "#FB9A2D",
    showline=True,
    linewidth=2,
    linecolor='black',
    showgrid = False,
    secondary_y=True,
    range=[0, 105],
    nticks=2,
    row=2
)

# customize hover labels
# fig.update_layout(hovermode="x unified")
fig.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
    )
)

# set margins
fig.update_layout(
    margin = dict(
        l = 50,
        r = 50,
        t = 175,
        b = 50
    )
)

#set legend
fig.update_layout(
    legend = dict(
        xanchor = 'right',
        yanchor = 'top',
        x = 0.9,
        y = 0.35
    ),
    showlegend=False
)

# open the figure in a web browser
fig.show()

# write the figure to a shareable .html file
fig.write_html(file_path_out + file_name + '_Plot.html')