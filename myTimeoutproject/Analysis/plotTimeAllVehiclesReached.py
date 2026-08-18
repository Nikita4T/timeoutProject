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
    vehiclesReachedPct = vehiclesReached / nodeCount
    newDf['timeNeeded'] = time
    
    dfs.append(newDf)

df = pd.concat(dfs) # concats combines the different appends into one dataframe
	
import plotly.express as px

df_allVehicles = df[df['vehiclesReached'].astype(int) == nodeCount]

fig = px.box(
    df_allVehicles,
    x="timeoutMax",
    y="timeNeeded",
#    points="all",
    labels={
    	"timeoutMax": "Maximaler Timeout [ms]",
        "timeNeeded": "Zeit [s]",
        "repetitions": "Wiederholungen"
    },
)

fig.update_traces(
	hoveron='boxes'
	)

os.makedirs(os.path.join(resultDir, "plots", "pdf"), exist_ok=True)
fig.write_html(os.path.join(resultDir, "plots", "TimeAllVehiclesReached.html"))
fig.write_image(os.path.join(resultDir, "plots", "pdf", "TimeAllVehiclesReached.pdf"))
