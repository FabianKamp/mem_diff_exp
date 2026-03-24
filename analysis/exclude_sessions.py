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
# returned data
returned_sessions = [
    "M-PG-006-B"
]

# load data
output_data = pd.read_csv("./output_data/aggregated/aggregated_pilots.csv")

# quick check 
box = sns.boxplot(
    data=output_data, 
    x="bin_time_per_item", 
    y="accuracy", 
    hue="condition_name", 
    native_scale=True,
    palette=colors_palette[:2],
    medianprops={'color': 'red', 'linewidth': 2},
    )
box.grid(alpha=.3)
# %% 
# mean accuracy threshold
session_means = output_data.groupby("session_id")[["hits", "accuracy"]].median()
threshold = .6

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
excluded_sessions = session_means.loc[session_means.accuracy<=threshold].index.to_list()
excluded_sessions = (
    excluded_sessions + 
    [s for s in returned_sessions if s not in excluded_sessions]
)
print("To exclude: ", excluded_sessions)
print("n exluded: ", len(excluded_sessions))

texts = []
for j, (session_id, row) in zip(jitter, session_means.iterrows()):
    if session_id in excluded_sessions: 
        c = "red" if session_id in returned_sessions else "black" 
        ax_scatter.text(
            j, row["accuracy"], session_id, c=c, fontsize=4, ha="center", va="center")

ax_scatter.set_xlim(-0.5, 0.5)
ax_scatter.set_xticks([])  # hide x ticks
ax_scatter.set_ylabel("")
plt.tight_layout()

# %%
# save to json
excluded_dict = {
    "returned": sorted(returned_sessions),
    "excluded": sorted(excluded_sessions)
}
with open("./output_data/excluded_session.json", "w") as f: 
    json.dump(excluded_dict, f, indent=4)

# %%
box = sns.boxplot(
    data=output_data.loc[~output_data.session_id.isin(excluded_sessions)], 
    x="bin_time_per_item", 
    y="accuracy", 
    hue="condition_name", 
    native_scale=True,
    palette=colors_palette[:2],
    medianprops={'color': 'red', 'linewidth': 2},
    )
box.grid(alpha=.3)

# %%
