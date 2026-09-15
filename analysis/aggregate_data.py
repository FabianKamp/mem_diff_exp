# %% 
# loading packages
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

# set colors
colors_palette = ["#F2857D","#7EBDC3","#9ED9A3","#F5B971"]
sns.set_palette(colors_palette)
# set working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(script_dir))

# %% 
# load data
bin_width = .25
bin_width_per_item = .1
out_name = "aggregated_v1"

# define pilots
session_dict = {
    "M-V1": list(range(1,120))
}

# %%
# load data
def load_data(session_dict):
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
    return all_data

all_data = load_data(session_dict)
all_data = all_data.loc[(all_data.rt>150)]

# %%
# load settings
def add_load_col(output_data):
    if "load" in output_data.columns: 
        return output_data
    
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
    # add the load
    output_data = (output_data
        .assign(wave_id = lambda d: d.session_id.str[:4])
        .merge(load_df, on="wave_id")
    )
    return output_data

# %%
# time to sec, take log and digitize
def bin(time, width): 
    return np.floor(time/width)*width + width/2

def add_time_cols(output_data):
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
    return output_data

#%% 
# preprocess working memory data
def preproc_vs_trials(all_data):
    # filter 
    output_data = all_data.loc[
        (all_data.trial_type=='wm') & 
        (all_data.condition_name!='mixed') & 
        (all_data.phase == "recognition") 
        ].copy()
    print("NA responses: ", np.sum(output_data.response.isna()))

    # set the response data
    output_data.response = output_data.response.astype("Int64")
    output_data.correct_response = output_data.correct_response.astype("Int64")
    output_data["correct"] = (output_data.response == output_data.correct_response)
    output_data["time"] = output_data.encoding_time/1e3

    rt_by_response = (
        output_data.groupby(["session_id","encoding_time","condition_name","condition","correct"])["rt"]
        .mean()
        .unstack("correct")
        .rename(columns={True: "rt_hit", False: "rt_error"})
    )

    rt_by_response_median = (
        output_data.groupby(["session_id","encoding_time", "condition", "condition_name", "correct"])["rt"]
        .median()
        .unstack("correct")
        .rename(columns={True: "rt_hit_median", False: "rt_error_median"})
    )

    rt_by_response_thresh = (
        output_data.loc[(output_data["rt"]>=200) & (output_data["rt"]<=3000)]
        .groupby(["session_id", "encoding_time", "condition", "condition_name", "correct"])["rt"]
        .median()
        .unstack("correct")
        .rename(columns={True: "rt_hit_thresh", False: "rt_error_thresh"})
    )

    # aggregate
    output_data = (output_data
        .groupby(["wave_id", "session_id", "condition", "condition_name", "encoding_time"])
        .agg(
            valid_responses = ("response", lambda x: (~x.isna()).sum()),
            hits = ("correct", "sum"),
            accuracy = ("correct", "mean"), 
            rt = ("rt", "mean")
        )
        .assign(
            dprime = lambda d: (norm.ppf(d["accuracy"])-norm.ppf(1-d["accuracy"]))/np.sqrt(2)
        )
        .join(rt_by_response)
        .join(rt_by_response_median)
        .join(rt_by_response_thresh)
        .reset_index()
        .assign(subject_id = lambda d: d.session_id.str.split("-").str[-2].astype(int))
    )
    return output_data


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
# vs data 

vs_data = preproc_vs_trials(all_data)
vs_data = add_load_col(vs_data)
vs_data = add_time_cols(vs_data)
# plot_aggregate(output_data, time_col="bin_time_per_item")
# plot_aggregate(output_data, time_col="bin_time_per_item", load=3)
plot_aggregate(vs_data, time_col="bin_time_per_item", load=4)

# save output data
vs_data.to_csv(f"./output_data/aggregated/{out_name}_vs.csv")

# %%
# mixed trials
def preproc_mixed_trials(all_data):
    output_data = all_data.loc[
        (all_data.trial_type=='wm') & 
        (all_data.condition_name=='mixed') & 
        (all_data.response.notna()) &
        (all_data.phase == "recognition") 
        ].copy()

    output_data.response = output_data.response.astype("Int64")

    # get response name (visual vs semantic)
    output_data["response_name"] = (output_data
        .apply(lambda row: row.stimulus_left if row.response == 0 else row.stimulus_right, axis=1)
        .str.split("/").str[-1].str[0]
        .map({'3': "semantic", '4': "visual"})
    )

    rt_by_response = (
        output_data.groupby(["session_id","encoding_time","condition_name","condition","response_name"])["rt"]
        .mean()
        .unstack("response_name")
        .rename(columns={"semantic": "rt_semantic", "visual": "rt_visual"})
    )

    rt_by_response_median = (
        output_data
        .groupby(["session_id","encoding_time","condition_name","condition","response_name"])["rt"]
        .median()
        .unstack("response_name")
        .rename(columns={"semantic": "rt_semantic_median", "visual": "rt_visual_median"})
    )

    rt_by_response_thresh = (
        output_data
        .loc[(output_data["rt"]>=200) & (output_data["rt"]<=3000)]
        .groupby(["session_id","encoding_time","condition_name","condition","response_name"])["rt"]
        .median()
        .unstack("response_name")
        .rename(columns={"semantic": "rt_semantic_thresh", "visual": "rt_visual_thresh"})
    )
    
    # aggregate
    output_data = (
        output_data.groupby(["wave_id", "session_id", "condition", "condition_name", "encoding_time"])
        .agg(
            count_visual = ("response_name", lambda x: (x == 'visual').sum()),
            count_semantic = ("response_name", lambda x: (x == 'semantic').sum()),
            rt = ("rt", "mean")
        )
        .join(rt_by_response)
        .join(rt_by_response_median)
        .join(rt_by_response_thresh)
        .reset_index()
        .assign(subject_id = lambda d: d.session_id.str.split("-").str[-2].astype(int))
    )
    
    # ["response_name"]
    # output_data = pd.DataFrame({
    #     "count_visual":     grouped_data.apply(lambda x: (x == 'visual').sum()),
    #     "count_semantic":   grouped_data.apply(lambda x: (x == 'semantic').sum())
    # }).reset_index()

    percent_semantic = output_data.count_semantic/(output_data.count_visual + output_data.count_semantic)

    output_data = output_data.assign(
        percent_semantic = percent_semantic,
        dprime = np.sqrt(2)*norm.ppf(percent_semantic),
        percent_visual = 1-percent_semantic,
        semantic_index = (output_data.count_semantic-output_data.count_visual)/(output_data.count_visual + output_data.count_semantic)
    )
    return output_data

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

# %%
# mixed data
mixed_data = preproc_mixed_trials(all_data)
mixed_data = add_load_col(mixed_data)
mixed_data = add_time_cols(mixed_data)

# plot_mixed(output_data, time_col="bin_time_per_item")
# plot_mixed(output_data, time_col="bin_time_per_item", load=3)
plot_mixed(mixed_data, time_col="bin_time_per_item", load=4)

# save output data
mixed_data.to_csv(f"./output_data/aggregated/{out_name}_mixed.csv")

# %%
# lm data
def preproc_lm_trials(all_data): 
    lm_data = all_data.loc[
        (all_data.trial_type=="lm")
        ].copy()
    print("NA responses: ", np.sum(lm_data.response.isna()))

    # set response data
    lm_data.response = lm_data.response.astype('Int64')
    lm_data.correct_response = lm_data.correct_response.astype('Int64')
    lm_data["correct"] = (lm_data.response == lm_data.correct_response)
    lm_data["time"] = lm_data.encoding_time/1e3

    rt_by_response = (
        lm_data.groupby(["session_id","encoding_time", "condition", "condition_name", "correct"])
        ["rt"].mean()
        .unstack("correct")
        .rename(columns={True: "rt_hit", False: "rt_error"})
    )

    rt_by_response_median = (
        lm_data.groupby(["session_id","encoding_time", "condition", "condition_name", "correct"])
        ["rt"].median()
        .unstack("correct")
        .rename(columns={True: "rt_hit_median", False: "rt_error_median"})
    )

    rt_by_response_thresh = (
        lm_data.loc[(lm_data["rt"]>=200) & (lm_data["rt"]<=3000)]
        .groupby(["session_id","encoding_time", "condition", "condition_name", "correct"])
        ["rt"].median()
        .unstack("correct")
        .rename(columns={True: "rt_hit_thresh", False: "rt_error_thresh"})
    )

    # aggregate
    lm_data = (lm_data
        .groupby(["wave_id", "session_id", "encoding_time", "condition", "condition_name"])
        .agg(
            valid_responses = ("response", lambda x: (~x.isna()).sum()),
            hits = ("correct", "sum"),
            responses = ("correct", "count"),
            accuracy = ("correct", "mean"), 
            rt = ("rt", "mean"),
        )
        .assign(
            accuracy_corrected = lambda d: d["accuracy"].clip(0.5/d["responses"], (d["responses"]-0.5)/d["responses"]), 
        )
        .join(rt_by_response)
        .join(rt_by_response_median)
        .join(rt_by_response_thresh)
        .reset_index()
        .assign(
            subject_id = lambda d: d.session_id.str.split("-").str[-2].astype(int),
            dprime = lambda d: (norm.ppf(d["accuracy_corrected"])-norm.ppf(1-d["accuracy_corrected"]))/np.sqrt(2)
        )
    )
    return lm_data

# %%
lm_data = preproc_lm_trials(all_data)
lm_data = add_load_col(lm_data)
lm_data = add_time_cols(lm_data)

# save
lm_data.to_csv(f"./output_data/aggregated/{out_name}_lm.csv")


# %%
