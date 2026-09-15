# %% 
# loading packages
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from scipy.stats import ttest_rel
import pingouin as pg 


import seaborn as sns
colors_palette = ["#F2857D","#7EBDC3","#9ED9A3","#F5B971"]
sns.set_palette(colors_palette)

# set working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(script_dir))

# %%
vs_data = pd.read_csv("./output_data/aggregated/aggregated_v1_vs.csv")
mixed_data = pd.read_csv("./output_data/aggregated/aggregated_v1_mixed.csv")

# exclude bad sessions
with open("./output_data/excluded_sessions/exclude_sessions_v1.json", "r") as file:
    excluded = json.load(file)["to_exclude"]

vs_data = vs_data.loc[~vs_data.session_id.isin(excluded)]

mixed_data = mixed_data.loc[~mixed_data.session_id.isin(excluded)]
mixed_data = mixed_data.melt(
    id_vars=["session_id", "time"], 
    value_vars=["rt_semantic_thresh", "rt_visual_thresh"], 
    value_name="reaction_time_thresh", 
    var_name="response"
    )
mixed_data["response"] = mixed_data.response.str.split('_').str[1]


# %%
# quick check 
plt.figure()
sns.boxplot(
    data=vs_data, 
    x="time",
    y="rt_hit_median", 
    hue="condition_name",
    palette=colors_palette[:2]
)
plt.title("Median Time")

# %%
# fig, ax = plt.subplots()
# sns.barplot(
#     data=vs_data,
#     x="time",
#     y="rt_hit_thresh",
#     hue="condition_name",
#     palette=colors_palette[:2],
#     ax=ax
# )
# ax.set_ylim(500, None)
# plt.title("Median Time Thresholded")

outname = "rt_visual_semantic"
sns.set_theme(style="whitegrid")
plt.figure(figsize=(6, 4))
bar = sns.barplot(
    data=vs_data, 
    x="time", 
    y="rt_hit_thresh", 
    hue="condition_name", 
    native_scale=True,
    palette=colors_palette[:2],
    errorbar=("ci", 95),
    edgecolor="white",
    linewidth=1.5,
    width=0.8,
    capsize=0.1,          # adds caps to error bars
    err_kws={"linewidth": 1.5}
)

bar.set_xlabel("Encoding Time (s)", fontsize=11)
bar.set_ylabel("Reaction Time [hits]", fontsize=11)
bar.set_xticks([0.4, 2])
bar.set_xticklabels(["0.4", "2.0"])
bar.yaxis.grid(True, alpha=0.7)
bar.xaxis.grid(False)
bar.set_axisbelow(True)
bar.legend(frameon=True, fancybox=False, edgecolor="gray")
bar.set_ylim(600, 2000)

sns.despine()
plt.tight_layout()

# save figure
plt.savefig(f"figures/v1_final/{outname}.pdf", bbox_inches="tight", facecolor="white")
plt.show()

# save data
vs_data[["session_id", "time", "rt_hit_thresh", "condition_name"]].to_csv(f"figures/v1_final/{outname}.csv", index=False)


# %%
import scipy.stats as stats
vs_data = vs_data.assign(
    condition_name = pd.Categorical(
        vs_data.condition_name,
        categories=['visual', 'semantic'],  
        ordered=True
    ),
    encoding_time = pd.Categorical(
        vs_data["time"].map({.4: "short", 2.: "long"}),
        categories=['short', 'long'],  
        ordered=True
    )
)

# %% 
# 1. Repeated measures ANOVA
rm_anova = pg.rm_anova(
    data=vs_data, 
    dv='rt_hit_thresh', 
    within=['condition_name', 'encoding_time'],
    subject='session_id'
    )

# 2. Post-hoc pairwise comparisons with Cohen's d
posthocs = pg.pairwise_tests(
    data=vs_data, 
    dv='rt_hit_thresh',
    within=['condition_name', 'encoding_time'],
    subject='session_id',
    effsize='cohen'
    )

# 3. Save results
rm_anova.to_csv(f'results/v1/{outname}_rm_anova.csv')
posthocs.to_csv(f'results/v1/{outname}_posthocs.csv')


#%% MIXED
outname = "rt_direct_comparison"

mixed_data = mixed_data.assign(
    response = pd.Categorical(
        mixed_data.response,
        categories=['visual', 'semantic'],  
        ordered=True
    ),
    encoding_time = pd.Categorical(
        mixed_data["time"].map({.4: "short", 2.: "long"}),
        categories=['short', 'long'],  
        ordered=True
    )
)

plt.figure()
sns.boxplot(
    data=mixed_data, 
    x="time",
    y="reaction_time_thresh", 
    hue="response",
    palette=colors_palette[:2]
)
plt.title("Mixed condition")

# %%
sns.set_theme(style="whitegrid")
plt.figure(figsize=(6, 4))
bar = sns.barplot(
    data=mixed_data, 
    x="time", 
    y="reaction_time_thresh", 
    hue="response", 
    native_scale=True,
    palette=colors_palette[:2],
    errorbar=("ci", 95),
    edgecolor="white",
    linewidth=1.5,
    width=0.8,
    capsize=0.1,          # adds caps to error bars
    err_kws={"linewidth": 1.5}
)

bar.set_xlabel("Encoding Time (s)", fontsize=11)
bar.set_ylabel("Reaction Time", fontsize=11)
bar.set_xticks([0.4, 2])
bar.set_xticklabels(["0.4", "2.0"])
bar.yaxis.grid(True, alpha=0.7)
bar.xaxis.grid(False)
bar.set_axisbelow(True)
bar.legend(title="Response", frameon=True, fancybox=False, edgecolor="gray")
bar.set_ylim(600, 2000)

sns.despine()
plt.tight_layout()

# save figure
plt.savefig(f"figures/v1_final/{outname}.pdf", bbox_inches="tight", facecolor="white")
plt.show()

# save data
mixed_data[["session_id", "time", "reaction_time_thresh", "response"]].to_csv(f"figures/v1_final/{outname}.csv", index=False)


#%%

# 1. Repeated measures ANOVA
rm_anova = pg.rm_anova(
    data=mixed_data, 
    dv='reaction_time_thresh', 
    within=['response', 'encoding_time'],
    subject='session_id'
    )

# 2. Post-hoc pairwise comparisons with Cohen's d
posthocs = pg.pairwise_tests(
    data=mixed_data, 
    dv='reaction_time_thresh',
    within=['response', 'encoding_time'],
    subject='session_id',
    effsize='cohen'
    )

# 3. Save results
rm_anova.to_csv(f'results/v1/{outname}_rm_anova.csv')
posthocs.to_csv(f'results/v1/{outname}_posthocs.csv')

# %%
# test difference in the mixed condition
mixed_data["time_condition"] = mixed_data.encoding_time.map({400:"short", 2000:"long"})
mixed_data["rt_diff"] = mixed_data.rt_semantic - mixed_data.rt_visual

model = smf.ols('rt_diff ~ 1', data=mixed_data).fit()
print(model.summary())

# same with scipy stats
cond1 = mixed_data['rt_semantic']
cond2 = mixed_data['rt_visual']

t_stat, p_value = ttest_rel(cond2, cond1)
print(f"t = {t_stat:.3f}, p = {p_value:.4f}")
# %%
