# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
from scipy import stats

# %%
def plot_logit_prior(mu=0, sigma=1, n_samples=10000):
    """
    Visualize a Normal prior on logit scale and its implied distribution on probability scale.

    Args:
        mu: Mean of Normal prior on logit scale
        sigma: SD of Normal prior on logit scale
        n_samples: Number of samples for histogram
    """
    fig, axes = plt.subplots(1, 3, figsize=(12, 3))

    # Sample from prior on logit scale
    logit_samples = np.random.normal(mu, sigma, n_samples)
    prob_samples = 1 / (1 + np.exp(-logit_samples))  # invlogit

    # Left: prior on logit scale
    axes[0].hist(logit_samples, bins=50, density=True, alpha=0.7)
    axes[0].set_xlabel("logit scale")
    axes[0].set_title(f"Prior: Normal({mu}, {sigma})")
    axes[0].axvline(mu, color='red', linestyle='--', label=f'mean={mu} → p={1/(1+np.exp(-mu)):.2f}')
    axes[0].legend()

    # Middle: transformation
    x = np.linspace(-4, 4, 100)
    axes[1].plot(x, 1/(1+np.exp(-x)), 'b-', lw=2)
    axes[1].set_xlabel("logit scale")
    axes[1].set_ylabel("probability scale")
    axes[1].set_title("invlogit transformation")
    axes[1].axhline(0.5, color='gray', linestyle=':', alpha=0.5)
    axes[1].axvline(0, color='gray', linestyle=':', alpha=0.5)

    # Right: implied prior on probability scale
    axes[2].hist(prob_samples, bins=50, density=True, alpha=0.7)
    axes[2].set_xlabel("probability scale")
    axes[2].set_title("Implied prior on probability")
    median_prob = np.median(prob_samples)
    axes[2].axvline(median_prob, color='red', linestyle='--', label=f'median={median_prob:.2f}')
    ci_low, ci_high = np.percentile(prob_samples, [2.5, 97.5])
    axes[2].axvline(ci_low, color='orange', linestyle=':', label=f'95% CI: [{ci_low:.2f}, {ci_high:.2f}]')
    axes[2].axvline(ci_high, color='orange', linestyle=':')
    axes[2].legend()

    plt.tight_layout()
    plt.show()

    print(f"Prior on probability scale (from Normal({mu}, {sigma}) on logit):")
    print(f"  Median: {median_prob:.2f}")
    print(f"  95% CI: [{ci_low:.2f}, {ci_high:.2f}]")

plot_logit_prior(mu=0, sigma=1)

# %%
def simulate_mpt_data(params, seed=42):
    """
    Simulate MPT data for two encoding time conditions.

    Args:
        params: dict with keys:
            - n_participants, n_trials
            - ms_short, ms_long, mv_short, mv_long, b (true values)
            - sd_ms, sd_mv, sd_b (between-subject SDs)
        seed: random seed

    Returns:
        df: DataFrame with columns [subject_id, condition, encoding_time, hits, n_trials]
    """
    np.random.seed(seed)

    n_participants = params["n_participants"]
    n_trials = params["n_trials"]

    # Simulate individual variation around true values
    ms_short_subj = np.clip(np.random.normal(params["ms_short"], params["sd_ms"], n_participants), 0.01, 0.99)
    ms_long_subj = np.clip(np.random.normal(params["ms_long"], params["sd_ms"], n_participants), 0.01, 0.99)
    mv_short_subj = np.clip(np.random.normal(params["mv_short"], params["sd_mv"], n_participants), 0.01, 0.99)
    mv_long_subj = np.clip(np.random.normal(params["mv_long"], params["sd_mv"], n_participants), 0.01, 0.99)
    b_subj = np.clip(np.random.normal(params["b"], params["sd_b"], n_participants), 0.01, 0.99)

    def compute_hit_probs(ms, mv, b):
        ph_s = ms + (1 - ms) * 0.5
        ph_v = mv + (1 - mv) * 0.5
        ph_sv = ms * (1 - mv) + ms * mv * b + (1 - ms) * (1 - mv) * 0.5
        return ph_s, ph_v, ph_sv

    # Build dataframe
    rows = []
    for subj in range(n_participants):
        for enc_time, ms, mv, b in [
            ("short", ms_short_subj[subj], mv_short_subj[subj], b_subj[subj]),
            ("long", ms_long_subj[subj], mv_long_subj[subj], b_subj[subj])
        ]:
            ph_s, ph_v, ph_sv = compute_hit_probs(ms, mv, b)
            hits_s = np.random.binomial(n_trials, ph_s)
            hits_v = np.random.binomial(n_trials, ph_v)
            hits_sv = np.random.binomial(n_trials, ph_sv)

            rows.append({"subject_id": subj, "condition": "s", "encoding_time": enc_time, "hits": hits_s, "n_trials": n_trials})
            rows.append({"subject_id": subj, "condition": "v", "encoding_time": enc_time, "hits": hits_v, "n_trials": n_trials})
            rows.append({"subject_id": subj, "condition": "sv", "encoding_time": enc_time, "hits": hits_sv, "n_trials": n_trials})

    df = pd.DataFrame(rows)

    return df

# %%
# Define true parameters
# Now modeling mv directly instead of c = mv/ms
true_params = {
    "n_participants": 80,
    "n_trials": 26,
    "ms_short": 0.5,
    "ms_long": 0.7,
    "mv_short": 0.7,  
    "mv_long": 0.5,   
    "b": 0.8,
    "sd_ms": 0.1,
    "sd_mv": 0.1,
    "sd_b": 0.1,
}

# Simulate data
df = simulate_mpt_data(true_params, seed=42)

n_participants = true_params["n_participants"]
n_trials = true_params["n_trials"]

print("True parameters:")
for k, v in true_params.items():
    print(f"  {k}: {v}")
print(f"\nSimulated {n_participants} participants, {n_trials} trials per condition")
print(df.head(12))

# %%
def plot_accuracy_by_condition(df):
    """
    Plot mean accuracy by condition for each encoding time.

    Args:
        df: DataFrame with columns [condition, encoding_time, hits, n_trials]
    """
    df = df.copy()
    df["accuracy"] = df["hits"] / df["n_trials"]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)

    for ax, enc_time in zip(axes, ["short", "long"]):
        subset = df[df["encoding_time"] == enc_time]
        means = subset.groupby("condition")["accuracy"].mean()
        sems = subset.groupby("condition")["accuracy"].sem()

        conditions = ["s", "v", "sv"]
        x = np.arange(len(conditions))

        ax.bar(x, [means[c] for c in conditions], yerr=[sems[c] for c in conditions],
               capsize=5, color=['steelblue', 'coral', 'seagreen'], alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(conditions)
        ax.set_xlabel("Condition")
        ax.set_title(f"{enc_time.capitalize()} encoding")
        ax.set_ylim(0, 1)
        ax.axhline(0.5, color='gray', linestyle='--', alpha=0.5, label='chance')

    axes[0].set_ylabel("Accuracy (hits / n_trials)")
    axes[0].legend()

    plt.suptitle("Mean accuracy by condition and encoding time", y=1.02)
    plt.tight_layout()
    plt.show()

plot_accuracy_by_condition(df)

# %%
# Prepare data with indices for PyMC
# Create encoding time index: 0 = short, 1 = long
enc_map = {"short": 0, "long": 1}
df["enc_idx"] = df["encoding_time"].map(enc_map)

# Extract data arrays per condition (s, v, sv)
# Each array: one row per (subject, encoding_time) combination
def prepare_condition_data(df, condition):
    subset = df[df["condition"] == condition].sort_values(["subject_id", "enc_idx"])
    return {
        "hits": subset["hits"].values,
        "n_trials": subset["n_trials"].values,
        "subj_idx": subset["subject_id"].values,
        "enc_idx": subset["enc_idx"].values,
    }

data_s = prepare_condition_data(df, "s")
data_v = prepare_condition_data(df, "v")
data_sv = prepare_condition_data(df, "sv")

n_obs = len(data_s["hits"])  # observations per condition
print(f"\nData shape: {n_obs} observations per condition ({n_participants} subjects × 2 encoding times)")
print(f"Short encoding mean hits: s={data_s['hits'][data_s['enc_idx']==0].mean():.1f}, v={data_v['hits'][data_v['enc_idx']==0].mean():.1f}, sv={data_sv['hits'][data_sv['enc_idx']==0].mean():.1f}")
print(f"Long encoding mean hits:  s={data_s['hits'][data_s['enc_idx']==1].mean():.1f}, v={data_v['hits'][data_v['enc_idx']==1].mean():.1f}, sv={data_sv['hits'][data_sv['enc_idx']==1].mean():.1f}")

# %%
# Extract indices for model
subj_idx = data_s["subj_idx"]  # same for all conditions
enc_idx = data_s["enc_idx"]    # same for all conditions

with pm.Model() as mpt_model:
    # Data containers
    subj_idx_data = pm.Data("subj_idx", subj_idx)
    enc_idx_data = pm.Data("enc_idx", enc_idx)

    # Group-level priors: shape=(2,) for [short, long]
    mu_ms = pm.Normal("mu_ms", mu=0, sigma=1, shape=2)
    mu_mv = pm.Normal("mu_mv", mu=0, sigma=1, shape=2)
    mu_b = pm.Normal("mu_b", mu=0, sigma=1)

    # Between-subject SDs (shared across encoding times)
    sigma_ms = pm.Exponential("sigma_ms", lam=2)
    sigma_mv = pm.Exponential("sigma_mv", lam=2)
    sigma_b = pm.Exponential("sigma_b", lam=2)

    # Subject-level offsets (shared across encoding times - same subject deviation)
    ms_offset = pm.Normal("ms_offset", mu=0, sigma=1, shape=n_participants)
    mv_offset = pm.Normal("mv_offset", mu=0, sigma=1, shape=n_participants)
    b_offset = pm.Normal("b_offset", mu=0, sigma=1, shape=n_participants)

    # Subject-level parameters: shape=(2, n_participants) for [enc_time, subject]
    ms_subj = pm.Deterministic(
        "ms_subj",
        pm.math.invlogit(mu_ms[:, None] + sigma_ms * ms_offset[None, :])
    )  # shape: (2, n_participants)
    mv_subj = pm.Deterministic(
        "mv_subj",
        pm.math.invlogit(mu_mv[:, None] + sigma_mv * mv_offset[None, :])
    )
    b_subj = pm.Deterministic(
        "b_subj",
        pm.math.invlogit(mu_b + sigma_b * b_offset)
    )  # shape: (n_participants,)

    # Index into subject-level parameters for each observation
    ms = ms_subj[enc_idx_data, subj_idx_data]
    mv = mv_subj[enc_idx_data, subj_idx_data]
    b = b_subj[subj_idx_data]

    # Derived contrasts on group level (logit scale)
    c_logit = pm.Deterministic("c_logit", mu_mv - mu_ms)  # shape: (2,) [short, long]
    c_diff = pm.Deterministic("c_diff", c_logit[0] - c_logit[1])  # short - long

    # Hit probabilities
    ph_s = ms + (1 - ms) * 0.5
    ph_v = mv + (1 - mv) * 0.5
    ph_sv = ms * (1 - mv) + ms * mv * b + (1 - ms) * (1 - mv) * 0.5

    # Likelihoods (single observation per condition, indexed)
    obs_s = pm.Binomial("obs_s", n=data_s["n_trials"], p=ph_s, observed=data_s["hits"])
    obs_v = pm.Binomial("obs_v", n=data_v["n_trials"], p=ph_v, observed=data_v["hits"])
    obs_sv = pm.Binomial("obs_sv", n=data_sv["n_trials"], p=ph_sv, observed=data_sv["hits"])

# %%
# Sample from posterior
with mpt_model:
    trace = pm.sample(2000, tune=2000, cores=1, chains=2, random_seed=42,
                       target_accept=0.95)

# %%
# Summarize group-level results
print("Group-level parameters:")
print(az.summary(trace, var_names=["mu_ms", "mu_mv", "mu_b", "c_logit", "c_diff"]))

# %%
# Key contrast: is the mv/ms relationship different between conditions?
c_diff_samples = trace.posterior["c_diff"].values.flatten()
c_logit_samples = trace.posterior["c_logit"].values  # shape: (chains, draws, 2)
c_short_logit_samples = c_logit_samples[:, :, 0].flatten()
c_long_logit_samples = c_logit_samples[:, :, 1].flatten()

print("\n" + "="*60)
print("KEY RESULT: mv/ms relationship across conditions")
print("="*60)

print(f"\nc_short (logit scale, logit(mv) - logit(ms)):")
print(f"  Mean: {c_short_logit_samples.mean():.3f}")
print(f"  94% HDI: [{np.percentile(c_short_logit_samples, 3):.3f}, {np.percentile(c_short_logit_samples, 97):.3f}]")

print(f"\nc_long (logit scale, logit(mv) - logit(ms)):")
print(f"  Mean: {c_long_logit_samples.mean():.3f}")
print(f"  94% HDI: [{np.percentile(c_long_logit_samples, 3):.3f}, {np.percentile(c_long_logit_samples, 97):.3f}]")

print(f"\nc_diff (c_short - c_long, on logit scale):")
print(f"  Mean: {c_diff_samples.mean():.3f}")
print(f"  94% HDI: [{np.percentile(c_diff_samples, 3):.3f}, {np.percentile(c_diff_samples, 97):.3f}]")
print(f"  P(c_diff > 0): {(c_diff_samples > 0).mean():.3f}")

if np.percentile(c_diff_samples, 3) > 0 or np.percentile(c_diff_samples, 97) < 0:
    print("\n→ HDI excludes 0: Evidence for different mv/ms relationship across conditions")
else:
    print("\n→ HDI includes 0: No evidence for different mv/ms relationship across conditions")

# Compute true c ratios for comparison
true_c_short = true_params['mv_short'] / true_params['ms_short']
true_c_long = true_params['mv_long'] / true_params['ms_long']
print(f"\nTrue values: c_short={true_c_short:.2f}, c_long={true_c_long:.2f}")

# %%
# Transform and display all group means
mu_ms_samples = trace.posterior["mu_ms"].values  # shape: (chains, draws, 2)
mu_mv_samples = trace.posterior["mu_mv"].values
ms_short_group = 1 / (1 + np.exp(-mu_ms_samples[:, :, 0].flatten()))
ms_long_group = 1 / (1 + np.exp(-mu_ms_samples[:, :, 1].flatten()))
mv_short_group = 1 / (1 + np.exp(-mu_mv_samples[:, :, 0].flatten()))
mv_long_group = 1 / (1 + np.exp(-mu_mv_samples[:, :, 1].flatten()))
b_group = 1 / (1 + np.exp(-trace.posterior["mu_b"].values.flatten()))

print("\nGroup means (transformed to probability scale):")
print(f"  ms[0] (short): {ms_short_group.mean():.3f} (true: {true_params['ms_short']})")
print(f"  ms[1] (long):  {ms_long_group.mean():.3f} (true: {true_params['ms_long']})")
print(f"  mv[0] (short): {mv_short_group.mean():.3f} (true: {true_params['mv_short']})")
print(f"  mv[1] (long):  {mv_long_group.mean():.3f} (true: {true_params['mv_long']})")
print(f"  b:             {b_group.mean():.3f} (true: {true_params['b']})")

# Derived c ratios
print("\nDerived c ratios (mv/ms):")
print(f"  c[0] (short): {(mv_short_group / ms_short_group).mean():.3f} (true: {true_params['mv_short']/true_params['ms_short']:.2f})")
print(f"  c[1] (long):  {(mv_long_group / ms_long_group).mean():.3f} (true: {true_params['mv_long']/true_params['ms_long']:.2f})")

# %%
# Plot the key contrasts
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# Top row: ms and mv estimates (indexed)
az.plot_posterior(trace, var_names=["mu_ms"], ax=axes[0, 0])
axes[0, 0].set_title("Source memory (mu_ms) - logit scale\n[0]=short, [1]=long")

az.plot_posterior(trace, var_names=["mu_mv"], ax=axes[0, 1])
axes[0, 1].set_title("Verbatim memory (mu_mv) - logit scale\n[0]=short, [1]=long")

# Bottom row: c relationship and contrast
az.plot_posterior(trace, var_names=["c_logit"], ax=axes[1, 0])
axes[1, 0].set_title("c = logit(mv) - logit(ms)\n[0]=short, [1]=long")

az.plot_posterior(trace, var_names=["c_diff"], ax=axes[1, 1], ref_val=0)
axes[1, 1].set_title("c_diff: (c_short - c_long)")
axes[1, 1].axvline(x=0, color='red', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()


# %%
