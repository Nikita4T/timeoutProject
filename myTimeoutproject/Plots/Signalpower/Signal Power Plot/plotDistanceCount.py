import re
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt
import os


#config

csvDir = os.getenv("CSV_DIR", "/home/veins/storage/Data/Signalpower/Signal Power Plot/signalpower")
resultDir = os.getenv("RESULT_DIR", "/home/veins/storage/Data/Signalpower/Signal Power Plot")

#/config

csvs = glob(os.path.join(csvDir, "*.csv")) #*NoGui_*.csv")	#all csvs in one

dfs = []
for csv in csvs:
    df = pd.read_csv(csv, sep=",") # read csv as dataframe
    dfs.append(df)

df = pd.concat(dfs) # concats combines the different appends into one dataframe
	
count_df = (
    df["distance_m"]
    .value_counts()
    .sort_index()
    .reset_index()
)	
	
import plotly.express as px

fig = px.bar(
    count_df,
    x="distance_m",
    y="count",
)

# fig.update_yaxes(tickformat=".0%")
fig.update_xaxes(ticksuffix="m")

os.makedirs(os.path.join(resultDir, "plots"), exist_ok=True)

fig.write_html(os.path.join(resultDir, "plots", "distanceCount.html"))

