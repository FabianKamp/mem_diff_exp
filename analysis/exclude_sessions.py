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
to_exclude = []

# returned data
returned_sessions = [
    # "M-PG-006-B"
]
to_exclude.extend(returned_sessions)

# outname 
outname = "excluded_sessions_v1"

# load data
data_file = "./output_data/aggregated/aggregated_v1_vs.csv"
output_data = pd.read_csv(data_file)

quality_file = "./output_data/data_quality/qc_M-V1.csv"
data_quality = pd.read_csv(quality_file)

# %%
# quick check 
box = sns.boxplot(
    data=output_data, 
    x="time", 
    y="accuracy", 
    hue="condition_name", 
    native_scale=True,
    palette=colors_palette[:2],
    medianprops={'color': 'red', 'linewidth': 2},
    showmeans=True
    )
box.grid(alpha=.3)

# %% 
# exclude based on data quality
blur_threshold = 3
time_outs_threshold = 3
fullscreen_exits_thresholds = 1
attention_errors_threshold = 1

low_quality_sessions = data_quality.loc[
    (data_quality.blur > blur_threshold) |
    (data_quality.time_outs > time_outs_threshold) |
    (data_quality.fullscreenexit > fullscreen_exits_thresholds) |
    (data_quality.attention_check_errors > attention_errors_threshold), 
    "session_id"
].to_list()

print("To exclude because of low quality: ", low_quality_sessions)
print("n exluded: ", len(low_quality_sessions))
# %% 
# mean accuracy threshold
session_means = output_data.groupby("session_id")[["hits", "accuracy"]].mean()
threshold = .5

# excluded sessions if accuracy is below threshold
bad_sessions = session_means.loc[session_means.accuracy<=threshold].index.to_list()

print("To exclude because of low performance: ", bad_sessions)
print("n exluded: ", len(bad_sessions))

# plot 
fig, (ax_box, ax_scatter) = plt.subplots(
    ncols=2, 
    figsize=(5, 6), 
    sharey=True,
    gridspec_kw={"width_ratios": [1, 5]},
    )

sns.boxplot(data=session_means, y="accuracy", ax=ax_box)
np.random.seed(420)
jitter = np.random.uniform(-0.3, 0.3, size=len(session_means))
ax_scatter.scatter(jitter, session_means["accuracy"], alpha=0.5)

# annotate the sessions to exclude
texts = []
for j, (session_id, row) in zip(jitter, session_means.iterrows()):
    if session_id in bad_sessions: 
        c = "red" if session_id in returned_sessions else "black" 
        ax_scatter.text(
            j, row["accuracy"], session_id, c=c, fontsize=4, ha="center", va="center")

ax_scatter.set_xlim(-0.5, 0.5)
ax_scatter.set_xticks([])  # hide x ticks
ax_scatter.set_ylabel("")
plt.tight_layout()


# %% 
# slow sessions
session_means = output_data.groupby("session_id")["rt"].median()
threshold = session_means.mean() + 2.5 * session_means.std()
slow_sessions = session_means[session_means > threshold].index.tolist()

print("To exclude because of slow reaction times: ", slow_sessions)
print("n exluded: ", len(slow_sessions))

# plot 
fig, (ax_box, ax_scatter) = plt.subplots(
    ncols=2, 
    figsize=(5, 6), 
    sharey=True,
    gridspec_kw={"width_ratios": [1, 5]},
    )

sns.boxplot(y=session_means, ax=ax_box)
np.random.seed(420)
jitter = np.random.uniform(-0.3, 0.3, size=len(session_means))
ax_scatter.scatter(jitter, session_means, alpha=0.5)

# annotate the sessions to exclude
texts = []
for j, (session_id, row) in zip(jitter, session_means.items()):
    if session_id in slow_sessions: 
        c = "red" if session_id in returned_sessions else "black" 
        ax_scatter.text(
            j, row, session_id, c=c, fontsize=4, ha="center", va="center")

ax_scatter.set_xlim(-0.5, 0.5)
ax_scatter.set_xticks([])  # hide x ticks
ax_scatter.set_ylabel("")
plt.tight_layout()

# %%
# save to json
out_dict = {
    "returned": sorted(returned_sessions),
    "low_quality_sessions": sorted(low_quality_sessions),
    "bad_session": sorted(bad_sessions),
    "slow_session": sorted(slow_sessions),
    "to_exclude": sorted(set(returned_sessions + low_quality_sessions + bad_sessions + slow_sessions))
}


print("Total to exclude:", len(out_dict["to_exclude"]), sep="\t")
print(json.dumps(out_dict, indent=4))

# %%
with open("./output_data/excluded_sessions/exclude_sessions_v1.json", "w") as f: 
    json.dump(out_dict, f, indent=4)

# %%
box = sns.boxplot(
    data=output_data.loc[~output_data.session_id.isin(out_dict["to_exclude"])], 
    x="time", 
    y="accuracy", 
    hue="condition_name", 
    native_scale=True,
    palette=colors_palette[:2],
    medianprops={'color': 'red', 'linewidth': 2},
    showmeans=True
    )
box.grid(alpha=.3)

# %%
