import re
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt
import os


#config

csvDir = os.getenv("CSV_DIR", "/home/veins/storage/signalpower")
resultDir = os.getenv("RESULT_DIR", "/home/veins/storage")

#/config

csvs = glob(os.path.join(csvDir, "*.csv")) #*NoGui_*.csv")	#all csvs in one

dfs = []
for csv in csvs:
    df = pd.read_csv(csv, sep=",") # read csv as dataframe
    dfs.append(df)

df = pd.concat(dfs) # concats combines the different appends into one dataframe
	
import plotly.express as px

fig = px.box(
    df,
    x="distance_m",
    y="recvPower_dBm",
    points="all"
)
fig.update_traces(
	hoveron='boxes'
	)

# fig.update_yaxes(tickformat=".0%")
fig.update_xaxes(ticksuffix="m")

os.makedirs(os.path.join(resultDir, "plots"), exist_ok=True)

fig.write_html(os.path.join(resultDir, "plots", "distancetoRecvPower.html"))

