# DataScraper
# Go to dreaming spanish website, go to requests, then find dayWatchedTime
# Copy it, then paste into notepad as ds_raw.txt

#%% Requesting Data

import json
import pandas as pd
# import matplotlib.pyplot as plt # PYPLOT
import plotly.graph_objects as go # PLOTLY
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import numpy as np
import matplotlib.dates as mdates
import requests
from dotenv import load_dotenv
import os
import plotly.io as pio # PLOTLY
pio.renderers.default = 'browser' # PLOTLY

load_dotenv()
url = "https://app.dreaming.com/.netlify/functions/dayWatchedTime?language=es"
headers = {
    "Authorization": os.getenv("DS_AUTH_HEADER")  
    }

response = requests.get(url, headers=headers)

data = response.json()

script_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(script_dir, 'Dreaming Spanish Hours Chart.png')


# with open('ds_raw.txt') as f:
#     data = json.load(f)




#%% Making dataFrame in Pandas
df = pd.DataFrame(data)

df['totalHours'] = (df['timeSeconds'].cumsum() / 3600).round(2) + 3
df["date"] = pd.to_datetime(df["date"])  # convert here, before anything else
date = df['date']
totalHours = df['totalHours']

# Now the dataframe is ready

milestones = {50: "red", 150: "purple", 300: "blue", 600: "cyan", 1000: "green", 1500: "green" }

#%% Plot - Plotly

fig = go.Figure()

# Main line
fig.add_trace(go.Scatter(
    x=date,
    y=totalHours,
    mode='lines',
    line=dict(color='black', width=2),
    fill='tozeroy',
    fillcolor='rgba(0,0,0,0.1)',
    name='Hours'
))

# Milestone horizontal lines + labels
for y, color in milestones.items():
    fig.add_hline(
        y=y,
        line=dict(color=color, dash='dash', width=1),
        opacity=0.3
    )
    fig.add_annotation(
        x=date.iloc[0],
        y=y + 10,
        text=f"{y} hrs",
        showarrow=False,
        font=dict(color=color, size=8),
        xanchor='left'
    )

# Milestone crossing date annotations
for y, color in milestones.items():
    subset = df[df["totalHours"] >= y]
    if subset.empty:
        continue
    crossed = subset.iloc[0]
    fig.add_annotation(
        x=crossed["date"],
        y=y + 65,
        text=crossed["date"].strftime("%b %d %Y"),
        showarrow=False,
        font=dict(color=color, size=8),
        textangle=-20,
        xanchor='left'
    )

fig.update_layout(
    title='Spanish Progress Tracking',
    xaxis_title='Date',
    yaxis_title='Hours',
    yaxis=dict(range=[0, 2000]),
    xaxis=dict(
        range=[date.iloc[0], date.iloc[-1]],
        tickformat="%m/%d/%y",
        dtick="M2"
    ),
    width=1400,
    height=400,
    plot_bgcolor='white',
    showlegend=False
)



fig.write_image(save_path, scale=1.5)
print(f"Plot saved to {save_path}")
print(f'Current hours: {totalHours.iloc[-1]}')
fig.show()



#%% Plot - Matplotlib
# =============================================================================
# 
# plt.figure(figsize=(30, 5))
# plt.plot(date,totalHours,linewidth = 2,color = 'k')
# # plt.xticks(rotation=45, ha='right')
# plt.title('Spanish Progress Tracking')
# plt.ylabel('Hours')
# plt.xlabel('Date')
# plt.ylim([0, 2000])
# plt.xlim([date.iloc[0], date.iloc[-1]])
# plt.fill_between(date, totalHours, alpha=0.1, color="black")
# 
# ax = plt.gca()
# ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
# ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%y"))
# 
# for y, color in milestones.items():
#     plt.axhline(y=y, color=color, linestyle='--',alpha=.2)
#     plt.text(date.iloc[0], y+10, f"{y} hrs", color=color, fontsize=8)
#     
# for y, color in milestones.items():
#     subset = df[df["totalHours"] >= y]
#     if subset.empty:
#         continue
#     crossed = subset.iloc[0]
#     plt.annotate(crossed["date"].strftime("%b %d %Y"), xy=(crossed["date"], y+65), fontsize=8, color=color, rotation=20)
# 
# 
# 
# # Save Plot
# 
# plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
# print(f"Plot saved to {save_path}")
# print(f'Current hours: {totalHours.iloc[-1]}')
# plt.show()
# =============================================================================

#%% =============================================================================
# Turn to CSV
df.to_csv("raw_data.csv", index=False)
# =============================================================================


# input('debug...')

# =============================================================================
# #%% Rolling average
# 
# window = 180 # 90 days
# recent = df.tail(window)
# avg_h_per_day = (recent["totalHours"].iloc[-1] - recent["totalHours"].iloc[0]) / window
# 
# future_dates = pd.date_range(df["date"].iloc[-1] + pd.Timedelta(days=1), periods=365)
# future_hours = [totalHours.iloc[-1] + avg_h_per_day * i for i in range(1, 366)]
# 
# plt.plot(future_dates, future_hours, color="blue", linestyle="--", label="Projected")
# plt.xlim([date.iloc[0], future_dates[-1]])
# =============================================================================

#%% Polynomial
# =============================================================================
# df["date"] = pd.to_datetime(df["date"])
# df["dayNum"] = ((df["date"] - df["date"].iloc[0]).dt.days) + 1
# 
# X = df["dayNum"].values.reshape(-1, 1)
# y_hours = df["totalHours"].values
# 
# poly = PolynomialFeatures(degree = 2)
# X_poly = poly.fit_transform(X)
# 
# model = LinearRegression()
# model.fit(X_poly,y_hours)
# 
# # Generate future day numbers — 365 days beyond your last data point
# last_day = df["dayNum"].iloc[-1]
# future_days = np.arange(last_day + 1, last_day + 365).reshape(-1, 1)
# future_dates = pd.date_range(df["date"].iloc[-1] + pd.Timedelta(days=1), periods=364)
# future_hours = model.predict(poly.transform(future_days))
# 
# # Shift the entire projection up/down to match your last real value
# offset = totalHours.iloc[-1] - future_hours[0]
# future_hours = future_hours + offset
# 
# # Prepend last real point
# future_dates = future_dates.insert(0, df["date"].iloc[-1])
# future_hours = np.insert(future_hours, 0, totalHours.iloc[-1])
# 
# plt.plot(future_dates, future_hours, color="blue", linestyle="--", label="Projected")
# plt.xlim([date.iloc[0], future_dates[-1]])
# =============================================================================



