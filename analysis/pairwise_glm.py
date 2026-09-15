"""
Paired-comparison GLM (Bradley-Terry / Thurstone-Mosteller), following
Critchlow & Fligner (1991, Psychometrika 56, 517-533).

Fits win/loss data for a set of items as a binomial GLM:

    link( P(i beats j) ) = lambda_i - lambda_j

- logit link  -> Bradley-Terry model, lambda_i = log-worth of item i
- probit link -> Thurstone-Mosteller Case V model; lambda_i is then
                 rescaled by sqrt(2) to give Thurstone's latent
                 "scale value" mu_i (under the sigma = 1 convention).

One item is fixed as reference (lambda = 0) for identifiability.

Mixed-effects extension:
    For repeated measures (multiple subjects), use pymer4 to fit a GLMM
    with random intercepts/slopes per subject.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm

# Optional: pymer4 for mixed-effects (requires R + lme4)
try:
    from pymer4.models import Lmer
    HAS_PYMER4 = True
except ImportError:
    HAS_PYMER4 = False


def build_design_matrix(items: list[str], pairs: list[tuple[str, str]], reference: str) -> pd.DataFrame:
    """One row per compared pair (i, j): +1 in item i's column, -1 in
    item j's column. The reference item's column is omitted, which
    pins lambda_reference = 0."""
    columns = [it for it in items if it != reference]
    X = pd.DataFrame(0.0, index=range(len(pairs)), columns=columns)
    for row, (i, j) in enumerate(pairs):
        if i in columns:
            X.loc[row, i] += 1.0
        if j in columns:
            X.loc[row, j] -= 1.0
    return X


def simulate_thurstone_case_v(mu_true: dict[str, float], pairs: list[tuple[str, str]],
                               n_per_pair: int, rng: np.random.Generator) -> np.ndarray:
    """Generate win counts under Thurstone's Case V generative model:
    X_i ~ N(mu_i, 1), independent across items and trials; i beats j
    on a given trial iff X_i > X_j."""
    wins = []
    for i, j in pairs:
        Xi = rng.normal(mu_true[i], 1.0, size=n_per_pair)
        Xj = rng.normal(mu_true[j], 1.0, size=n_per_pair)
        wins.append(int(np.sum(Xi > Xj)))
    return np.array(wins)


def fit_paired_comparison_glm(X: pd.DataFrame, wins: np.ndarray, n_trials: np.ndarray, link):
    """Binomial GLM with endog given as (successes, failures) counts."""
    endog = np.column_stack([wins, n_trials - wins])
    model = sm.GLM(endog, X, family=sm.families.Binomial(link=link()))
    return model.fit()


def thurstone_scale_values(probit_result, items: list[str], reference: str):
    """Rescale probit-link lambda's into Thurstone Case V scale values
    mu_i = sqrt(2) * lambda_i (sigma = 1 convention), still expressed
    relative to the reference item (mu_reference = 0)."""
    mu = pd.Series(0.0, index=items)
    se = pd.Series(0.0, index=items)
    for name in probit_result.params.index:
        mu[name] = np.sqrt(2) * probit_result.params[name]
        se[name] = np.sqrt(2) * probit_result.bse[name]
    return mu, se


# =============================================================================
# Mixed-effects model (multiple subjects)
# =============================================================================

def build_long_format_data(
    items: list[str],
    reference: str,
    comparisons: pd.DataFrame
) -> pd.DataFrame:
    """
    Convert trial-level data to long format for mixed-effects model.

    Parameters
    ----------
    items : list of str
        All item names (e.g., ["A", "B", "C", "D"]).
    reference : str
        Reference item whose lambda is fixed to 0.
    comparisons : DataFrame
        Trial-level data with columns:
        - subject: subject identifier
        - left_item: item shown on left
        - right_item: item shown on right
        - chose_left: 1 if subject chose left_item, 0 if chose right_item

    Returns
    -------
    DataFrame
        Long-format data with columns: subject, y, and one column per
        non-reference item with contrast coding (+1 for left, -1 for right).
    """
    non_ref_items = [it for it in items if it != reference]

    rows = []
    for _, trial in comparisons.iterrows():
        row = {
            'subject': trial['subject'],
            'y': int(trial['chose_left']),
        }
        for item in non_ref_items:
            if trial['left_item'] == item:
                row[item] = 1.0
            elif trial['right_item'] == item:
                row[item] = -1.0
            else:
                row[item] = 0.0
        rows.append(row)

    return pd.DataFrame(rows)


def simulate_multisubject_thurstone(
    mu_true: dict[str, float],
    pairs: list[tuple[str, str]],
    n_subjects: int,
    subject_sd: float,
    rng: np.random.Generator
) -> pd.DataFrame:
    """
    Simulate paired-comparison data for multiple subjects under Thurstone Case V.

    Parameters
    ----------
    mu_true : dict
        True scale values for each item (e.g., {"A": 0.0, "B": 1.2, "C": -0.5}).
    pairs : list of tuples
        All (left_item, right_item) pairs to compare.
    n_subjects : int
        Number of subjects.
    subject_sd : float
        Standard deviation of random intercepts (subject-level bias).
    rng : np.random.Generator
        Random number generator.

    Returns
    -------
    DataFrame
        Trial-level data with columns: subject, left_item, right_item, chose_left.
    """
    rows = []
    subject_intercepts = rng.normal(0, subject_sd, size=n_subjects)

    for subj_idx in range(n_subjects):
        bias = subject_intercepts[subj_idx]
        for left, right in pairs:
            # Thurstone Case V: X_i ~ N(mu_i, 1), chose left if X_left > X_right
            # Add subject bias to left item (simulates response bias)
            X_left = rng.normal(mu_true[left] + bias, 1.0)
            X_right = rng.normal(mu_true[right], 1.0)
            chose_left = int(X_left > X_right)
            rows.append({
                'subject': f'S{subj_idx:03d}',
                'left_item': left,
                'right_item': right,
                'chose_left': chose_left,
            })

    return pd.DataFrame(rows)


def fit_mixed_effects_glm(
    df_long: pd.DataFrame,
    items: list[str],
    reference: str,
    random_slopes: bool = False
):
    """
    Fit a mixed-effects logistic regression for paired comparisons.

    Parameters
    ----------
    df_long : DataFrame
        Long-format data from build_long_format_data().
    items : list of str
        All item names.
    reference : str
        Reference item (its column is omitted from df_long).
    random_slopes : bool
        If True, fit random slopes per item per subject. If False (default),
        fit only random intercepts.

    Returns
    -------
    Lmer
        Fitted pymer4 model.
    """
    if not HAS_PYMER4:
        raise ImportError("pymer4 not available. Use fit_gee() instead.")

    non_ref_items = [it for it in items if it != reference]
    fixed_effects = ' + '.join(non_ref_items)

    if random_slopes:
        random_effects = f"(0 + {fixed_effects} | subject)"
    else:
        random_effects = "(1 | subject)"

    formula = f"y ~ 0 + {fixed_effects} + {random_effects}"

    model = Lmer(formula, data=df_long, family='binomial')
    model.fit()
    return model


def fit_gee(
    df_long: pd.DataFrame,
    items: list[str],
    reference: str,
    link: str = 'logit'
):
    """
    Fit a GEE (population-averaged) logistic regression for paired comparisons.

    This is a pure-Python alternative to pymer4 that doesn't require R.
    GEE accounts for within-subject correlation and provides robust SEs.

    Parameters
    ----------
    df_long : DataFrame
        Long-format data from build_long_format_data().
    items : list of str
        All item names.
    reference : str
        Reference item (its column is omitted from df_long).
    link : str
        'logit' (default) or 'probit'.

    Returns
    -------
    GEEResults
        Fitted statsmodels GEE model.
    """
    non_ref_items = [it for it in items if it != reference]

    X = df_long[non_ref_items].values
    y = df_long['y'].values
    groups = df_long['subject'].values

    if link == 'logit':
        link_fn = sm.families.links.Logit()
    else:
        link_fn = sm.families.links.Probit()

    model = sm.GEE(
        y, X, groups=groups,
        family=sm.families.Binomial(link=link_fn),
        cov_struct=sm.cov_struct.Exchangeable()
    )
    result = model.fit()

    # Add column names to params for easier access
    result.params = pd.Series(result.params, index=non_ref_items)
    result.bse = pd.Series(result.bse, index=non_ref_items)

    return result


def thurstone_scale_values_gee(gee_result, items: list[str], reference: str, link: str = 'logit'):
    """
    Extract Thurstone scale values from a fitted GEE model.
    """
    mu = pd.Series(0.0, index=items)
    se = pd.Series(0.0, index=items)

    if link == 'probit':
        scale_factor = np.sqrt(2)
    else:
        # logit: approximate probit ≈ logit / 1.7, then * sqrt(2)
        scale_factor = np.sqrt(2) / 1.7

    for item in items:
        if item == reference:
            continue
        if item in gee_result.params.index:
            mu[item] = scale_factor * gee_result.params[item]
            se[item] = scale_factor * gee_result.bse[item]

    return mu, se


def thurstone_scale_values_mixed(model: Lmer, items: list[str], reference: str):
    """
    Extract Thurstone scale values from a fitted mixed-effects probit model.

    Note: pymer4 uses logit link by default. The coefficients are log-odds,
    not probit. For approximate Thurstone scaling, divide by 1.7 (probit ≈ logit/1.7)
    then multiply by sqrt(2).

    For exact Thurstone scaling, you'd need a probit link (not directly
    supported in lme4/pymer4 for GLMMs without custom families).
    """
    coefs = model.coefs
    mu = pd.Series(0.0, index=items)
    se = pd.Series(0.0, index=items)

    # Approximate conversion: probit ≈ logit / 1.7, then Thurstone: * sqrt(2)
    scale_factor = np.sqrt(2) / 1.7

    for item in items:
        if item == reference:
            continue
        if item in coefs.index:
            mu[item] = scale_factor * coefs.loc[item, 'Estimate']
            se[item] = scale_factor * coefs.loc[item, 'SE']

    return mu, se


def main():
    rng = np.random.default_rng(0)

    items = ["A", "B", "C"]
    reference = "A"
    pairs = [("A", "B"), ("A", "C"), ("B", "C")]
    n_per_pair = 200

    # Ground truth on the Thurstone latent scale (sigma = 1), unknown to the fit.
    mu_true = {"A": 0.0, "B": 1.2, "C": -0.5}

    wins = simulate_thurstone_case_v(mu_true, pairs, n_per_pair, rng)
    n_trials = np.full(len(pairs), n_per_pair)

    X = build_design_matrix(items, pairs, reference)

    print("Data (design matrix columns = lambda_B, lambda_C; A is reference = 0):")
    print(X.assign(wins=wins, n=n_trials, p_hat=(wins / n_trials).round(3)).to_string(index=False))
    print()

    # --- Bradley-Terry: logit link ---
    bt_fit = fit_paired_comparison_glm(X, wins, n_trials, sm.families.links.Logit)
    print("Bradley-Terry (logit-link) GLM: log-worth relative to A")
    for name in bt_fit.params.index:
        print(f"  lambda_{name} = {bt_fit.params[name]:6.3f}  (SE {bt_fit.bse[name]:.3f})")
    print()

    # --- Thurstone-Mosteller: probit link ---
    tm_fit = fit_paired_comparison_glm(X, wins, n_trials, sm.families.links.Probit)
    print("Thurstone-Mosteller (probit-link) GLM: raw coefficients relative to A")
    for name in tm_fit.params.index:
        print(f"  lambda_{name} = {tm_fit.params[name]:6.3f}  (SE {tm_fit.bse[name]:.3f})")
    print()

    mu_hat, se_hat = thurstone_scale_values(tm_fit, items, reference)
    mu_true_series = pd.Series(mu_true)

    print("Thurstone scale values mu_i = sqrt(2) * lambda_i (relative to A = 0):")
    report = pd.DataFrame({
        "true_mu": mu_true_series,
        "estimated_mu": mu_hat,
        "SE": se_hat,
    })
    print(report.to_string(float_format=lambda v: f"{v:6.3f}"))
    print()
    print("(SEs above are for the 'A fixed at 0' parameterization. Re-centering")
    print(" to mean-zero shifts all values by a constant with correlated")
    print(" uncertainty across items, so SEs would need to be recomputed via")
    print(" the delta method rather than just re-used.)")


def demo_mixed_effects():
    """Demonstrate mixed-effects paired comparison model with multiple subjects."""
    rng = np.random.default_rng(42)

    items = ["A", "B", "C", "D"]
    reference = "A"
    # All pairwise comparisons
    pairs = [(i, j) for idx, i in enumerate(items) for j in items[idx + 1:]]

    n_subjects = 80
    subject_sd = 0.3  # Random intercept SD (response bias variability)

    # Ground truth on the Thurstone latent scale
    mu_true = {"A": 0.0, "B": 1.2, "C": -0.5, "D": 0.8}

    print(f"Simulating {n_subjects} subjects, {len(pairs)} pairs each "
          f"({n_subjects * len(pairs)} total trials)")
    print(f"True scale values: {mu_true}")
    print(f"Subject random intercept SD: {subject_sd}")
    print()

    # Simulate trial-level data
    comparisons = simulate_multisubject_thurstone(
        mu_true, pairs, n_subjects, subject_sd, rng
    )
    print(f"Data shape: {comparisons.shape}")
    print(comparisons.head(10).to_string(index=False))
    print()

    # Convert to long format
    df_long = build_long_format_data(items, reference, comparisons)
    print("Long-format design matrix (first 10 rows):")
    print(df_long.head(10).to_string(index=False))
    print()

    # --- GEE (no R required) ---
    print("=" * 50)
    print("GEE (population-averaged, no R required)")
    print("=" * 50)
    print()

    gee_result = fit_gee(df_long, items, reference, link='logit')

    print("Fixed effects (log-odds scale):")
    print(pd.DataFrame({
        'Estimate': gee_result.params,
        'SE': gee_result.bse,
        'z': gee_result.tvalues,
        'p': gee_result.pvalues,
    }).to_string(float_format=lambda v: f"{v:6.3f}"))
    print()

    print(f"Estimated within-subject correlation: {gee_result.cov_struct.dep_params:.3f}")
    print()

    mu_hat, se_hat = thurstone_scale_values_gee(gee_result, items, reference)
    mu_true_series = pd.Series(mu_true)

    print("Approximate Thurstone scale values (logit/1.7 * sqrt(2)):")
    report = pd.DataFrame({
        "true_mu": mu_true_series,
        "estimated_mu": mu_hat,
        "SE": se_hat,
    })
    print(report.to_string(float_format=lambda v: f"{v:6.3f}"))
    print()

    # --- pymer4 (if available) ---
    if HAS_PYMER4:
        print("=" * 50)
        print("Mixed-effects GLMM via pymer4 (requires R)")
        print("=" * 50)
        print()
        print("Formula: y ~ 0 + B + C + D + (1 | subject)")
        print()

        try:
            model = fit_mixed_effects_glm(df_long, items, reference, random_slopes=False)

            print("Fixed effects (log-odds scale):")
            print(model.coefs[['Estimate', 'SE', 'Sig']].to_string())
            print()

            print("Random effects variance:")
            print(model.ranef_var)
            print()

            mu_hat, se_hat = thurstone_scale_values_mixed(model, items, reference)
            print("Approximate Thurstone scale values:")
            report = pd.DataFrame({
                "true_mu": mu_true_series,
                "estimated_mu": mu_hat,
                "SE": se_hat,
            })
            print(report.to_string(float_format=lambda v: f"{v:6.3f}"))
        except Exception as e:
            print(f"pymer4 failed: {e}")
    else:
        print("(pymer4 not available - skipping GLMM demo)")


if __name__ == "__main__":
    main()
    print("\n" + "=" * 70 + "\n")
    demo_mixed_effects()
