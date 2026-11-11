# %% 
# loading packages
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

# %% 
def plot_aggregate(output_data, time_col, load=None): 
    data = output_data.copy()
    if load is not None: 
        data = output_data.loc[output_data.load==load]
    
    fig, (ax_bar, ax_box) = plt.subplots(
        nrows=2, 
        ncols=1, 
        sharex=True, 
        gridspec_kw={"height_ratios": [1, 3]},
        figsize=(10, 6)
    )

    session_count = (data
        .groupby([time_col, "condition", "condition_name"])["session_id"]
        .nunique()
        .reset_index()
        .rename(columns=dict(session_id="session_count"))
    )

    bar = sns.barplot(
        data=session_count,
        x=time_col,
        y="session_count",
        native_scale=True,
        ax=ax_bar,
        legend=False, 
        facecolor="white",
        edgecolor="black",
    )
    bar.set_xlabel("")  
    bar.grid(alpha=.2)

    box = sns.boxplot(
        data=data, 
        x=time_col, 
        y="accuracy", 
        hue="condition_name", 
        native_scale=True,
        palette=colors_palette[:2], 
        medianprops={'color': 'red', 'linewidth': 2},
        ax=ax_box
        )
    
    box.legend(loc="lower right")
    box.grid(alpha=.2)
    box.set_xlabel(time_col.replace("_", " "))
    title = f"Load = {load}" if load is not None else ""
    bar.set_title(title)
    plt.tight_layout()

# %%
def plot_mixed(output_data, time_col, load=None): 
    data = output_data.copy()
    if load is not None: 
        data = output_data.loc[output_data.load==load]
    
    fig, (ax_bar, ax_box) = plt.subplots(
    nrows=2, 
    ncols=1, 
    sharex=True, 
    gridspec_kw={"height_ratios": [1, 3]},
    figsize=(10, 6)
    )

    session_count = (data
        .groupby(time_col)["session_id"]
        .nunique()
        .reset_index()
        .rename(columns=dict(session_id="session_count"))
    )

    bar = sns.barplot(
        data=session_count,
        x=time_col,
        y="session_count",
        native_scale=True,
        ax=ax_bar,
        legend=False, 
        facecolor="white",
        edgecolor="black",
    )
    bar.set_xlabel("")  
    bar.grid(alpha=.2)

    box = sns.boxplot(
        data=data, 
        x=time_col, 
        y="percent_visual", 
        native_scale=True,
        medianprops={'color': 'green', 'linewidth': 2},
        color = colors_palette[2],
        ax=ax_box
        )
    
    box.grid(alpha=.2)
    box.axhline(.5, c="k", linewidth=2)
    box.set_xlabel(time_col.replace("_", " "))


    title = f"Load = {load}" if load is not None else ""
    bar.set_title(title)
    plt.tight_layout()