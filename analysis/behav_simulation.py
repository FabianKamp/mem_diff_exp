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

# %% 
# set up encoding times 
def get_input_data(time, wave_id):    
    timesxconditions = product(time, conditions)
    data = [{
        "wave_id":      wave_id,
        "time":         time, 
        "condition":    condition,
        } for _, (time, condition) in enumerate(timesxconditions)
        ] 
    data = pd.DataFrame(data)
    data.index.name = "trial_id"
    return data 

conditions = [0,1]
n_trials_per_condition = 13

input_data = pd.concat([
    get_input_data(np.array([.7, 1.2, 1.7, 2.2]), 1),   # wave 1
    get_input_data(np.array([.4,  .9, 1.4, 1.9]), 2),   # wave 2
    get_input_data(np.array([.5,  .7, 1.2, 1.5 ]), 3)   # wave 3
])

input_data["time"] = np.round(input_data.time, 3)
input_data

# %% 
# plotting function
def boxplot_idata(data, ax):  
    sns.boxplot(
        data=data, 
        x="time", 
        y="accuracy", 
        hue="condition", 
        ax=ax,
        native_scale=True,
        width=.5
        )

    ax.axhline(
        .5, 
        linestyle="--",
        c="k",
        linewidth=.1,
        )

    ax.grid(alpha=.1)

# %%
# simulating outcome
def simulator(input_data, draws):
    with pm.Model() as generator_model:
        t_bar = pm.Normal('t_bar', (1., 1.), .1, shape=2)
        beta   = pm.Normal('beta', (.5, 2.), .1, shape=2)
        
        cid   = pm.Data('cid', input_data['condition'])
        time = pm.Data('time', input_data['time'].values)

        # logit p
        logit_p = beta[cid] * (time - t_bar[cid])
        
        lapse = .5
        p = pm.Deterministic('p', lapse + (1-lapse) * pm.math.invlogit(logit_p))
        pm.Binomial('y', n=n_trials_per_condition, p=p)

    with generator_model:
        idata = pm.sample_prior_predictive(draws=draws)
    
    simulated_data  = idata.prior.y[0,:,:].to_pandas().T
    simulated_data = input_data.join(simulated_data)
    return simulated_data

# %%
# process output
n_sessions = 10
simulated_data = pd.concat([
    simulator(input_data.loc[input_data.wave_id==wave], draws=n_sessions)
    for wave in input_data.wave_id.unique()
])

output_data  = (simulated_data
    .melt(id_vars=["wave_id", "condition", "time"], var_name="session_id", value_name="hits")
    .assign(session_id = lambda d: d["session_id"] + (d["wave_id"]-1)*n_sessions)
    .assign(accuracy = lambda d: d["hits"]/n_trials_per_condition)
    .sort_values(by=["session_id","condition","time"])
    )

# one plot
fig, ax = plt.subplots(figsize=(18,6), sharex=True, sharey=True)
boxplot_idata(output_data, ax);

# fig, ax = plt.subplots(2,1, figsize=(18,6), sharex=True, sharey=True)
# boxplot_idata(output_data.loc[output_data.wave_id==1], ax[0]);
# boxplot_idata(output_data.loc[output_data.wave_id==2], ax[1]);

# %%
# fit hierachical model
output_data["session_id"] = output_data.session_id.astype(int)
output_data["condition"] = output_data.condition.astype(int)
output_data["hits"] = output_data.hits.astype(int)

n_sessions = output_data.session_id.nunique()
n_conditions = 2 

coords = {
    "session": range(n_sessions),
    "condition": range(n_conditions),
    "obs": range(len(output_data)),
}

with pm.Model(coords=coords) as hierachical_model:
    # index variables
    sid  = pm.Data('sid',  output_data['session_id'].values, dims="obs")
    cid  = pm.Data('cid',  output_data['condition'].values, dims="obs")
    time = pm.Data('time', output_data['time'].values, dims="obs")

    # t (reparameterized for multilevel)
    t_bar = pm.Normal('t_bar', 1., .5)
    t_sigma = pm.Exponential('t_sigma', 1.)
    t_z = pm.Normal('t_z', 0., 1., dims=("session", "condition"))
    t = pm.Deterministic('t', t_bar + t_z[sid,cid] * t_sigma, dims="obs")

    # slopes
    beta = pm.LogNormal('beta', mu=0, sigma=1, dims="condition")
        
    l = .5
    p = pm.Deterministic('p', l + (1-l) * pm.math.invlogit(beta[cid] * (time - t)), dims="obs")
    y = pm.Binomial('y', p=p, n=n_trials_per_condition, observed=output_data['hits'].values, dims="obs")

with hierachical_model:
    idata = pm.sample(nuts_sampler="numpyro", draws=2000)

# %%
# plot inference data
posterior = idata.posterior
t_sessions = posterior["t_bar"] + posterior["t_z"] * posterior["t_sigma"]
t_df = (t_sessions.mean(dim=["chain", "draw"])
    .to_dataframe("t")
    .reset_index()
)

sns.boxplot(
    data=t_df, 
    y="t", 
    hue="condition",
)

plt.figure()
plt.hist(posterior.beta[...,0].to_numpy().flatten())
plt.hist(posterior.beta[...,1].to_numpy().flatten())

# %%
