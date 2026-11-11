
# %%
import os
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.stats import norm

# set working directory to project root
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(script_dir))

# SVG export settings for Inkscape compatibility
mpl.rcParams['svg.fonttype'] = 'none'

# colors (Okabe-Ito)
colors = {
    "semantic": "#E69F00",
    "visual": "#0072B2",
}

# fixed axis range for forest plot (all parameters on same scale)
FOREST_XLIM = (-.1, 1.5)


# %%
# data loading
def load_data(wave_ids):
    df = pd.read_csv(f"./output_data/aggregated/aggregated_pilot_vs.csv")
    df["encoding_time"] /= 1000
    df = df.loc[df.wave_id.isin(wave_ids)]
    df = df.rename(columns=dict(valid_responses="n", encoding_time="time"))
    return df


# %%
# model building
def build_model(df):
    sid, sessions = pd.factorize(df["session_id"], sort=True)
    cid, conditions = pd.factorize(df["condition_name"], sort=True)
    K = len(conditions)

    coords = {
        "session": sessions,
        "condition": conditions,
        "obs": np.arange(len(df)),
    }

    with pm.Model(coords=coords) as model:
        # data containers
        sid_ = pm.Data("sid", sid, dims="obs")
        cid_ = pm.Data("cid", cid, dims="obs")
        t = pm.Data("t", df["time"].to_numpy(), dims="obs")
        n = pm.Data("n", df["n"].to_numpy(), dims="obs")

        # population-level priors
        T_bar = pm.Normal("T_bar", mu=1.0, sigma=0.2, dims="condition")
        beta = pm.LogNormal("beta", mu=0.0, sigma=1.0, dims="condition")
        lam = pm.Beta("lam", alpha=2.0, beta=48.0)

        # random effects: LKJ Cholesky
        chol, R, sigma = pm.LKJCholeskyCov(
            "chol_T", n=K, eta=2.0,
            sd_dist=pm.Exponential.dist(1.0, shape=K),
            compute_corr=True,
        )

        # non-centered session deviations
        z = pm.Normal("z", mu=0.0, sigma=1.0, dims=("session", "condition"))
        v = pm.Deterministic("v", pm.math.dot(z, chol.T), dims=("session", "condition"))

        # session- and condition-specific thresholds
        T = pm.Deterministic("T", T_bar + v, dims=("session", "condition"))

        # psychometric function: guess rate 0.5, lapse lam, probit link
        eta = beta[cid_] * (t - T[sid_, cid_])
        p = pm.Deterministic("p", 0.5 + (0.5 - lam) * pm.math.invprobit(eta), dims="obs")

        # likelihood
        y = pm.Binomial("y", n=n, p=p, observed=df["hits"].to_numpy(), dims="obs")

    return model, sessions, conditions


# %%
# model fitting
def fit_model(model, draws=1000, tune=1000, chains=4, cores=2, target_accept=0.9, seed=42):
    with model:
        idata = pm.sample_prior_predictive(draws=500, random_seed=seed)
        trace = pm.sample(draws=draws, tune=tune, chains=chains, cores=cores, target_accept=target_accept, random_seed=seed)
        idata.extend(trace)
        ppc = pm.sample_posterior_predictive(idata, random_seed=seed)
        idata.extend(ppc)
    return idata


# %%
# psychometric function
def psychometric(t, T_bar, beta, lam):
    eta = beta * (t - T_bar)
    return 0.5 + (0.5 - lam) * norm.cdf(eta)


# %%
# plot psychometric function
def plot_psychometric(idata, conditions, wave_ids, save=True):
    # extract posteriors
    T_bar_post = idata.posterior["T_bar"].stack(sample=("chain", "draw")).values
    beta_post = idata.posterior["beta"].stack(sample=("chain", "draw")).values
    lam_post = idata.posterior["lam"].stack(sample=("chain", "draw")).values

    # time grid
    t_grid = np.linspace(0, 2.5, 100)

    # compute predictions
    p_pop = np.zeros((len(conditions), len(t_grid), T_bar_post.shape[1]))
    for c_idx in range(len(conditions)):
        for t_idx, t_val in enumerate(t_grid):
            p_pop[c_idx, t_idx, :] = psychometric(
                t_val, T_bar_post[c_idx, :], beta_post[c_idx, :], lam_post
            )

    p_mean = p_pop.mean(axis=2)
    p_lower = np.percentile(p_pop, 3, axis=2)
    p_upper = np.percentile(p_pop, 97, axis=2)

    # threshold statistics
    T_bar_mean = T_bar_post.mean(axis=1)
    T_bar_lower = np.percentile(T_bar_post, 3, axis=1)
    T_bar_upper = np.percentile(T_bar_post, 97, axis=1)
    threshold_p = 0.5 + (0.5 - lam_post.mean()) * 0.5

    # plot
    fig, ax = plt.subplots(figsize=(6, 4))

    for c_idx, cond in enumerate(conditions):
        ax.fill_between(t_grid, p_lower[c_idx], p_upper[c_idx], alpha=0.15, color=colors[cond])
        ax.plot(t_grid, p_mean[c_idx], label=cond, color=colors[cond], lw=2)

        ax.axvspan(T_bar_lower[c_idx], T_bar_upper[c_idx], alpha=0.08, color=colors[cond])
        ax.axvline(T_bar_mean[c_idx], color=colors[cond], ls="--", lw=1.5)
        ax.text(T_bar_mean[c_idx], 0.5, f"{T_bar_mean[c_idx]:.2f}s",
                rotation=90, va="center", ha="right", fontsize=12, color=colors[cond])

    ax.axhline(threshold_p, color="gray", ls=":", lw=1, alpha=0.7, label=f"threshold ({threshold_p:.0%})")
    ax.set_xlabel("Encoding time (s)")
    ax.set_ylabel("P(correct)")
    ax.set_xlim(0, 2.5)
    ax.set_ylim(0.4, 1.0)
    ax.legend(title="Condition")

    # title with wave IDs
    waves_str = ", ".join([w.replace("M-", "") for w in wave_ids])
    ax.set_title(f"Waves: {waves_str}")
    fig.tight_layout()

    if save:
        waves_fname = "_".join([w.replace("M-", "") for w in wave_ids])
        fname = f"./figures/pilots/psychometric_{waves_fname}.svg"
        fig.savefig(fname, format="svg", bbox_inches="tight")
        print(f"Saved: {fname}")

    return fig, ax


# %%
# plot forest
def plot_forest(idata, conditions, wave_ids, save=True):
    # extract posteriors and compute summaries
    post = idata.posterior

    params = []
    # T_bar per condition
    for cond in conditions:
        samples = post["T_bar"].sel(condition=cond).values.flatten()
        params.append({
            "name": f"T_bar[{cond}]",
            "mean": np.mean(samples),
            "hdi_low": np.percentile(samples, 3),
            "hdi_high": np.percentile(samples, 97),
            "color": colors[cond],
        })
    # beta per condition
    for cond in conditions:
        samples = post["beta"].sel(condition=cond).values.flatten()
        params.append({
            "name": f"beta[{cond}]",
            "mean": np.mean(samples),
            "hdi_low": np.percentile(samples, 3),
            "hdi_high": np.percentile(samples, 97),
            "color": colors[cond],
        })
    # lam (single parameter)
    samples = post["lam"].values.flatten()
    params.append({
        "name": "lam",
        "mean": np.mean(samples),
        "hdi_low": np.percentile(samples, 3),
        "hdi_high": np.percentile(samples, 97),
        "color": "#555555",
    })

    # plot
    fig, ax = plt.subplots(figsize=(6, 4))

    # y positions with grouping: T_bar group, gap, beta group, gap, lam
    n_cond = len(conditions)
    y_positions = []
    y = 0
    # lam (bottom)
    y_positions.append(y)
    y += 1.5  # gap before beta group
    # beta group
    for _ in range(n_cond):
        y_positions.append(y)
        y += 0.6  # tight spacing within group
    y += 0.9  # gap before T_bar group
    # T_bar group
    for _ in range(n_cond):
        y_positions.append(y)
        y += 0.6
    y_positions = y_positions[::-1]  # reverse to match params order

    for i, p in enumerate(params):
        y = y_positions[i]
        # HDI bar
        ax.plot([p["hdi_low"], p["hdi_high"]], [y, y], color=p["color"], lw=3, solid_capstyle="round")
        # mean point
        ax.plot(p["mean"], y, "o", color=p["color"], markersize=8, markeredgecolor="white", markeredgewidth=1)

    ax.set_yticks(y_positions)
    ax.set_yticklabels([p["name"] for p in params])
    ax.set_xlabel("Estimate (94% HDI)")
    ax.set_xlim(FOREST_XLIM)

    # title with wave IDs
    waves_str = ", ".join([w.replace("M-", "") for w in wave_ids])
    ax.set_title(f"Waves: {waves_str}")
    fig.tight_layout()

    if save:
        waves_fname = "_".join([w.replace("M-", "") for w in wave_ids])
        fname = f"./figures/pilots/forest_{waves_fname}.svg"
        fig.savefig(fname, format="svg", bbox_inches="tight")
        print(f"Saved: {fname}")

    return fig, ax


# %%
# main analysis function
def run_analysis(wave_ids, save=True):
    print(f"Running analysis for waves: {wave_ids}")

    # load data
    df = load_data(wave_ids)
    print(f"Loaded {len(df)} observations from {df['session_id'].nunique()} sessions")

    # build and fit model
    model, sessions, conditions = build_model(df)
    idata = fit_model(model)

    # print summary
    print(az.summary(idata, var_names=["T_bar", "beta", "lam", "chol_T_stds", "chol_T_corr"]))

    # plots
    plot_psychometric(idata, conditions, wave_ids, save=save)
    plot_forest(idata, conditions, wave_ids, save=save)

    return idata, model, sessions, conditions


# %%
# run analysis for specified waves
if __name__ == "__main__":
    wave_ids = ["M-PD", "M-PE", "M-PF"]
    idata, model, sessions, conditions = run_analysis(wave_ids, save=True)


# %%
