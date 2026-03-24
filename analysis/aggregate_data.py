# %% 
# loading packages
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# set colors
colors_palette = ["#F2857D","#7EBDC3","#9ED9A3","#F5B971"]
sns.set_palette(colors_palette)
# set working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(script_dir))

# %% 
# load data

# define pilots
session_dict = {
    "M-PE": list(range(1,12)),
    "M-PD": list(range(1,12)),
    "M-PF": list(range(1,12)),
    "M-PG": list(range(1,21)),
}

# session_dict = {
#     "M-PG": list(range(1,21)),
# }

bin_width = .25
bin_width_per_item = .125
out_name = "aggregated_pilots"

# %%
# load data
out_files = [f"./output_data/raw/{wave_code}/{wave_code}-{i:03d}-{suffix}.csv" 
             for wave_code in session_dict.keys()
             for i in session_dict[wave_code] 
             for suffix in "ABCD" 
             ]
out_files = filter(os.path.exists, out_files)

# concat data
all_data = [] 
for file in out_files: 
    data = pd.read_csv(file)   
    all_data.append(data)
all_data = pd.concat(all_data) 

# %%
# load settings
setting_files = [f"./input_data/{wave_id}/_settings.json" for wave_id in session_dict.keys()]
setting_files = filter(os.path.exists, setting_files)

load_df = []
for file in setting_files: 
    with open(file, "r") as f: 
        settings = json.load(f)
        load_df.append({
            "wave_id": settings["wave"]["wave_id"],
            "load": settings["memory_experiment"]["load"],
        })
load_df = pd.DataFrame(load_df)

#%% 
# preprocess working memory data
# filter data
output_data = all_data.loc[
    (all_data.trial_type=='wm') & 
    (all_data.condition_name!='mixed') & 
    (all_data.phase == "recognition") 
    ].copy()
print("NA responses: ", np.sum(output_data.response.isna()))

# set the 
output_data.response = output_data.response.astype("Int64")
output_data.correct_response = output_data.correct_response.astype("Int64")
output_data["correct"] = (output_data.response == output_data.correct_response)
output_data["time"] = output_data.encoding_time/1e3

# aggregate
output_data = (output_data
    .groupby(["session_id", "condition", "condition_name", "encoding_time"])
    .agg(
        hits = ("correct", "sum"),
        responses = ("correct", "count"),
        accuracy = ("correct", "mean")
    )
    .reset_index()
)

# add the load
output_data = (output_data
    .assign(wave_id = lambda d: d.session_id.str[:4])
    .merge(load_df, on="wave_id")
)

# time to sec, take log and digitize
def bin(time, width): 
    return np.floor(time/width)*width + width/2

output_data = (output_data
    .assign(time = lambda d: d["encoding_time"]/1e3)
    .assign(log_time = lambda d: np.log(d["time"]))
    .assign(bin_time = lambda d: bin(d["time"], bin_width))
    .assign(bin_log_time = lambda d: bin(d["log_time"], bin_width))
)

# time per item
output_data = (output_data
    .assign(time_per_item = lambda d: d["time"]/d["load"])
    .assign(log_time_per_item = lambda d: np.log(d["time_per_item"]))
    .assign(bin_time_per_item = lambda d: bin(d["time_per_item"], bin_width_per_item))
    .assign(bin_log_time_per_item = lambda d: bin(d["log_time_per_item"], bin_width_per_item))
)

# save the ouput_data
output_data.to_csv(f"./output_data/aggregated/{out_name}.csv")

# %% 
def plot_aggregate(output_data, time_col, load): 
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
        ax=ax_box
        )
    box.legend(loc="lower right")
    box.grid(alpha=.2)
    box.set_xlabel(time_col.replace("_", " "))
    title = f"Load = {load}" if load is not None else ""
    bar.set_title(title)
    plt.tight_layout()

# %% 
# native time plot
plot_aggregate(output_data, time_col="bin_time_per_item", load=3)
plot_aggregate(output_data, time_col="bin_time_per_item", load=3)
plot_aggregate(output_data, time_col="time_per_item", load=4)




# %% 
# time per item plot
# data count 
fig, (ax_bar, ax_box) = plt.subplots(
    nrows=2, 
    ncols=1, 
    sharex=True, 
    gridspec_kw={"height_ratios": [1, 3]},
    figsize=(10, 6)
)

session_count = (output_data
    .groupby(["bin_time_per_item", "condition", "condition_name"])["session_id"]
    .nunique()
    .reset_index()
    .rename(columns=dict(session_id="session_count"))
)

bar = sns.barplot(
    data=session_count,
    x="bin_time_per_item",
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
    data=output_data, 
    x="bin_time_per_item", 
    y="accuracy", 
    hue="condition_name", 
    native_scale=True,
    palette=colors_palette[:2],
    medianprops={'color': 'red', 'linewidth': 2}
    )
box.legend(loc="lower right")
box.grid(alpha=.2)
box.set_xlabel("native time")
plt.tight_layout()

# %% 
# log plot
# data count 
fig, (ax_bar, ax_box) = plt.subplots(
    nrows=2, 
    ncols=1, 
    sharex=True, 
    gridspec_kw={"height_ratios": [1, 3]},
    figsize=(10, 6)
)

session_count = (output_data
    .groupby(["bin_log_time", "condition", "condition_name"])["session_id"]
    .nunique()
    .reset_index()
    .rename(columns=dict(session_id="session_count"))
)

bar = sns.barplot(
    data=session_count,
    x="bin_log_time",
    y="session_count",
    native_scale=True,
    ax=ax_bar,
    legend=False, 
    facecolor="white",
    edgecolor="black",
)
bar.set_xlabel("")  
bar.grid(alpha=.2)
bar_top = bar.secondary_xaxis("top", functions=(np.exp, np.log))

box = sns.boxplot(
    data=output_data, 
    x="bin_log_time", 
    y="accuracy", 
    hue="condition_name", 
    native_scale=True,
    palette=colors_palette[:2]
    )
box.legend(loc="lower right")
box.grid(alpha=.2)
box.set_xlabel("log time")
plt.tight_layout()


# %%
