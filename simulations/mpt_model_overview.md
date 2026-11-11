# Multinomial Processing Tree (MPT) Model for Memory Encoding

## Research Question

Does the relationship between semantic memory (ms) and visual memory (mv) change across encoding time conditions (short vs. long)?

We hypothesize that with longer encoding time, participants may differentially benefit in semantic vs. visual memory processes. The model estimates these memory parameters separately for each condition and tests whether their relationship differs.

---

## Experimental Design

- **Participants**: 80 subjects
- **Trials**: 26 per condition per encoding time (156 total per participant)
- **Encoding times**: Short vs. Long
- **Conditions**:
  - **S** (semantic only): Items encoded with semantic information
  - **V** (visual only): Items encoded with visual information
  - **SV** (semantic + visual): Items encoded with both types of information

---

## The MPT Model Structure

### Core Parameters

| Parameter | Description |
|-----------|-------------|
| **ms** | Semantic memory - probability of successfully encoding/retrieving semantic information |
| **mv** | Visual memory - probability of successfully encoding/retrieving visual information |
| **b** | Bias - tendency to respond "old" when both semantic and visual traces are present but conflict |

### Decision Trees and Hit Probability Equations

The model assumes a sequential decision process for each condition:

#### Condition S (Semantic Only)

```
item → [ms] → HIT (semantic memory succeeds)
     → [1-ms] → guess → [0.5] → HIT
                      → [0.5] → MISS
```

**P(hit|s) = ms + (1 - ms) × 0.5**

Interpretation: Either semantic memory succeeds directly, OR it fails and the participant guesses (50/50).

#### Condition V (Visual Only)

```
item → [mv] → HIT (visual memory succeeds)
     → [1-mv] → guess → [0.5] → HIT
                      → [0.5] → MISS
```

**P(hit|v) = mv + (1 - mv) × 0.5**

Interpretation: Same logic as condition S, but for visual memory.

#### Condition SV (Semantic + Visual)

This is the most complex tree, modeling the interaction between both memory types:

```
item → [ms] → semantic succeeds
            → [1-mv] → HIT (semantic alone suffices)
            → [mv] → both traces present → [b] → HIT (bias toward "old")
                                         → [1-b] → MISS (conflict leads to rejection)
     → [1-ms] → semantic fails
             → [1-mv] → guess → [0.5] → HIT
                              → [0.5] → MISS
             → [mv] → MISS (visual without semantic = rejection)
```

**P(hit|sv) = ms(1 - mv) + ms × mv × b + (1 - ms)(1 - mv) × 0.5**

Interpretation:
- **ms(1 - mv)**: Semantic succeeds, visual fails → respond "old"
- **ms × mv × b**: Both succeed, bias determines response
- **(1 - ms)(1 - mv) × 0.5**: Both fail → guess

Note: When semantic fails but visual succeeds, the model assumes rejection (MISS), reflecting that visual-only information without semantic context may be perceived as unfamiliar.

---

## Hierarchical Bayesian Model

### Why Hierarchical?

We have repeated measurements from multiple participants. A hierarchical model:
1. Estimates individual variation (subject-level parameters)
2. Estimates population-level effects (group means)
3. Allows partial pooling - extreme individual estimates are pulled toward the group mean

### Why Logit Scale?

Memory parameters (ms, mv, b) are probabilities bounded between 0 and 1. Working on the logit scale:
1. Transforms probabilities to unbounded (-∞, +∞) scale
2. Makes Normal priors appropriate
3. Prevents impossible values during sampling
4. Allows meaningful comparisons (differences on logit scale = log odds ratios)

The inverse logit (sigmoid) function maps back to probability:

```
probability = 1 / (1 + exp(-logit_value))
```

### Non-Centered Parameterization

We use non-centered parameterization to avoid "funnel" problems in MCMC sampling:

```
# Instead of:
ms_subj ~ Normal(mu_ms, sigma_ms)  # centered - problematic

# We use:
ms_offset ~ Normal(0, 1)           # standard normal
ms_subj = invlogit(mu_ms + sigma_ms × ms_offset)  # non-centered
```

This separates the group-level parameters from the individual offsets, making sampling more efficient when:
- There's limited data per subject
- The between-subject variance is small relative to the group mean

### Model Specification

```python
# Group-level priors (logit scale)
mu_ms ~ Normal(0, 1)    # shape: (2,) for [short, long]
mu_mv ~ Normal(0, 1)    # shape: (2,) for [short, long]
mu_b ~ Normal(0, 1)     # single value (same across conditions)

# Between-subject SDs
sigma_ms ~ Exponential(2)
sigma_mv ~ Exponential(2)
sigma_b ~ Exponential(2)

# Subject offsets (shared across encoding times)
ms_offset ~ Normal(0, 1)    # shape: (n_participants,)
mv_offset ~ Normal(0, 1)
b_offset ~ Normal(0, 1)

# Subject-level parameters
ms_subj = invlogit(mu_ms[:, None] + sigma_ms × ms_offset)  # shape: (2, n_participants)
mv_subj = invlogit(mu_mv[:, None] + sigma_mv × mv_offset)
b_subj = invlogit(mu_b + sigma_b × b_offset)

# Likelihoods
hits_s ~ Binomial(n_trials, P(hit|s))
hits_v ~ Binomial(n_trials, P(hit|v))
hits_sv ~ Binomial(n_trials, P(hit|sv))
```

### Prior Interpretation

With `Normal(0, 1)` on the logit scale:
- Median probability: 0.50
- 95% prior interval: approximately [0.12, 0.88]

This is a weakly informative prior that:
- Centers on chance (0.5)
- Allows the full range of reasonable probability values
- Is symmetric on the logit scale

---

## Key Contrast: Testing the Hypothesis

The main research question translates to: **Does c = logit(mv) - logit(ms) differ between short and long encoding?**

We compute:

```python
c_logit = mu_mv - mu_ms          # shape: (2,) for [short, long]
c_diff = c_logit[0] - c_logit[1] # short minus long
```

### Interpretation of c_diff

| Result | Interpretation |
|--------|----------------|
| c_diff > 0 | Visual memory benefits relatively more than semantic in short encoding |
| c_diff < 0 | Semantic memory benefits relatively more than visual in short encoding |
| c_diff ≈ 0 | The mv/ms relationship is similar across encoding times |

If the 94% HDI of c_diff excludes zero, we have evidence that the relationship between semantic and visual memory differs across encoding conditions.

---

## Data Structure

The input data is a DataFrame with columns:

| Column | Description |
|--------|-------------|
| `subject_id` | Participant identifier (0 to n_participants-1) |
| `condition` | Trial type: "s", "v", or "sv" |
| `encoding_time` | "short" or "long" |
| `hits` | Number of correct responses |
| `n_trials` | Total trials (26) |

For model fitting, we use indexing:
- `enc_idx`: 0 = short, 1 = long
- `subj_idx`: participant index

This allows efficient vectorized computation without separate variables per condition.

---

## Files in This Directory

| File | Description |
|------|-------------|
| `multinomial_tree_simulation.py` | Simulation and model fitting code |
| `mpt_dashboard.html` | Interactive visualization of hit probabilities |
| `mpt_trees.svg` | Standalone SVG of the MPT decision trees |
| `mpt_model_overview.md` | This documentation file |
