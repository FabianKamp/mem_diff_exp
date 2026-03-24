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

import seaborn as sns
colors_palette = ["#F2857D","#7EBDC3","#9ED9A3","#F5B971"]
sns.set_palette(colors_palette)
# set working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(script_dir))
# %%
# load data
output_data = pd.read_csv("./output_data/aggregated/aggregated_pilots.csv")

# exclude bad sessions
with open("./output_data/excluded_session.json", "r") as file:
    excluded = json.load(file)["excluded"]
output_data = output_data.loc[~output_data.session_id.isin(excluded)]

# filter for load
# output_data = output_data.loc[output_data.load==4]

# %%
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
# plotting functions
def plot_posterior_predictions(ppc_times, predictions): 
    fig, ax = plt.subplots(figsize=(6,4))
    ax.fill_between(
        ppc_times,
        np.percentile(predictions["semantic"], 5, axis=1),
        np.percentile(predictions["semantic"], 95, axis=1),
        color=colors_palette[0],
        alpha=0.3
    )
    ax.fill_between(
        ppc_times,
        np.percentile(predictions["visual"], 5, axis=1),
        np.percentile(predictions["visual"], 95, axis=1),
        color=colors_palette[1],
        alpha=0.3
    )

    ax.plot(ppc_times, predictions["semantic"].mean("sample"), label="semantic", linewidth=3, c=colors_palette[0]);
    ax.plot(ppc_times, predictions["visual"].mean("sample"), label="visual", linewidth=3, c=colors_palette[1]);
    ax.legend()
    return fig

def forest_plot(idata):
    fig, ax = plt.subplots(figsize=(6,3))
    az.plot_forest(
        idata, 
        var_names=["t", "beta"],
        combined=True, 
        # kind="ridgeplot",
        ridgeplot_quantiles=[.25, .5, .75],
        ridgeplot_overlap=0.3,
        ridgeplot_truncate=False,
        colors='black',
        ax=ax
    )
    return fig

# %%
# multilevel
# separat models for pilots with load=3 and load=4

n_trials_per_condition = 13
session_labels = output_data.session_id.unique()
session_map = {s: i for i,s in enumerate(session_labels)}
condition_map = {"visual": 0 , "semantic":1}
load_map = {3: 0, 4:1}

output_data = (output_data.assign(
    cid = output_data.condition_name.map(condition_map).astype("Int64"),
    lid = output_data.load.map(load_map).astype("Int64"),
    hits = output_data.hits.astype("Int64"),
    ))

coords = {
    "load": [3,4],
    "condition": ["visual", "semantic"],
    "obs": range(len(output_data)),
}

idata = dict()

# partially pooled (multilevel model)
with pm.Model(coords=coords) as pp_model:
    # index variables
    lid = pm.Data('lid', output_data['lid'].values.astype('int64'), dims="obs")
    cid = pm.Data('cid', output_data['cid'].values.astype('int64'), dims="obs")
    time = pm.Data('time', output_data['time_per_item'].values, dims="obs")

    # hyperpriors 
    t_bar = pm.Normal('t_bar', mu=.5, sigma=.1, dims="condition")
    t_sigma = pm.Exponential('t_sigma', 1., dims="condition")
    t_z = pm.Normal('t_z', 0., 1., dims=("load", "condition"))
    t = pm.Deterministic('t', t_bar + t_z * t_sigma, dims=("load", "condition"))

    # slopes
    beta = pm.LogNormal('beta', mu=0, sigma=1, dims="condition")

    # guess rate
    g = .5

    # lapse rate         
    l = pm.Beta('l', alpha=2, beta=48)
    
    # p = pm.Deterministic('p', g + (1-g-l) * pm.math.invlogit(beta[cid] * pm.math.log(time/t[lid,cid])), dims="obs")
    p = pm.Deterministic('p', g + (1-g-l) * pm.math.invlogit(beta[cid] * (time - t[lid,cid])), dims="obs")
    y = pm.Binomial('y', p=p, n=n_trials_per_condition, observed=output_data['hits'].values, dims="obs")

    # sample
    idata["partial_pooling"] = pm.sample(
        nuts_sampler="numpyro", 
        draws=2000,
        target_accept=0.99
        )

# %%
# posterior predicitive -- partial pooling (pp)
ppc_n = 50
ppc_times = np.linspace(1e-1,.7,ppc_n)

predictions = dict()
for cname, cid in condition_map.items():
    with pp_model:
        pm.set_data(
            dict(
                time = ppc_times, 
                cid = np.repeat(cid,ppc_n),
                lid = np.repeat(1, ppc_n).astype("int64") # load = 4
                ), 
            coords={"obs": range(ppc_n)}
        )

        predictions[cname] = pm.sample_posterior_predictive(
            idata["partial_pooling"].sel(draw=slice(None, None, 5)), 
            var_names=["p"],
            predictions=True
        ).predictions.p.stack(sample=("chain","draw"))

# plot native scale 
plot_posterior_predictions(ppc_times, predictions)
forest_plot(idata["partial_pooling"])

# %%
# contrast 
contrast = predictions["visual"]-predictions["semantic"]
fig, ax = plt.subplots(figsize=(6,4))
ax.fill_between(
    ppc_times,
    np.percentile(contrast, 5, axis=1),
    np.percentile(contrast, 95, axis=1),
    color=colors_palette[0],
    alpha=0.3
)

ax.plot(
    ppc_times, 
    contrast.mean("sample"), 
    label="mean difference", 
    linewidth=3, 
    c=colors_palette[0], 
);
ax.legend()
# %%
# facet grid
n = 5
fig, ax = plt.subplots(
    n, n, 
    sharex=True,
    sharey=True,
    figsize=(10,10)
    )

idx = np.linspace(0,49,n+1).astype(int)
bin_width = 0.005
bins = np.arange(-.05, .08 + bin_width, bin_width)

for i in range(n): 
    for j in range(n):
        effect = contrast[idx[i]] - contrast[idx[j]]
        
        if i!=j:
            ax[i, j].hist(effect, bins)
            ax[i, j].axvline(np.percentile(effect, 25), color='black', linestyle='--', linewidth=1)
            ax[i, j].axvline(np.percentile(effect, 50), color='red', linestyle='--', linewidth=1)

        if i==0:
            ax[i,j].set_title(f"Stop {np.round(ppc_times[idx[j]],2)}")
        if j==0:
            ax[i,j].set_ylabel(f"Start {np.round(ppc_times[idx[i]],2)}")

plt.tight_layout()
# %%
