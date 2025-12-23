import pandas as pd
import numpy as np
from itertools import product
import pymc as pm

def get_times(lower_limit=1, a=.33, b=.66):
    upper_limit = lower_limit * 2.5
    lower_middle = lower_limit + (upper_limit-lower_limit) * a
    upper_middle = lower_limit + (upper_limit-lower_limit) * b

    times = np.array([
        lower_limit,
        lower_middle,
        upper_middle, 
        upper_limit
    ])

    time_centered = times-np.mean(times)
    time_centered
    return time_centered

time_centered = get_times()
conditions = [0,1]
timesxconditions = product(time_centered, conditions)

n_trials_per_condition = 12
data = [{
    "time":         time, 
    "condition":    condition,
    } for i, (time, condition) in enumerate(timesxconditions)
    ] 
data = data*n_trials_per_condition
data = pd.DataFrame(data)
data.index.name = "trial_id"

# pm model
draws = 100
with pm.Model() as model1:
    l = .5

    hyper_alpha = (0., 0.)
    hyper_beta  = (5., 3.)

    alpha_mu = pm.Normal("alpha_mu", hyper_alpha, 1., shape=2)
    beta_mu  = pm.Normal("beta_mu",  hyper_beta, 1., shape=2)

    alpha = pm.Normal('alpha', alpha_mu, .1, shape=2)
    beta  = pm.Normal('beta', beta_mu,  .1, shape=2)
    cid   = pm.Data('cid', data['condition'])
    
    time = pm.Data('time', data['time'].values)
    
    p = pm.Deterministic(
        'p', 
        l + (1-l) * pm.math.invlogit(alpha[cid] + beta[cid] * time)
        )
    y = pm.Bernoulli('y', p=p)

with model1:
    idata = pm.sample_prior_predictive(draws=draws)

idf  = idata.prior.p[0,:,:].to_pandas().T
idf  = (data
        .join(idf)
        .groupby(["condition","time"])
        .mean()
        .reset_index()
        )

print(idf.iloc[:, :5].head())

