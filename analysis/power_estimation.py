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
from scipy.special import expit
import seaborn as sns
from tqdm import tqdm
from scipy import stats


# %%
# set up
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
box.set_xlabel("time per item")
box.grid(alpha=.3)

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
def power_simulation(
        posterior,
        times,
        sample_size,
        n_trials = 26,
        n_sim = 1000, 
    ):

    significant = 0
    conditions = ["visual", "semantic"]    
    y = np.zeros((sample_size, n_sim, 2, 2))
    
    for sim in tqdm(range(n_sim)):
        idx = np.random.randint(0, 8000)
        for i,j in np.ndindex((2,2)):
            
            condition = conditions[i]
            time = times[j]
            
            b_param = posterior["beta"].sel(condition=condition).values[idx]
            t_param = posterior["t"].sel(condition=condition).values[idx]
            l_param = posterior["l"].values[idx]

            p = .5 + (.5-l_param) * expit(b_param * (time - t_param))
            y[:,sim,i,j] = np.random.binomial(n_trials, p, size=sample_size)

        # frequentist power
        acc = y[:,sim,...]/n_trials
        beta0 = acc[:,0,0] - acc[:,0,1]
        beta1 = acc[:,1,0] - acc[:,1,1]
        _, pval = stats.ttest_rel(beta0, beta1)
        if pval < .05:
            significant += 1
    
    freq_power = significant/n_sim
    
    return dict(
        freq_power = freq_power,
    )

# %%
posterior = (idata["partial_pooling"]
    .posterior
    .stack(sample=("chain", "draw"))
    .sel(load=4)
)

times = [.1, .55]
sample_sizes = np.arange(50,201,25)
results = []

for n in sample_sizes:
    print("Running sample size: ", n, end="\n")
    power_dict = power_simulation(
        posterior,
        sample_size=n,
        times = times,
    )
    results.append({
        "n": n, 
        "t1": times[0],
        "t2": times[1],
        "power": power_dict["freq_power"], 
        })
df_power = pd.DataFrame(results)

# %%
# plot power
line = sns.lineplot(
    data=df_power,
    x="n",
    y="power",
    marker="o",
)
line.grid(alpha=.2)

# %%
# archive

# recovery model
coords = {
    "simulation": range(n_sim),
    "sample": range(sample_size),
    "condition": ["visual", "semantic"],
    "time": ["short", "long"],
}

with pm.Model(coords=coords) as recov_model:
    mu = pm.Normal('mu', mu=0, sigma=1, dims=("simulation", "condition", "time"))
    p = pm.Deterministic('p', pm.math.invlogit(mu), dims=("simulation", "condition", "time"))
    y = pm.Binomial('y', p=p, n=n_trials, observed=y, dims=("sample", "simulation", "condition", "time"))
    idata = pm.sample(nuts_sampler="numpyro", chains=2, draws=500, target_accept=0.95)


mu = idata.posterior["mu"]
beta0 = mu.sel(condition="visual", time="short") - mu.sel(condition="visual", time="long")
beta1 = mu.sel(condition="semantic", time="short") - mu.sel(condition="semantic", time="long")
interaction = beta0 - beta1  

samples = interaction.stack(sample=("chain", "draw")).values
hdi_vals = az.hdi(samples, hdi_prob=0.90)

lower = hdi_vals[:, 0]
upper = hdi_vals[:, 1]

significant = ((lower > 0) | (upper < 0)).sum()
bayes_power = significant / n_sim


with pm.Model(coords=coords) as recov_model:
    time_vals = pm.Data('time_vals', np.array(times), dims="time")
    t = pm.Normal('t', mu=.5, sigma=.5, dims=("simulation","condition"))
    beta = pm.LogNormal('beta', mu=0, sigma=1, dims=("simulation","condition"))

    g = .5      
    l = pm.Beta('l', alpha=2, beta=48, dims="simulation")

    p = pm.Deterministic('p',
        g + (1-g-l[:, None, None]) * pm.math.invlogit(beta[:, :, None] * (time_vals[None, None, :] - t[:, :, None])),
        dims=("simulation", "condition", "time"))

    y = pm.Binomial('y', p=p, n=n_trials, observed=y, dims=("sample", "simulation", "condition", "time"))
    idata = pm.sample(nuts_sampler="numpyro", chains=2, draws=500, target_accept=0.95)
