# %% 
# loading packages
import os
import json
import numpy as np
import pandas as pd
from itertools import product
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
# general model configuration
n_trials_per_condition = 13

session_labels = output_data.session_id.unique()
session_map = {s: i for i,s in enumerate(session_labels)}
condition_map = {"visual": 0 , "semantic":1}

output_data = (output_data.assign(
    sid = output_data.session_id.map(session_map).astype("Int64"),
    cid = output_data.condition_name.map(condition_map).astype("Int64"),
    hits = output_data.hits.astype("Int64"),
    ))

coords = {
    "session": session_labels,
    "condition": ["visual", "semantic"],
    "obs": range(len(output_data)),
}

idata = dict()
# %%
# partially pooled (multilevel model)
with pm.Model(coords=coords) as pp_model:
    # index variables
    sid  = pm.Data('sid',  output_data['sid'].values, dims="obs")
    cid  = pm.Data('cid',  output_data['cid'].values, dims="obs")
    time = pm.Data('time', output_data['time'].values, dims="obs")

    # t (reparameterized for multilevel)
    t_bar = pm.Normal('t_bar', 1., .2)
    t_sigma = pm.Exponential('t_sigma', 1.)
    t_z = pm.Normal('t_z', 0., 1., dims="session")
    t = pm.Deterministic('t', t_bar + t_z * t_sigma, dims="session")

    # slopes
    beta = pm.LogNormal('beta', mu=0, sigma=1, dims="condition")

    # guess rate
    g = .5

    # lapse rate         
    l = pm.Beta('l', alpha=2, beta=48)
    
    p = pm.Deterministic('p', g + (1-g-l) * pm.math.invlogit(beta[cid] * (time - t[sid])), dims="obs")
    y = pm.Binomial('y', p=p, n=n_trials_per_condition, observed=output_data['hits'].values, dims="obs")

    # sample
    idata["partial_pooling"] = pm.sample(nuts_sampler="numpyro", draws=2000)

# %%
# plot multilevel model
model_key = "partial_pooling"
fig, axes = plt.subplots(1,2, figsize=(10,6))

# threshold
az.plot_forest(
    idata[model_key].posterior, 
    var_names=["t"],
    combined=True, 
    colors="k",
    ax=axes[0]
)

# show the median
t_median = idata[model_key].posterior.t.mean(["chain", "draw"]).median(dim="session")
print(t_median)
axes[0].axvline(t_median, c="k", alpha=.5)
axes[0].set_xticks(range(-3,5))

## beta
az.plot_forest(
    idata[model_key], 
    var_names=["beta"],
    combined=True, 
    kind="ridgeplot",
    ridgeplot_quantiles=[.25, .5, .75],
    ridgeplot_overlap=0.7,
    ridgeplot_truncate=False,
    colors='white',
    ax = axes[1]
)

# %%
# %%
# posterior predicitive -- partially pooled (cp)
ppc_times = np.linspace(0,2.5,20)

posterior_input = product(ppc_times, condition_map.values(), session_map.values())
posterior_input = np.array(list(posterior_input))

post_coords = {
    "session": session_labels,
    "condition": ["visual", "semantic"],
    "obs": range(len(posterior_input)),
}

with pp_model:
    # set data
    pm.set_data(
        dict(
            time = posterior_input[:,0].flatten(), 
            cid = posterior_input[:,1].astype(int), 
            sid = posterior_input[:,2].astype(int)
            ), 
        coords=post_coords
        )
    
    # predict
    predictions = pm.sample_posterior_predictive(
        idata["partial_pooling"].sel(draw=slice(None, None, 5)), 
        var_names=["p"],
        predictions=True
    ).predictions.p.stack(sample=("chain","draw"))

mean_predictions = np.mean(predictions, axis=1)
posterior_out = pd.DataFrame(posterior_input, columns=["time", "cid", "sid"])
posterior_out["mean_prediction"] = mean_predictions

inverted_smap = {v: k for k, v in session_map.items()}
inverted_cmap = {v: k for k, v in condition_map.items()}
posterior_out["session"] = posterior_out.sid.map(inverted_smap)
posterior_out["condition"] = posterior_out.cid.map(inverted_cmap)

# plot

g = sns.FacetGrid(posterior_out, col="session", hue="condition", col_wrap=5)
g.map(sns.lineplot, "time", "mean_prediction")
g.set_titles("{col_name}")
g.add_legend()

# %%
