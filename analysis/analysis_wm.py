# %% 
# loading packages
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import pingouin as pg 
from matplotlib.patches import Patch
import seaborn as sns
from scipy.stats import pearsonr
from scipy.stats import ttest_1samp, ttest_rel
from scipy.stats import gaussian_kde
from matplotlib.patches import Polygon


# %%
# colors 
color_dict = {
    "semantic": "#EF5350", 
    "visual": "#26C6DA", 
    "mixed": "#76FF7A", 
    "difference": "#BDBDBD",
}

colors_palette = list(color_dict.values())
sns.set_palette(colors_palette)
sns.set_theme(style="ticks")

# %%
#  set directories
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(script_dir))

save=True
results_dir = "./results/v1_frequentist"
figures_dir = "./figures/v1_final"

# %%

def load_data():
    # load data - visual vs. semantic
    vs_data = pd.read_csv("./output_data/aggregated/aggregated_v1_vs.csv")
    mixed_data = pd.read_csv("./output_data/aggregated/aggregated_v1_mixed.csv")

    # exclude bad sessions
    with open("./output_data/excluded_sessions/exclude_sessions_v1.json", "r") as file:
        excluded = json.load(file)["to_exclude"]

    vs_data = vs_data.loc[~vs_data.session_id.isin(excluded)]
    mixed_data = mixed_data.loc[~mixed_data.session_id.isin(excluded)]

    # concat data files
    vs_data["p"] = vs_data["accuracy"]
    mixed_data["p"] = mixed_data["percent_semantic"]

    rel_cols = ["session_id", "time", "condition_name", "condition", "dprime", "p"]
    complete_data = pd.concat([vs_data[rel_cols], mixed_data[rel_cols]])

    complete_data = complete_data.assign(
        condition_name = pd.Categorical(
            complete_data.condition_name,
            categories=['visual', 'semantic', 'mixed'],  
            ordered=True
        ),
        encoding_time = pd.Categorical(
            complete_data.time.map({.4: "short", 2.: "long"}),
            categories=['short', 'long'],  
            ordered=True
        )
    )
    return complete_data

complete_data = load_data()
print("Total n = ", complete_data.session_id.nunique())

# %% 
# Test VISUAL vs SEMANTIC 
# 1. Repeated measures ANOVA
rm_anova = pg.rm_anova(
    data=complete_data.loc[complete_data.condition!=0], 
    dv='dprime', 
    within=['condition_name', 'encoding_time'],
    subject='session_id'
    )
print("\n##### ANOVA #####\n", rm_anova)

# 2. Post-hoc pairwise comparisons with Cohen's d
posthocs = pg.pairwise_tests(
    data=complete_data.loc[complete_data.condition!=0], 
    dv='dprime',
    within=['condition_name', 'encoding_time'],
    subject='session_id',
    effsize='cohen'
    )
print("\n##### POSTHOC #####\n", posthocs)

# 3. Save results
outname = "deprime_memory"
if save:
    rm_anova.to_csv(f'results/v1/{outname}_anova.csv')
    posthocs.to_csv(f'results/v1/{outname}_posthocs.csv')

# %%
# plot INTERACTION semantic and visual
plt.figure(figsize=(4,4))
point = sns.pointplot(
    data=complete_data.loc[complete_data.condition!=0], 
    x="time", 
    y="dprime", 
    hue="condition_name", 
    hue_order= ["semantic", "visual"],
    palette=color_dict,
    errorbar=("ci", 95),
    dodge=0.1,
    markers="o",
    linestyles="-",
    capsize=0.1,              # same as barplot
    err_kws={"linewidth": 1.5},  # same as barplot
    legend=False
)

point.set_ylim(bottom=0.2, top=1.2)
outname = "interaction_plot"

# save 
if save: 
    plt.savefig(f"figures/v1_final/{outname}.pdf", bbox_inches="tight", facecolor="white")
    complete_data.to_csv(f"figures/v1_final/{outname}.csv", index=False)

# %%
# test SEMANTIC vs DISTRACTOR / VISUAL
# 1. Repeated measures ANOVA
rm_anova = pg.rm_anova(
    data=complete_data.loc[complete_data.condition_name!="visual"], 
    dv='dprime', 
    within=['condition_name', 'encoding_time'],
    subject='session_id'
    )
print("\n##### ANOVA #####\n", rm_anova)

# 2. Post-hoc pairwise comparisons with Cohen's d
posthocs = pg.pairwise_tests(
    data=complete_data.loc[complete_data.condition_name!="visual"], 
    dv='dprime',
    within=['condition_name', 'encoding_time'],
    subject='session_id',
    effsize='cohen'
    )
print("\n##### POSTHOC #####\n", posthocs)

# 3. Save results
outname = "deprime_semantic_memory"
if save:
    rm_anova.to_csv(f'results/v1/{outname}_anova.csv')
    posthocs.to_csv(f'results/v1/{outname}_posthocs.csv')

# %%
# plot SEMANTIC MAIN effect
plt.figure(figsize=(4,4))
point = sns.pointplot(
    data=complete_data.loc[complete_data.condition_name!="visual"], 
    x="time", 
    y="dprime", 
    hue="condition_name", 
    hue_order= ["semantic", "mixed"],
    palette=color_dict,
    errorbar=("ci", 95),
    dodge=0.1,
    markers="o",
    linestyles="-",
    capsize=0,             
    err_kws={"linewidth": 2},
    legend=False
)

point.set_ylim(bottom=-0.2, top=1.2)
outname = "semantic_plot"

save = True 
if save: 
    plt.savefig(f"figures/v1_final/{outname}.pdf", bbox_inches="tight", facecolor="white")

# %% 
# TEST ADDITIVITY
additivity_data_wide = complete_data.pivot(
    index=["encoding_time", "time", "session_id"], 
    values="dprime", 
    columns="condition_name"
    ).reset_index()

additivity_data_wide["difference"] = additivity_data_wide["semantic"] - additivity_data_wide["visual"]

additivity_data = additivity_data_wide.melt(
    id_vars=["encoding_time", "time", "session_id"], 
    value_vars=["difference", "mixed"], 
    value_name="dprime"
    )

# test SEMANTIC vs DISTRACTOR / VISUAL
# 1. Repeated measures ANOVA
rm_anova = pg.rm_anova(
    data=additivity_data, 
    dv='dprime', 
    within=['condition_name', 'encoding_time'],
    subject='session_id'
    )
print("\n##### ANOVA #####\n", rm_anova)

# 2. Post-hoc pairwise comparisons with Cohen's d
posthocs = pg.pairwise_tests(
    data=additivity_data,
    dv='dprime',
    within=['condition_name', 'encoding_time'],
    subject='session_id',
    effsize='cohen'
    )
print("\n##### POSTHOC #####\n", posthocs)

# 3. Save results
outname = "deprime_additivity"
if save:
    rm_anova.to_csv(f'results/v1/{outname}_anova.csv')
    posthocs.to_csv(f'results/v1/{outname}_posthocs.csv')

# 4. plot
plt.figure(figsize=(4,4))
point = sns.pointplot(
    data=additivity_data,
    x="time", 
    y="dprime", 
    hue="condition_name", 
    palette=color_dict,
    errorbar=("ci", 95),
    dodge=0.1,
    markers="o",
    linestyles="-",
    capsize=0,              
    err_kws={"linewidth": 2},  
    legend=False
)

# %%
# regressing the direct dprime on the other two
# Multiple regression: observed ~ semantic + visual + intercept 
# the intercept is basically accounting for the bias
import statsmodels.formula.api as smf

additivity_agg = additivity_data_wide.groupby("session_id")[["semantic", "visual", "mixed", "difference"]].mean().reset_index()
model = smf.ols("mixed ~ semantic + visual", data=additivity_agg).fit()
print(model.summary())

# Marginal effects plots
fig, ax = plt.subplot_mosaic("MVS", figsize=(12,4), sharey=True)

x_lims = [-1.,1.5]
additivity_agg["error"] = additivity_agg["mixed"] - additivity_agg["difference"]
ax["M"].scatter(
    additivity_agg["difference"], 
    additivity_agg["mixed"], 
    c=color_dict["mixed"], 
    edgecolor="k", 
    linewidth=.1, 
    s=100
    )

sns.kdeplot(
    x=additivity_agg["difference"],
    y=additivity_agg["mixed"],
    ax=ax["M"],
    levels=4,           # number of contour levels
    color="black",      # or use cmap="Blues" for filled
    linewidths=1,
    alpha=0.3,
    thresh=0.2,
    bw_adjust=1.5,
    zorder=0
)

ax["M"].axline(
    (0, 0), 
    slope=1, 
    color="k", 
    alpha=0.3, 
    linestyle="--", 
    linewidth=.8, 
    zorder=0
)

ax["M"].set_xlim(*x_lims)
ax["M"].set_ylim(*x_lims)

ax["M"].scatter(
    additivity_agg["difference"].mean(), 
    additivity_agg["mixed"].mean(), 
    c='k', 
    s=100,
    marker='x'
    )


for i, var1 in zip("VS", ["semantic", "visual"]):
    var2 = "visual" if var1 == "semantic" else "semantic"

    x_range = np.linspace(additivity_agg[var1].min(),additivity_agg[var1].max(), 100)
    pred_data = pd.DataFrame({var1: x_range, var2: additivity_agg[var2].mean()})
    pred_data["predicted"] = model.predict(pred_data)

    ax[i].scatter(
        additivity_agg[var1], 
        additivity_agg["mixed"], 
        c=color_dict[var1], 
        edgecolor="k", 
        linewidth=.1, 
        s=100
    )
    ax[i].plot(
        x_range, 
        pred_data["predicted"], 
        color=color_dict[var1], 
        linewidth=3, 
    )

    ax[i].set_xlabel(f"dprime_{var1}")

plt.tight_layout()


save = True
outname = "additivity_plot"
if save: 
    plt.savefig(f"figures/v1_final/{outname}.pdf", bbox_inches="tight", facecolor="white")

# %%
