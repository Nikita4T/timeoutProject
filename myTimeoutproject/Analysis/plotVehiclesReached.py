# The data-processing workflow in this script was inspired by the
# "Exercise with Veins" tutorial by Lorenzo Ghiro:
# https://ans.unibs.it/docs/veins_exercise.html
#
# The analysis and visualization were adapted and extended for this project.
import re
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt
import os
import numpy as np

#config

totalRepetitions = int(os.getenv("TOTAL_REPETITIONS", 1000))
nodeCount = int(os.getenv("NODE_COUNT", 25)) # nodes without leader
sendingStartTime = float(os.getenv("SENDING_START_TIME", 2))
resultDir = os.getenv("RESULT_DIR", "/home/veins/storage")

#/config
csvs = glob(os.path.join(resultDir, "result", "*.csv")) # all csvs in one

dfs = []

for csv in csvs:
    fname = os.path.basename(csv)
    df = pd.read_csv(csv, sep='\t') # read csv as dataframe
    data = []	# as we only have single entries which are the same for all vehicle nodes we make a new clean dataframe
    data.append({"redundant": 0}) # an empty dataframe doesnt work so we fill it with one column of redundant data.
    newDf = pd.DataFrame(data)
    name = fname.replace(".csv","")	#csv have naming scheme. timeoutMax_repetition ex 0_50
    list = name.split("_", 1)
    timeoutMax = float(list[0])
    repetition = int(list[1])
    newDf['timeoutMax'] = timeoutMax	#adds additional "column timeoutMax with just every row being timeoutMax
    newDf['repetition'] = repetition
    time = df['packetReceivedAt'].max()		#time is time needed until last packet was received
    time = time - sendingStartTime # subtract sending start time
    vehiclesReached = df[~df['node'].str.contains(r'node\[0\]')]['packetsReceived'].sum()		#packetsReveived is either 1 or 0. Sender node also has a 1 so we have to skip it.
    newDf['vehiclesReached'] = vehiclesReached
    
    dfs.append(newDf)

df = pd.concat(dfs) # concats combines the different appends into one dataframe

# determine overlapping repetetions
df_repetitions = (
	df
	.groupby(['timeoutMax', 'vehiclesReached'])	#group the combinations that share the same timeoutMax and vehiclesReached
	.size()	#count these groups. For ex. 3 times 0.1s timeoutMax with 20 vehiclesReached. This are the repetitions
	.reset_index(name='repetitions')	#create a datasframe with the repetitions as a new column
	)
# mean of vehicles reached
df_mean = (
    df
    .groupby('timeoutMax')['vehiclesReached']
    .mean()
    .reset_index(name='vehiclesReachedMean')
)
df_repetitions = df_repetitions.merge(
    df_mean,
    on='timeoutMax',
    how='left'
)

df_repetitions['vehiclesReachedPct'] = df_repetitions['vehiclesReached'] / nodeCount
df_repetitions['repetitionsPct'] = df_repetitions['repetitions'] / totalRepetitions
df_repetitions['vehiclesReachedMeanPct'] = df_repetitions['vehiclesReachedMean'] / nodeCount
	
import plotly.express as px
fig = px.scatter(
	df_repetitions, 
	x='timeoutMax', 
	y='vehiclesReached',
	color='repetitions',
	size='repetitions',
    size_max=8,
	# hover_data={'vehiclesReachedPct': ':.1%', 'repetitionsPct': ':.1%'},
	hover_data= ['timeoutMax', 'vehiclesReached',  'vehiclesReachedPct', 'repetitions', 'repetitionsPct', 'vehiclesReachedMean', 'vehiclesReachedMeanPct'],
	labels={
    		"timeoutMax": "Maximaler Timeout [ms]",
        	"vehiclesReached": "Fahrzeugabdeckungsgrad",
        	"repetitions": "Wiederholungen"
	},
	color_continuous_scale='viridis'				#trendline="ols"
	)
# fig.update_yaxes(tickformat=".0%")
# fig.update_xaxes(ticksuffix="ms")
fig.update_traces(
    hovertemplate=
    "Maximaler Timeout: %{x}<br>" +
    "Fahrzeugabdeckungsgrad: %{y} --> %{customdata[0]:.1%}<br>" +
    "Wiederholungen: %{customdata[1]} --> %{customdata[2]:.1%}<br>" +
    "⌀Fahrzeugabdeckungsgrad: %{customdata[3]:.4} --> %{customdata[4]:.1%}"
)

fig.add_scatter(
    x=df_mean["timeoutMax"],
    y=df_mean["vehiclesReachedMean"],
    mode="markers",
    name="Mittelwert",
    hoverinfo="skip",
    marker=dict(symbol="line-ew", size=2, line=dict(width=1))
)
fig.update_layout(legend_y=-0.1)
os.makedirs(os.path.join(resultDir, "plots", "pdf"), exist_ok=True)

fig.write_html(os.path.join(resultDir, "plots", "VehiclesReached.html"))
fig.write_image(os.path.join(resultDir, "plots", "pdf", "VehiclesReached.pdf"))
