# %% 
# loading packages
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
import matplotlib as mpl

# SVG export settings for Inkscape compatibility
mpl.rcParams['svg.fonttype'] = 'none'  # keep text as text (editable in Inkscape)


# %%
# colors 
color_dict = {
    "semantic": "#E69F00", 
    "visual": "#0072B2", 
    "mixed": "#009E73", 
    "difference": "#000000",
}

colors_palette = list(color_dict.values())
sns.set_palette(colors_palette)
sns.set_theme(style="ticks")

# %%
# set working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(script_dir))

# %% 
# load data
bin_width = .25
bin_width_per_item = .1
out_name = "aggregated_pilot_2"

# define pilots
session_dict = {
    "M-PA": list(range(2,30)), # first dataset did not contain encoding times
    "M-PB": list(range(1,30)),
    "M-PD": list(range(1,30)),
    "M-PE": list(range(1,30)),
    "M-PF": list(range(1,30)),
    "M-PG": list(range(1,30)),
}

# %%
# load data
def load_data(session_dict):
    out_files = [f"./output_data/raw/{wave_code}/{wave_code}-{i:03d}{suffix}.csv" 
                for wave_code in session_dict.keys()
                for i in session_dict[wave_code] 
                for suffix in ["", "-A", "-B", "-C" "-D"]
                ]
    out_files = filter(os.path.exists, out_files)

    # concat data
    all_data = [] 
    for file in out_files: 
        data = pd.read_csv(file)   
        all_data.append(data)
    all_data = pd.concat(all_data) 

    # add a suffix where its missing
    all_data = all_data.loc[~all_data.session_id.isna()]
    mask = all_data.session_id.str.contains(r'\d$')
    all_data.loc[mask, 'session_id'] = all_data.loc[mask, 'session_id'] + "-A"

    # wave id fix
    mask = ~all_data["wave_id"].str.startswith("M-")
    all_data.loc[mask, "wave_id"] = "M-" + all_data.loc[mask, "wave_id"]

    return all_data

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
    output_data = output_data.merge(load_df, on="wave_id")

    return output_data

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

# %% 
def get_bad_sessions(all_data): 
    # Check catch trials BEFORE filtering to wm only
    catch_data = all_data.loc[all_data.trial_type=="catch"].copy()
    catch_data["response"] = catch_data.response.astype("Int64")
    catch_data["correct_response"] = catch_data.correct_response.astype("Int64")
    catch_data["correct"] = (catch_data.response == catch_data.correct_response)

    catch_incorrect = catch_data.groupby("session_id")["correct"].apply(lambda x: (~x).sum())
    caught_sessions = catch_incorrect[catch_incorrect > 1].index.to_list()
    print(caught_sessions)

    output_data = all_data.loc[
        (all_data.trial_type=='wm') & 
        (all_data.condition_name!='mixed') & 
        (all_data.phase == "recognition") &
        (all_data.rt>150)
        ].copy()

    output_data.response = output_data.response.astype("Int64")
    output_data.correct_response = output_data.correct_response.astype("Int64")
    output_data["correct"] = (output_data.response == output_data.correct_response)

    
    output_data = (output_data
        .groupby(["wave_id", "session_id", "condition", "condition_name", "encoding_time"])
        .agg(
            valid_responses = ("response", lambda x: (~x.isna()).sum()),
            hits = ("correct", "sum"),
            accuracy = ("correct", "mean"), 
            rt = ("rt", "mean")
        )
        .reset_index()
        .assign(subject_id = lambda d: d.session_id.str.split("-").str[-2].astype(int))
    )

    session_means = output_data.groupby("session_id")[["hits", "accuracy"]].mean()
    poor_sessions = session_means.loc[session_means.accuracy<=.5].index.to_list()
    print(poor_sessions)

    bad_sessions = set(caught_sessions + poor_sessions)

    return set(bad_sessions)

#%% 
# preprocess working memory data
def preproc_vs_trials(all_data):
    # filter 
    output_data = all_data.loc[
        (all_data.trial_type=='wm') & 
        (all_data.condition_name!='mixed') & 
        (all_data.phase == "recognition") &
        (all_data.rt>150)
        ].copy()
    print("NA responses: ", np.sum(output_data.response.isna()))

    na_counts = output_data.groupby("session_id")["response"].apply(lambda x: x.isna().sum())
    print("NA responses:", na_counts[na_counts > 0])

    # set the response data
    output_data.response = output_data.response.astype("Int64")
    output_data.correct_response = output_data.correct_response.astype("Int64")
    output_data["correct"] = (output_data.response == output_data.correct_response)
    output_data["time"] = output_data.encoding_time/1e3

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
        .reset_index()
        .assign(subject_id = lambda d: d.session_id.str.split("-").str[-2].astype(int))
    )
    return output_data


# %%
def plot_vs(output_data, time_col, wave_ids=None, load=None, save=True):
    data = output_data.copy()
    if load is not None:
        data = data.loc[data.load == load]

    if wave_ids is not None:
        assert type(wave_ids)==list
        data = data.loc[data.wave_id.isin(wave_ids)]

    fig, ax = plt.subplots(figsize=(12, 5), dpi=150)

    # --- plot settings ---
    desired_box_width = 100  # box width in data units (e.g., ms)
    box_alpha = 0.6
    line_alpha = 0.6
    line_width = 0.6
    marker_size = 6

    # compute box width as relative proportion for seaborn
    unique_x = np.sort(data[time_col].unique())
    min_gap = np.diff(unique_x).min() if len(unique_x) > 1 else desired_box_width
    box_width = desired_box_width / min_gap

    # offset to align lines with dodged boxes (half box width per condition)
    x_offset = desired_box_width / 4
    offset_map = {"visual": -x_offset, "semantic": x_offset}
    data = data.assign(**{f"{time_col}_offset": data[time_col] + data["condition_name"].map(offset_map)})

    # --- boxplot (background, transparent) ---
    sns.boxplot(
        data=data,
        x=time_col,
        y="accuracy",
        hue="condition_name",
        hue_order=["visual", "semantic"],
        native_scale=True,
        width=box_width,
        palette=color_dict,
        boxprops=dict(alpha=box_alpha, linewidth=1),
        whiskerprops=dict(alpha=box_alpha, linewidth=1),
        capprops=dict(alpha=box_alpha, linewidth=1),
        medianprops=dict(color="black", linewidth=2, solid_capstyle="butt"),
        flierprops=dict(alpha=0),  # hide outliers (shown by lineplot)
        ax=ax
    )

    # --- lineplot (foreground) ---
    sns.lineplot(
        data=data,
        x=f"{time_col}_offset",
        y="accuracy",
        hue="condition_name",
        units="session_id",
        estimator=None,
        palette=color_dict,
        alpha=line_alpha,
        linewidth=line_width,
        marker='o',
        markersize=marker_size,
        legend=False,
        ax=ax
    )

    # --- axis formatting ---
    ax.set_xlim(300, 2300)
    ax.set_xlabel("Encoding time (ms)", fontsize=11)
    ax.set_ylabel("Accuracy", fontsize=11)
    ax.set_ylim(-.1, 1.1)
    ax.tick_params(labelsize=10)

    ax.axhline(0.5, color="black", linestyle="--", linewidth=1, alpha=0.5)

    # title with wave names
    waves = ", ".join([w.replace("M-", "") for w in wave_ids]) if wave_ids else "all"
    load_str = f" (load={load})" if load else ""
    ax.set_title(f"Waves: {waves}{load_str}", fontsize=12)

    plt.tight_layout()

    if save:
        waves_fname = "_".join([w.replace("M-", "") for w in wave_ids]) if wave_ids else "all"
        load_fname = f"_load{load}" if load else ""
        fname = f"./figures/pilots/vs_{waves_fname}{load_fname}.svg"
        fig.savefig(fname, format="svg", bbox_inches="tight")
        print(f"Saved: {fname}")

    # print median accuracy table
    median_table = (data
        .groupby(["condition_name", time_col])["accuracy"]
        .median()
        .unstack("condition_name")
        .round(2)
    )
    print(f"\nMedian accuracy ({waves}):")
    print(median_table.to_string())
    print()


# %%
# mixed trials
def preproc_mixed_trials(all_data):
    output_data = all_data.loc[
        (all_data.trial_type=='wm') & 
        (all_data.condition_name=='mixed') & 
        (all_data.response.notna()) &
        (all_data.rt>150) &
        (all_data.phase == "recognition") 
        ].copy()

    output_data.response = output_data.response.astype("Int64")

    # get response name (visual vs semantic)
    output_data["response_name"] = (output_data
        .apply(lambda row: row.stimulus_left if row.response == 0 else row.stimulus_right, axis=1)
        .str.split("/").str[-1].str[0]
        .map({'3': "semantic", '4': "visual"})
    )
    
    # aggregate
    output_data = (
        output_data.groupby(["wave_id", "session_id", "condition", "condition_name", "encoding_time"])
        .agg(
            count_visual = ("response_name", lambda x: (x == 'visual').sum()),
            count_semantic = ("response_name", lambda x: (x == 'semantic').sum()),
            rt = ("rt", "mean")
        )
        .reset_index()
        .assign(subject_id = lambda d: d.session_id.str.split("-").str[-2].astype(int))
    )

    percent_semantic = output_data.count_semantic/(output_data.count_visual + output_data.count_semantic)

    output_data = output_data.assign(
        percent_semantic = percent_semantic,
        dprime = np.sqrt(2)*norm.ppf(percent_semantic),
        percent_visual = 1-percent_semantic,
        semantic_index = (output_data.count_semantic-output_data.count_visual)/(output_data.count_visual + output_data.count_semantic)
    )
    return output_data

# %%
def plot_mixed(output_data, time_col, wave_ids=None, load=None, save=True):
    data = output_data.copy()
    if load is not None:
        data = data.loc[data.load == load]

    if wave_ids is not None:
        assert type(wave_ids)==list
        data = data.loc[data.wave_id.isin(wave_ids)]

    fig, ax = plt.subplots(figsize=(12, 5), dpi=150)

    # --- plot settings ---
    desired_box_width = 100  # box width in data units (e.g., ms)
    box_alpha = 0.6
    line_alpha = 0.6
    line_width = 0.6
    marker_size = 6
    mixed_color = color_dict["mixed"]

    # compute box width as relative proportion for seaborn
    unique_x = np.sort(data[time_col].unique())
    min_gap = np.diff(unique_x).min() if len(unique_x) > 1 else desired_box_width
    box_width = desired_box_width / min_gap

    # --- boxplot (background, transparent) ---
    sns.boxplot(
        data=data,
        x=time_col,
        y="percent_semantic",
        native_scale=True,
        width=box_width,
        color=mixed_color,
        boxprops=dict(alpha=box_alpha, linewidth=1),
        whiskerprops=dict(alpha=box_alpha, linewidth=1),
        capprops=dict(alpha=box_alpha, linewidth=1),
        medianprops=dict(color="black", linewidth=2, solid_capstyle="butt"),
        flierprops=dict(alpha=0),
        ax=ax
    )

    # --- lineplot (foreground) ---
    sns.lineplot(
        data=data,
        x=time_col,
        y="percent_semantic",
        units="session_id",
        estimator=None,
        color=mixed_color,
        alpha=line_alpha,
        linewidth=line_width,
        marker='o',
        markersize=marker_size,
        legend=False,
        ax=ax
    )

    # reference line at chance (0.5)
    ax.axhline(0.5, color="black", linestyle="--", linewidth=1, alpha=0.5)

    # --- axis formatting ---
    ax.set_xlim(300, 2300)
    ax.set_xlabel("Encoding time (ms)", fontsize=11)
    ax.set_ylabel("Percent semantic", fontsize=11)
    ax.set_ylim(-.1, 1.1)
    ax.tick_params(labelsize=10)

    # title with wave names
    waves = ", ".join([w.replace("M-", "") for w in wave_ids]) if wave_ids else "all"
    load_str = f" (load={load})" if load else ""
    ax.set_title(f"Waves: {waves}{load_str}", fontsize=12)

    plt.tight_layout()

    if save:
        waves_fname = "_".join([w.replace("M-", "") for w in wave_ids]) if wave_ids else "all"
        load_fname = f"_load{load}" if load else ""
        fname = f"./figures/pilots/mixed_{waves_fname}{load_fname}.svg"
        fig.savefig(fname, format="svg", bbox_inches="tight")
        print(f"Saved: {fname}")

# %%
# load and preproc data 
all_data = load_data(session_dict)
bad_sessions = get_bad_sessions(all_data)
all_data = all_data.loc[~all_data.session_id.isin(bad_sessions)]


# %%
# vs data 
vs_data = preproc_vs_trials(all_data)
vs_data = add_load_col(vs_data)
vs_data = add_time_cols(vs_data)

plot_vs(vs_data, time_col="encoding_time",  wave_ids=["M-PA", "M-PB"], save=False)
plot_vs(vs_data, time_col="encoding_time",  wave_ids=["M-PD"], save=False)
plot_vs(vs_data, time_col="encoding_time",  wave_ids=["M-PE"], save=False)
plot_vs(vs_data, time_col="encoding_time",  wave_ids=["M-PF"], save=False)
plot_vs(vs_data, time_col="encoding_time", wave_ids=["M-PG"], save=False)

rel_cols = ["wave_id", "session_id", "condition", "condition_name", "encoding_time", "hits", "accuracy", "valid_responses", "load"]
vs_data[rel_cols].to_csv(f"./output_data/aggregated/aggregated_pilot_vs.csv", index=False)


# plot_vs(vs_data, time_col="encoding_time",  wave_ids=["M-PA","M-PB"])
# plot_vs(vs_data, time_col="encoding_time",  wave_ids=["M-PD","M-PE","M-PF"])
# plot_vs(vs_data, time_col="encoding_time", wave_ids=["M-PG"])


# %%
# mixed data
mixed_data = preproc_mixed_trials(all_data)
mixed_data = add_load_col(mixed_data)
mixed_data = add_time_cols(mixed_data)

plot_mixed(mixed_data, time_col="encoding_time", wave_ids=["M-PA","M-PB"])
plot_mixed(mixed_data, time_col="encoding_time", wave_ids=["M-PD","M-PE","M-PF"])
plot_mixed(mixed_data, time_col="encoding_time", wave_ids=["M-PG"])



# %%


