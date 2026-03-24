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
from scipy import stats

def power_simulation(
        posterior,
        times,
        sample_size,
        n_trials = 26,
        n_sim = 1000
    ):
    
    conditions = ["visual", "semantic"]
    successes = 0
    
    for _ in tqdm(range(n_sim)):
        idx = np.random.randint(0, 8000)
        
        y = np.zeros((sample_size, 2,2))
        for i,j in np.ndindex((2,2)):
            
            condition = conditions[i]
            time = times[j]
            
            b_param = posterior["beta"].sel(condition=condition).values[idx]
            t_param = posterior["t"].sel(condition=condition).values[idx]
            l_param = posterior["l"].values[idx]

            p = .5 + (.5-l_param) * expit(b_param * (time - t_param))
            y[:,i,j] = np.random.binomial(n_trials, p, size=sample_size)

        acc = y/n_trials
        beta0 = acc[:,0,0] - acc[:,0,1]
        beta1 = acc[:,1,0] - acc[:,1,1]
        interaction = beta0 - beta1

        _, pval = stats.ttest_1samp(interaction, 0)
        if pval < .05:
            successes += 1

    return successes/n_sim


# %%
posterior = (idata["partial_pooling"]
    .posterior
    .stack(sample=("chain", "draw"))
    .sel(load=4)
)

times = [
    [.1, .5],
    [.125, .5],
    [.1, .55],
    [.125, .55],
    [.1, .6],
    [.125, .6],
]

sample_sizes = [50, 65, 80, 95]
results = []

for t in times:
    for n in sample_sizes:
        print("Running sample size: ", n, end="\n")
        p_success = power_simulation(
            posterior,
            sample_size=n,
            times = t,
        )
        results.append({
            "n": n, 
            "t1": t[0],
            "t2": t[1],
            "power": p_success, 
            })

df_power = pd.DataFrame(results)


# %%

df_power["t_ratio"] = np.round(df_power.t2/df_power.t1,3)
sns.relplot(
    data=df_power,
    x="n",
    y="power",
    hue="t2",
    col="t1",
    marker="o",
    kind="line"
)

# %%
