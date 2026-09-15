# %% 
# loading packages
import os
import json
import itertools 
import numpy as np
import pandas as pd
import pymc as pm
import matplotlib.pyplot as plt
import arviz as az
import statsmodels.formula.api as smf
from scipy.stats import ttest_rel
from scipy.stats import norm
import pingouin as pg 
import seaborn as sns

# %%

# colors 
color_dict = {
    "semantic": "#EF5350", 
    "visual": "#26C6DA", 
    "mixed": "#76FF7A", 
    "other": "#1A1A1A",
    "short": "#AB47BC",
    "long": "#FF9800",

}

colors_palette = list(color_dict.values())
sns.set_palette(colors_palette)
sns.set_theme(style="ticks")

# %%
#  set directories

# set working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(script_dir))
save = False

# %%
# load data - long term data
lm_data = pd.read_csv("./output_data/aggregated/aggregated_v1_lm.csv")

# load excluded sessions
with open("./output_data/excluded_sessions/exclude_sessions_v1.json", "r") as file:
    excluded = json.load(file)["to_exclude"]

lm_data = lm_data.loc[~lm_data.session_id.isin(excluded)]
print("n = ", lm_data.session_id.nunique())

lm_data["wm_test_condition"] = lm_data["condition_name"]
lm_data["wm_test_condition"] = lm_data["wm_test_condition"].replace("mixed", "not_tested")

lm_data = lm_data.assign(
    wm_test_condition = pd.Categorical(
        lm_data.wm_test_condition,
        categories=['not_tested', 'visual', 'semantic'],  
        ordered=True
    ),
    encoding_time = pd.Categorical(
        lm_data["time"].map({.4: "short", 2.: "long"}),
        categories=['short', 'long'],  
        ordered=True
    )
)

# %%
# condition difference
box = sns.boxplot(
    data=lm_data, 
    x="time", 
    y="accuracy", 
    hue="condition_name", 
    native_scale=True,
    showmeans = True,
    palette=colors_palette[:3],
    medianprops={'color': 'red', 'linewidth': 2},
    meanprops={'marker': 'o', 'markerfacecolor': 'red', 'markeredgecolor': 'white'}
    )
box.grid(alpha=.3)
box.set_xticks([.4,2])

# %%
# last point plot

sns.set_theme(style="ticks")
plt.figure(figsize=(6, 6))
bar = sns.pointplot(
    data=lm_data, 
    x="wm_test_condition", 
    y="dprime", 
    hue="time", 
    native_scale=True,
    palette=colors_palette[4:],
    errorbar=("ci", 95),
    dodge=0.1,
    markers="o",
    linestyles="-",
    capsize=0.1,              # same as barplot
    legend=False
)

bar.set_xlabel("Encoding Time (s)", fontsize=11)
bar.set_ylabel("d'", fontsize=11)

bar.yaxis.grid(False)
bar.xaxis.grid(False)

plt.tight_layout()

save = True
outname = "dprime_lm"
if save:
    plt.savefig(f"figures/v1_final/{outname}.pdf", bbox_inches="tight")
    lm_data[["session_id", "time", "dprime", "wm_test_condition"]].to_csv(f"figures/v1_final/{outname}.csv", index=False)

# %% 
# 1. Repeated measures ANOVA
rm_anova = pg.rm_anova(
    data=lm_data, 
    dv='dprime', 
    within=['wm_test_condition', 'encoding_time'],
    subject='session_id'
    )
print(rm_anova)

# 2. Post-hoc pairwise comparisons with Cohen's d
posthocs = pg.pairwise_tests(
    data=lm_data, 
    dv='dprime',
    within=['wm_test_condition', 'encoding_time'],
    subject='session_id',
    effsize='cohen'
    )
print(posthocs)

# 3. Save results
if save: 
    rm_anova.to_csv(f'results/v1/{outname}_rm_anova.csv')
    posthocs.to_csv(f'results/v1/{outname}_posthocs.csv')

# %% 
# residual plot 
res_df = pd.read_csv("./figures/v1_final/lm_residuals.csv")

fig, (a,b) = plt.subplots(1,2,figsize=(6,4), sharex=True, sharey=True)
sns.regplot(
    data=res_df, 
    x="resid_semantic",
    y="resid_lm_visual", 
    color=colors_palette[1],
    ax=a
)

sns.regplot(
    data=res_df, 
    x="resid_visual",
    y="resid_lm_semantic", 
    color=colors_palette[2],
    ax=b
)
# %%
# trial by trial predictions

# Load data
long_data = pd.read_csv("./output_data/long/combined_data.csv")
long_data = long_data[~long_data["session_id"].isin(excluded)]

# Summary for plotting
lm_by_wm_accuracy = (
    long_data
    .query("condition_name != 'mixed'")
    .dropna(subset=["correct_wm"])
    .groupby(["session_id", "condition_name", "correct_wm"], as_index=False)
    .agg(correct_lm=("correct_lm", "mean"))
)

# Set condition order
lm_by_wm_accuracy["condition_name"] = pd.Categorical(
    lm_by_wm_accuracy["condition_name"], 
    categories=["visual", "semantic"]
)

# Plot
palette = {"semantic": "#EF5350", "visual": "#26C6DA"}
fig = plt.figure(figsize=(6,6))
point = sns.pointplot(
    data=lm_by_wm_accuracy,
    x="correct_wm",
    y="correct_lm",
    hue="condition_name",
    palette=palette,
    errorbar=("ci", 95),
    dodge=0.1,
    markers="o",
    linestyles="-",
    capsize=0.1,              # same as barplot
    legend=False
)
point.set_ylim(0.5, None)
point.set_yticks(np.arange(.5,.9,.1))

save = True
outname = "correct_lm_trials"
if save:
    plt.savefig(f"figures/v1_final/{outname}.pdf", bbox_inches="tight")
# %%

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load excluded sessions
with open("./output_data/excluded_sessions/exclude_sessions_v1.json") as f:
    excluded = json.load(f)["to_exclude"]

# Load data
long_data = pd.read_csv("./output_data/long/combined_data.csv")
long_data = long_data[~long_data["session_id"].isin(excluded)]

# Summary for plotting
lm_by_wm_accuracy = (
    long_data
    .query("condition_name != 'mixed'")
    .dropna(subset=["correct_wm"])
    .groupby(["session_id", "condition_name", "correct_wm"], as_index=False)
    .agg(correct_lm=("correct_lm", "mean"))
)

# Set condition order
lm_by_wm_accuracy["condition_name"] = pd.Categorical(
    lm_by_wm_accuracy["condition_name"], 
    categories=["visual", "semantic"]
)

# Plot
palette = {"semantic": "#EF5350", "visual": "#26C6DA"}
sns.boxplot(
    data=lm_by_wm_accuracy,
    x="condition_name",
    y="correct_lm",
    hue="correct_wm",
    palette=palette.values()
)

save = True
outname = "correct_lm_trials"
if save:
    plt.savefig(f"figures/v1_final/{outname}.pdf", bbox_inches="tight")


# %%
