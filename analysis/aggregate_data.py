# %% 
# loading packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# check cwd
if os.path.basename(os.getcwd()) == "analysis": 
    os.chdir("..")
colors_palette = ["#F2857D","#7EBDC3","#9ED9A3","#F5B971"]
sns.set_palette(colors_palette)

# %% 
# load data
# define exclusion criteria
session_ids = {
    "M-PE": list(range(1,12)),
    "M-PD": list(range(1,12)),
    "M-PF": list(range(1,12)),
}

out_files = [f"./output_data/raw/{wave_code}/{wave_code}-{i:03d}-{suffix}.csv" 
             for wave_code in session_ids.keys()
             for i in session_ids[wave_code] 
             for suffix in "ABCD" 
             ]
out_files = filter(os.path.exists, out_files)

# concat data
all_data = [] 
for file in out_files: 
    data = pd.read_csv(file)   
    all_data.append(data)
all_data = pd.concat(all_data) 

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

# time to sec, take log and digitize
output_data = (output_data
    .assign(time = lambda d: d["encoding_time"]/1e3)
    .assign(bin_time = lambda d: np.floor(d["time"]/.25)*.25 +.125)
    .assign(log_time = lambda d: np.log(d["time"]))
    .assign(bin_log_time = lambda d: np.floor(d["log_time"]/.25)*.25 +.125)
)

# save the ouput_data
output_data.to_csv("./output_data/aggregated/aggregated_wm-vs.csv")

# %% 
# native time plot
# data count 
fig, (ax_bar, ax_box) = plt.subplots(
    nrows=2, 
    ncols=1, 
    sharex=True, 
    gridspec_kw={"height_ratios": [1, 3]},
    figsize=(10, 6)
)

session_count = (output_data
    .groupby(["bin_time", "condition", "condition_name"])["session_id"]
    .nunique()
    .reset_index()
    .rename(columns=dict(session_id="session_count"))
)

bar = sns.barplot(
    data=session_count,
    x="bin_time",
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
    x="bin_time", 
    y="accuracy", 
    hue="condition_name", 
    native_scale=True,
    palette=colors_palette[:2]
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

