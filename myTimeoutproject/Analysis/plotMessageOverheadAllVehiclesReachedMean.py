import re
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt
import os


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
    data.append({"timeoutMax": timeoutMax, "repetition": repetition})	#adds additional "column timeoutMax, repetition
    time = df['packetReceivedAt'].max()		#time is time needed until last packet was received
    time = time - sendingStartTime # subtract sending start time
    vehiclesReached = df[~df['node'].str.contains(r'node\[0\]')]['packetsReceived'].sum()		#packetsReveived is either 1 or 0. Sender node also has a 1 so we have to skip it.
    newDf['vehiclesReached'] = vehiclesReached
    vehiclesReachedPct = vehiclesReached / nodeCount
    newDf['performance'] = vehiclesReached / time
    newDf['messageOverhead'] = (df['hopCount'] != 0).sum()+1 #hopcount from sender vehicle is 0 so +1
    
    dfs.append(newDf)

df = pd.concat(dfs) # concats combines the different appends into one dataframe

df = df[df['vehiclesReached'].astype(int) == nodeCount]

#determine overlapping repetetions
df_repetitions = (
	df
	.groupby(['timeoutMax', 'messageOverhead'])	#group the combinations that share the same timeoutMax and messageOverhead
	.size()	#count these groups. For ex. 3 times 0.1s timeoutMax with 20 vehiclesReached. This are the repetitions
	.reset_index(name='repetitions')	#create a datasframe with the repetitions as a new column
	)
# mean of message overhead
df_mean = (
    df
    .groupby('timeoutMax')['messageOverhead']
    .mean()
    .reset_index(name='messageOverheadMean')
)

df_mean['messageOverheadMeanPct'] = df_mean['messageOverheadMean'] / (nodeCount+1)

import plotly.express as px

fig = px.bar(
    df_mean,
    x="timeoutMax",
    y="messageOverheadMeanPct",
    hover_data={
    	"messageOverheadMeanPct": ":.2%"
    },
    labels={
    	"timeoutMax": "Maximaler Timeout [ms]",
        "messageOverheadMeanPct": "Nachrichtenaufwand"
    }
)

fig.update_yaxes(tickformat=".0%")

os.makedirs(os.path.join(resultDir, "plots", "pdf"), exist_ok=True)
fig.write_html(os.path.join(resultDir, "plots", "MessageOverheadAllVehiclesReachedMean.html"))
fig.write_image(os.path.join(resultDir, "plots", "pdf",
                                 "MessageOverheadAllVehiclesReachedMean.pdf"))    
