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

fig = px.scatter(
    df,
    x="recvPower_dBm",
    y="distance_m",
    marginal_x="histogram",
        labels={
    	"recvPower_dBm": "Ankommende Signalstärke [dBm]"
    }
)

fig.update_layout(
    yaxis=dict(
        tickmode="linear",
        dtick=120,
        title_text="Distanz [m]"
    ),
    yaxis2=dict(
        title_text="Anzahl",
        showticklabels=True
    )
)

os.makedirs(os.path.join(resultDir, "plots", "pdf"), exist_ok=True)

fig.write_html(os.path.join(resultDir, "plots", "distancetoRecvPowerReverse.html"))

fig.write_image(os.path.join(resultDir, "plots", "pdf",
                                 "distancetoRecvPowerReverse.pdf"))    

