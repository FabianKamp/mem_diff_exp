# %% 
# loading packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

import seaborn as sns
colors_palette = ["#F2857D","#7EBDC3","#9ED9A3","#F5B971"]
sns.set_palette(colors_palette)

# %%
# check cwd
if os.path.basename(os.getcwd()) == "analysis": 
    os.chdir("..")

# load data
output_data = pd.read_csv("./output_data/aggregated/aggregated_wm-vs.csv")

# quick check 
box = sns.boxplot(
    data=output_data, 
    x="bin_log_time", 
    y="accuracy", 
    hue="condition_name", 
    native_scale=True,
    palette=colors_palette[:2]
    )

# %% 
# mean accuracy threshold
session_means = output_data.groupby("session_id")[["hits", "accuracy"]].median()
threshold = 7

# plot 
fig, (ax_box, ax_scatter) = plt.subplots(
    ncols=2, 
    figsize=(5, 6), 
    sharey=True,
    gridspec_kw={"width_ratios": [1, 3]},
    )

sns.boxplot(data=session_means, y="hits", ax=ax_box)
np.random.seed(420)
jitter = np.random.uniform(-0.3, 0.3, size=len(session_means))
ax_scatter.scatter(jitter, session_means["hits"], alpha=0.7)

# annotate the sessions to exclude
excluded = session_means.loc[session_means.hits<=threshold]
print("To exclude: ", excluded.index.to_list())

texts = []
for j, (session_id, row) in zip(jitter, session_means.iterrows()):
    if row["hits"]>threshold: continue
    ax_scatter.text(j, row["hits"], session_id, fontsize=6)

ax_scatter.set_xlim(-0.5, 0.5)
ax_scatter.set_xticks([])  # hide x ticks
ax_scatter.set_ylabel("")
plt.tight_layout()
