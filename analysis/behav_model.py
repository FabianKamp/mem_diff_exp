# %% 
# loading packages
import pandas as pd
import numpy as np
from itertools import product
import pymc as pm
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns
from tqdm.notebook import tqdm
import arviz as az
import os
colors_palette = ["#F2857D","#7EBDC3","#9ED9A3","#F5B971"]
sns.set_palette(colors_palette)

# %% 
# load data
# define exclusion criteria
d_excluded = [8]
e_excluded = [5,6]

session_ids = {
    "M-PD": list(set(range(1,12))-set(d_excluded)),
    "M-PE": list(set(range(1,12))-set(e_excluded))
}

if os.path.basename(os.getcwd()) == "analysis": 
    os.chdir("..")

out_files = [f"./output_data/{wave_code}/{wave_code}-{i:03d}-{suffix}.csv" 
             for wave_code in session_ids.keys()
             for i in session_ids[wave_code] 
             for suffix in "ABCD" 
             ]

out_files = filter(os.path.exists, out_files)
all_data = []
for file in out_files: 
    # print(file)
    data = pd.read_csv(file)   
    all_data.append(data)

all_data = pd.concat(all_data) 

#%% 
# preprocess working memory data
output_data = all_data.loc[
    (all_data.trial_type=='wm') & 
    (all_data.condition_name!='mixed') & 
    (all_data.phase == "recognition") 
    ].copy()
print("NA responses: ", np.sum(output_data.response.isna()))

output_data.response = output_data.response.astype("Int64")
output_data.correct_response = output_data.correct_response.astype("Int64")

output_data["correct"] = (output_data.response == output_data.correct_response)
output_data["time"] = output_data.encoding_time/1e3

# aggregate
output_data = (output_data
    .groupby(["session_id", "condition", "condition_name", "time"])
    .agg(
        hits = ("correct", "sum"),
        responses = ("correct", "count"),
        accuracy = ("correct", "mean")
    )
    .reset_index()
    .assign(log_time = lambda d: np.log(d["time"]))
)

box = sns.boxplot(
    data=output_data, 
    x="time", 
    y="accuracy", 
    hue="condition_name", 
    native_scale=True,
    width=.5, 
    palette=colors_palette[:2]
    )
box.grid(alpha=.1)

fig = plt.figure()
box = sns.boxplot(
    data=output_data, 
    x="log_time", 
    y="accuracy", 
    hue="condition_name", 
    native_scale=True,
    width=.5, 
    palette=colors_palette[:2]
    )
box.grid(alpha=.1)


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
# complete pooled (cp)
with pm.Model(coords=coords) as cp_model:
    # index variables
    cid  = pm.Data('cid',  output_data['cid'].values, dims="obs")
    time = pm.Data('time', output_data['time'].values, dims="obs")

    # threshold
    t = pm.Normal('t', mu=1., sigma=.5)

    # slopes
    beta = pm.LogNormal('beta', mu=0, sigma=1, dims="condition")

    # guess rate
    g = .5

    # lapse rate         
    l = pm.Beta('l', alpha=2, beta=48)
    
    p = pm.Deterministic('p', g + (1-g-l) * pm.math.invlogit(beta[cid] * (time - t)), dims="obs")
    y = pm.Binomial('y', p=p, n=n_trials_per_condition, observed=output_data['hits'].values, dims="obs")
    idata["complete_pooling"] = pm.sample(nuts_sampler="numpyro", draws=2000, target_accept=0.95)

# %%
# posterior predicitive -- complete pooled (cp)
ppc_times = np.linspace(-1,3,20)
predictions = dict()
for cname, cid in condition_map.items():
    with cp_model:
        pm.set_data(
            dict(time = ppc_times, cid = np.repeat(cid,20)), 
            coords={"obs": range(20)}
        )
        predictions[cname] = pm.sample_posterior_predictive(
            idata["complete_pooling"].sel(draw=slice(None, None, 5)), 
            var_names=["p"],
            predictions=True
        ).predictions.p.stack(sample=("chain","draw"))

fig, ax = plt.subplots()
ax.plot(ppc_times, predictions["semantic"], c=colors_palette[0], alpha=.01);
ax.plot(ppc_times, predictions["visual"], c=colors_palette[1], alpha=.01);
ax.plot(ppc_times, predictions["semantic"].mean("sample"), label="semantic", linewidth=3, c=colors_palette[0]);
ax.plot(ppc_times, predictions["visual"].mean("sample"), label="visual", linewidth=3, c=colors_palette[1]);
ax.legend()

# plot posteriors
model_key = "complete_pooling"
axes = az.plot_forest(
    idata[model_key], 
    var_names=["t", "beta"],
    combined=True, 
    kind="ridgeplot",
    ridgeplot_quantiles=[.25, .5, .75],
    ridgeplot_overlap=0.7,
    ridgeplot_truncate=False,
    colors='white',
)

# %%
# log scale - complete pooled (cp)
with pm.Model(coords=coords) as cp_log_model:
    # index variables
    cid  = pm.Data('cid',  output_data['cid'].values, dims="obs")
    time = pm.Data('time', output_data['time'].values, dims="obs")

    # threshold
    t = pm.Normal('t', mu=1., sigma=.5)

    # slopes
    beta = pm.LogNormal('beta', mu=0, sigma=1, dims="condition")

    # guess rate
    g = .5

    # lapse rate         
    l = pm.Beta('l', alpha=2, beta=48)
    
    p = pm.Deterministic('p', g + (1-g-l) * pm.math.invlogit(beta[cid] * pm.math.log(time/t)), dims="obs")
    y = pm.Binomial('y', p=p, n=n_trials_per_condition, observed=output_data['hits'].values, dims="obs")
    idata["complete_pooling_log"] = pm.sample(nuts_sampler="numpyro", draws=2000, target_accept=0.95)

# %%
# posterior predicitive -- log scale complete pooled (cp)
ppc_times = np.linspace(-1,3,20)
predictions = dict()
for cname, cid in condition_map.items():
    with cp_model:
        pm.set_data(
            dict(
                time = ppc_times, 
                cid = np.repeat(cid,20)
                ), 
            coords={"obs": range(20)}
        )
        predictions[cname] = pm.sample_posterior_predictive(
            idata["complete_pooling_log"].sel(draw=slice(None, None, 5)), 
            var_names=["p"],
            predictions=True
        ).predictions.p.stack(sample=("chain","draw"))

fig, ax = plt.subplots()
ax.plot(ppc_times, predictions["semantic"], c=colors_palette[0], alpha=.01);
ax.plot(ppc_times, predictions["visual"], c=colors_palette[1], alpha=.01);
ax.plot(ppc_times, predictions["semantic"].mean("sample"), label="semantic", linewidth=3, c=colors_palette[0]);
ax.plot(ppc_times, predictions["visual"].mean("sample"), label="visual", linewidth=3, c=colors_palette[1]);
ax.legend()

# plot posteriors
model_key = "complete_pooling_log"
axes = az.plot_forest(
    idata[model_key], 
    var_names=["t", "beta"],
    combined=True, 
    kind="ridgeplot",
    ridgeplot_quantiles=[.25, .5, .75],
    ridgeplot_overlap=0.7,
    ridgeplot_truncate=False,
    colors='white',
)

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
fig, axes = plt.subplots(1,2, figsize=(10,4))

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
