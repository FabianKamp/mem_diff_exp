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
colors_palette = ["#F2857D","#7EBDC3","#9ED9A3","#F5B971"]
sns.set_palette(colors_palette)

# set working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(script_dir))

save=False
# %% 
results_dir = "./results/v1_frequentist"
figures_dir = "./figures/v1_final"

# %%
# load data - visual vs. semantic
vs_data = pd.read_csv("./output_data/aggregated/aggregated_v1_vs.csv")
mixed_data = pd.read_csv("./output_data/aggregated/aggregated_v1_mixed.csv")

# exclude bad sessions
with open("./output_data/excluded_sessions/exclude_sessions_v1.json", "r") as file:
    excluded = json.load(file)["to_exclude"]

vs_data = vs_data.loc[~vs_data.session_id.isin(excluded)]
mixed_data = mixed_data.loc[~mixed_data.session_id.isin(excluded)]

print("n = ", vs_data.session_id.nunique())

# %%
# quick check - accuracy
box = sns.boxplot(
    data=vs_data, 
    x="time", 
    y="accuracy", 
    hue="condition_name", 
    native_scale=True,
    palette=colors_palette[:2],
    showmeans = True,
    medianprops={'color': 'red', 'linewidth': 2},
    meanprops={'marker': 'o', 'markerfacecolor': 'red', 'markeredgecolor': 'white'}
    )
box.grid(alpha=.3)
box.set_xticks([.4,2])
box.set_title("Visual vs Semantic Condition")

# %% 
# dprime plot 
outname = "dprime_visual_semantic"

sns.set_theme(style="whitegrid")
plt.figure(figsize=(6, 4))
bar = sns.barplot(
    data=vs_data, 
    x="time", 
    y="dprime", 
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
bar.set_ylabel("d'", fontsize=11)
bar.set_xticks([0.4, 2])
bar.set_xticklabels(["0.4", "2.0"])
bar.yaxis.grid(True, alpha=0.7)
bar.xaxis.grid(False)
bar.set_axisbelow(True)
bar.legend(frameon=True, fancybox=False, edgecolor="gray")
sns.despine()
plt.tight_layout()


plt.show()

# save 
if save: 
    plt.savefig(f"figures/v1_final/{outname}.pdf", bbox_inches="tight", facecolor="white")
    vs_data[["session_id", "time", "dprime", "condition_name"]].to_csv(f"figures/v1_final/{outname}.csv", index=False)


# %%
# test interaction
# set the order of conditions 
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
    dv='dprime', 
    within=['condition_name', 'encoding_time'],
    subject='session_id'
    )

# 2. Post-hoc pairwise comparisons with Cohen's d
posthocs = pg.pairwise_tests(
    data=vs_data, 
    dv='dprime',
    within=['condition_name', 'encoding_time'],
    subject='session_id',
    effsize='cohen'
    )

# 3. Save results
if save:
    rm_anova.to_csv(f'results/v1/{outname}_rm_anova.csv')
    posthocs.to_csv(f'results/v1/{outname}_posthocs.csv')

# %%
## difference of differences 
pivot_df = (vs_data
    .pivot(
        index="session_id", 
        columns=("condition_name", "encoding_time"), 
        values="dprime"
        )
    .assign(
        semantic_difference = lambda d: d[("semantic","long")]-d[("semantic","short")],
        visual_difference = lambda d: d[("visual","long")]-d[("visual","short")]
    )
    .assign(
        difference_of_differences = lambda d: d["semantic_difference"]-d["visual_difference"]
    )
)

fig, ax = plt.subplots()
sns.boxplot(
    data=pivot_df, 
    y="difference_of_differences",
    ax=ax,
    color="white"
)

sns.stripplot(
    data=pivot_df, 
    y="difference_of_differences",
    ax=ax,
    color=colors_palette[3]
)

ax.axhline(0, linestyle="--", color="k")

# model = smf.ols('difference_of_differences ~ 1', data=pivot_df).fit()
# print(model.summary())

# %% 
# mixed trials
plt.figure()
box = sns.boxplot(
    data=mixed_data, 
    x="time", 
    y="dprime", 
    # errorbar=("ci", 95),
    native_scale=True,
    color=colors_palette[2],
    )
box.set_xticks([.4,2])
box.set_title("Mixed Condition")

# %%
sns.set_theme(style="whitegrid")
outname_dc = "dprime_direct_comparison"

plt.figure(figsize=(6, 4))
bar = sns.barplot(
    data=mixed_data,
    x="time",
    y="dprime",
    errorbar=("ci", 95),
    native_scale=True,
    color=colors_palette[2],
    edgecolor="white",
    linewidth=1.5,
    width=0.8,
    capsize=0.1,
    err_kws={"linewidth": 1.5}
)

bar.set_xlabel("Encoding Time (s)", fontsize=11)
bar.set_ylabel("dprime", fontsize=11)
bar.set_xticks([0.4, 2])
bar.set_xticklabels(["0.4", "2.0"])
bar.set_ylim(-.2, 1.2)
bar.axhline(0, linestyle="--", color="k", alpha=0.5)
bar.yaxis.grid(True, alpha=0.7)
bar.xaxis.grid(False)

legend_elements = [Patch(facecolor=colors_palette[2], edgecolor='white', label='direct comparison')]
bar.legend(handles=legend_elements, frameon=True, fancybox=False, edgecolor="gray")
bar.set_axisbelow(True)

sns.despine()
plt.tight_layout()

# save 
plt.show()

if save:
    plt.savefig(f"figures/v1_final/{outname_dc}.pdf", bbox_inches="tight", facecolor="white")
# %%
# test difference in the mixed condition
mixed_data["time_condition"] = mixed_data.encoding_time.map({400:"short", 2000:"long"})


# same with scipy stats
cond1 = mixed_data[mixed_data['time_condition'] == 'short']['dprime']
cond2 = mixed_data[mixed_data['time_condition'] == 'long']['dprime']

ttest = pg.ttest(cond2, cond1, paired=True)
ttest.to_csv(f'results/v1/{outname_dc}_ttest.csv')


# %%

vs_data_c = vs_data[["accuracy", "dprime", "encoding_time", "condition_name", "condition", "session_id"]].rename(columns=dict(accuracy="p"))
mixed_data_c = mixed_data[["percent_semantic", "dprime", "encoding_time", "condition_name", "condition", "session_id"]].rename(columns=dict(percent_semantic="p"))

complete_data = pd.concat([vs_data_c, mixed_data_c]).pivot(index=["encoding_time", "session_id"], values="dprime", columns="condition_name").reset_index()
complete_data["predicted"] = complete_data["semantic"]- complete_data["visual"]
complete_data["observed"] = complete_data["mixed"]
complete_data["delta"] = complete_data["observed"] - complete_data["predicted"]


# %% 
# plotting

from scipy.stats import gaussian_kde
from matplotlib.patches import Polygon

fig, ax = plt.subplots(figsize=(7, 7))

encoding_times = sorted(complete_data["encoding_time"].unique())
palette = {encoding_times[0]: "#9ED9A3",
           encoding_times[1]: "#F5B971"}

sns.scatterplot(
    data=complete_data,
    x="predicted",
    y="observed",
    hue="encoding_time",
    palette=palette,
    ax=ax
)

ax.axline((0, 0), slope=1, color="gray", linestyle="--", linewidth=1, zorder=0)
lw = .6
ax.axline((0, 0.5), slope=1, color="gray", linestyle=":", linewidth=lw, zorder=0)
ax.axline((0, -0.5), slope=1, color="gray", linestyle=":", linewidth=lw, zorder=0)
ax.axline((0, -1.), slope=1, color="gray", linestyle=":", linewidth=lw, zorder=0)
ax.axline((0, 1.), slope=1, color="gray", linestyle=":", linewidth=lw, zorder=0)

lims = [min(ax.get_xlim()[0], ax.get_ylim()[0]),
        max(ax.get_xlim()[1], ax.get_ylim()[1])]
ax.set_xlim(lims)
ax.set_ylim(lims)
ax.set_aspect("equal", adjustable="box")

# KDE perpendicular to diagonal, split by encoding_time
center = (lims[0] + lims[1]) / 2 + (lims[1] - lims[0]) * 0.2  # shift toward upper right

for enc_time in encoding_times:
    delta = complete_data.loc[complete_data["encoding_time"] == enc_time, "delta"].dropna()
    kde = gaussian_kde(delta)
    delta_range = np.linspace(delta.min(), delta.max(), 200)
    density = kde(delta_range)
    density_scaled = density / density.max() * (lims[1] - lims[0]) * 0.15


    # Mark the mean
    mean_delta = delta.mean()
    mean_x = center - mean_delta / 2
    mean_y = center + mean_delta / 2
    ax.plot(mean_x, mean_y, marker=(2, 0, -45), color=palette[enc_time], markersize=12, markeredgewidth=2)

    # Build polygon coordinates
    x_base = center - delta_range / 2
    y_base = center + delta_range / 2
    x_density = x_base + density_scaled / np.sqrt(2)
    y_density = y_base + density_scaled / np.sqrt(2)

    poly_x = np.concatenate([x_base, x_density[::-1]])
    poly_y = np.concatenate([y_base, y_density[::-1]])
    polygon = Polygon(np.column_stack([poly_x, poly_y]),
                      facecolor="none", edgecolor=palette[enc_time], linewidth=1.5, zorder=10)
    ax.add_patch(polygon)


# %%
