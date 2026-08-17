import re
import pandas as pd
from glob import glob
import matplotlib.pyplot as plt
import os


#config

csvDir = os.getenv("CSV_DIR", "M:/Documents/Bachelorarbeit/Analysis/Data/Signalpower/Signal Power Plot/signalpower")
resultDir = os.getenv("RESULT_DIR", "M:/Documents/Bachelorarbeit/Analysis/Data/Signalpower/Signal Power Plot")

#/config

csvs = glob(os.path.join(csvDir, "*.csv")) #*NoGui_*.csv")	#all csvs in one

dfs = []
for csv in csvs:
    df = pd.read_csv(csv, sep=",") # read csv as dataframe
    dfs.append(df)

df = pd.concat(dfs) # concats combines the different appends into one dataframe
	
import plotly.express as px

df["distance_label"] = (
    df["distance_m"].astype(int).astype(str) + " m"
)

fig = px.density_heatmap(
    df,
    x="recvPower_dBm",
    y="distance_label",
    nbinsx=50,
    histfunc="count",
    labels={
        "recvPower_dBm": "Ankommende Signalstärke [dBm]",
        "distance_label": "Distanz",
        "count": "Anzahl"
    }
)

fig.update_layout(
    xaxis_title="Ankommende Signalstärke [dBm]",
    yaxis_title="Distanz"
)

fig.write_image(os.path.join(resultDir, "plots", "pdf",
                                 "SignalpowerHeatmap.pdf"))  

