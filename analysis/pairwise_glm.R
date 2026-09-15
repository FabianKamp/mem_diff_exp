# Paired-comparison GLM (Bradley-Terry / Thurstone-Mosteller)
# Following Critchlow & Fligner (1991, Psychometrika 56, 517-533)
#
# Fits win/loss data for a set of items as a binomial GLM:
#     link( P(i beats j) ) = lambda_i - lambda_j
#
# - logit link  -> Bradley-Terry model, lambda_i = log-worth of item i
# - probit link -> Thurstone-Mosteller Case V model; lambda_i is then
#                  rescaled by sqrt(2) to give Thurstone's latent
#                  "scale value" mu_i (under the sigma = 1 convention).
#
# Mixed-effects extension uses lme4::glmer for random intercepts/slopes.

library(lme4)
library(dplyr)
library(tidyr)

# =============================================================================
# Design matrix construction
# =============================================================================

build_design_matrix <- function(items, pairs, reference) {
    # One row per compared pair (i, j): +1 in item i's column, -1 in
    # item j's column. The reference item's column is omitted.
    non_ref_items <- items[items != reference]
    n_pairs <- nrow(pairs)

    X <- matrix(0, nrow = n_pairs, ncol = length(non_ref_items))
    colnames(X) <- non_ref_items

    for (row in seq_len(n_pairs)) {
        left <- pairs$left[row]
        right <- pairs$right[row]
        if (left %in% non_ref_items) {
            X[row, left] <- 1
        }
        if (right %in% non_ref_items) {
            X[row, right] <- -1
        }
    }

    as.data.frame(X)
}


aggregate_by_subject <- function(comparisons) {
    # Aggregate trial-level data to win counts per pair per subject.
    #
    # Returns: data.frame with columns:
    #   - subject
    #   - left_item, right_item (the pair)
    #   - wins: number of times subject chose left_item
    #   - n: total comparisons for this pair (should be 1 per subject usually)

    comparisons %>%
        group_by(subject, left_item, right_item) %>%
        summarise(
            wins = sum(chose_left),
            n = n(),
            .groups = "drop"
        )
}


aggregate_across_subjects <- function(comparisons) {
    # Aggregate trial-level data to win counts per pair (pooled across subjects).
    #
    # Returns: data.frame with columns:
    #   - left_item, right_item (the pair)
    #   - wins: total times left_item was chosen
    #   - n: total comparisons
    #   - p_hat: proportion choosing left

    comparisons %>%
        group_by(left_item, right_item) %>%
        summarise(
            wins = sum(chose_left),
            n = n(),
            .groups = "drop"
        ) %>%
        mutate(p_hat = wins / n)
}


build_long_format_data <- function(items, reference, comparisons) {
    # Convert trial-level data to long format for mixed-effects model.
    #
    # comparisons: data.frame with columns:
    #   - subject: subject identifier
    #   - left_item: item shown on left
    #   - right_item: item shown on right
    #   - chose_left: 1 if subject chose left_item, 0 if chose right_item
    #
    # Returns: data.frame with columns: subject, y, and one column per
    #          non-reference item with contrast coding (+1 for left, -1 for right).

    non_ref_items <- items[items != reference]

    df <- comparisons %>%
        mutate(y = chose_left)

    # Add contrast-coded columns for each non-reference item
    for (item in non_ref_items) {
        df[[item]] <- ifelse(df$left_item == item, 1,
                             ifelse(df$right_item == item, -1, 0))
    }

    df %>% select(subject, y, all_of(non_ref_items))
}


# =============================================================================
# Simulation
# =============================================================================

simulate_multisubject_thurstone <- function(mu_true, pairs, n_subjects,
                                             subject_sd = 0, seed = NULL) {
    # Simulate paired-comparison data for multiple subjects under Thurstone Case V.
    #
    # mu_true: named vector of true scale values (e.g., c(A=0, B=1.2, C=-0.5))
    # pairs: data.frame with columns 'left' and 'right'
    # n_subjects: number of subjects
    # subject_sd: SD of random intercepts (response bias)

    if (!is.null(seed)) set.seed(seed)

    subject_intercepts <- rnorm(n_subjects, mean = 0, sd = subject_sd)

    rows <- list()
    idx <- 1

    for (subj_idx in seq_len(n_subjects)) {
        bias <- subject_intercepts[subj_idx]
        for (pair_idx in seq_len(nrow(pairs))) {
            left <- pairs$left[pair_idx]
            right <- pairs$right[pair_idx]

            # Thurstone Case V: X_i ~ N(mu_i, 1)
            X_left <- rnorm(1, mean = mu_true[left] + bias, sd = 1)
            X_right <- rnorm(1, mean = mu_true[right], sd = 1)
            chose_left <- as.integer(X_left > X_right)

            rows[[idx]] <- data.frame(
                subject = sprintf("S%03d", subj_idx),
                left_item = left,
                right_item = right,
                chose_left = chose_left,
                stringsAsFactors = FALSE
            )
            idx <- idx + 1
        }
    }

    bind_rows(rows)
}


# =============================================================================
# Model fitting
# =============================================================================

fit_glm_aggregated <- function(X, wins, n_trials, link = "logit") {
    # Fit aggregated binomial GLM (no random effects).
    # X: design matrix
    # wins: vector of win counts
    # n_trials: vector of trial counts

    df <- cbind(X, wins = wins, n = n_trials)
    formula_str <- paste0("cbind(wins, n - wins) ~ 0 + ",
                          paste(colnames(X), collapse = " + "))

    glm(as.formula(formula_str), data = df, family = binomial(link = link))
}


fit_glmm <- function(df_long, items, reference, link = "logit",
                     random_slopes = FALSE) {
    # Fit mixed-effects logistic/probit regression for paired comparisons.
    #
    # df_long: long-format data from build_long_format_data()
    # items: all item names
    # reference: reference item (column omitted)
    # link: "logit" or "probit"
    # random_slopes: if TRUE, fit random slopes per item per subject

    non_ref_items <- items[items != reference]
    fixed_effects <- paste(non_ref_items, collapse = " + ")

    if (random_slopes) {
        random_effects <- sprintf("(0 + %s | subject)", fixed_effects)
    } else {
        random_effects <- "(1 | subject)"
    }

    formula_str <- sprintf("y ~ 0 + %s + %s", fixed_effects, random_effects)

    glmer(as.formula(formula_str), data = df_long,
          family = binomial(link = link),
          control = glmerControl(optimizer = "bobyqa"))
}


# =============================================================================
# Scale value extraction
# =============================================================================

thurstone_scale_values <- function(model, items, reference, link = "logit") {
    # Extract Thurstone scale values from a fitted model.
    #
    # For probit link: mu_i = sqrt(2) * lambda_i
    # For logit link: approximate via mu_i = sqrt(2) / 1.7 * lambda_i

    coefs <- fixef(model)
    se <- sqrt(diag(vcov(model)))

    if (link == "probit") {
        scale_factor <- sqrt(2)
    } else {
        # logit: approximate probit ≈ logit / 1.7
        scale_factor <- sqrt(2) / 1.7
    }

    mu <- setNames(rep(0, length(items)), items)
    se_out <- setNames(rep(0, length(items)), items)

    for (item in names(coefs)) {
        mu[item] <- scale_factor * coefs[item]
        se_out[item] <- scale_factor * se[item]
    }

    data.frame(
        item = items,
        mu = mu[items],
        se = se_out[items],
        row.names = NULL
    )
}


# =============================================================================
# Demo
# =============================================================================

demo <- function() {
    set.seed(42)

    items <- c("A", "B", "C", "D")
    reference <- "A"

    # All pairwise comparisons
    pairs <- expand.grid(left = items, right = items, stringsAsFactors = FALSE) %>%
        filter(left < right) %>%
        rename(left = left, right = right)

    n_subjects <- 80
    subject_sd <- 0.3

    # Ground truth on the Thurstone latent scale
    mu_true <- c(A = 0.0, B = 1.2, C = -0.5, D = 0.8)

    cat(sprintf("Simulating %d subjects, %d pairs each (%d total trials)\n",
                n_subjects, nrow(pairs), n_subjects * nrow(pairs)))
    cat("True scale values:", paste(names(mu_true), "=", mu_true, collapse = ", "), "\n")
    cat("Subject random intercept SD:", subject_sd, "\n\n")

    # Simulate trial-level data
    comparisons <- simulate_multisubject_thurstone(mu_true, pairs, n_subjects,
                                                    subject_sd, seed = 42)
    cat("Data shape:", nrow(comparisons), "x", ncol(comparisons), "\n")
    print(head(comparisons, 10))
    cat("\n")

    # --- Aggregate data ---
    cat(strrep("=", 50), "\n")
    cat("Aggregated data (pooled across subjects)\n")
    cat(strrep("=", 50), "\n\n")

    agg_pooled <- aggregate_across_subjects(comparisons)
    print(agg_pooled)
    cat("\n")

    cat("Per-subject aggregation (first 20 rows):\n")
    agg_subject <- aggregate_by_subject(comparisons)
    print(head(agg_subject, 20))
    cat("\n")

    cat("Summary of win proportions per pair:\n")
    summary_stats <- agg_subject %>%
        group_by(left_item, right_item) %>%
        summarise(
            mean_p = mean(wins / n),
            sd_p = sd(wins / n),
            n_subjects = n(),
            .groups = "drop"
        )
    print(summary_stats)
    cat("\n")

    # Convert to long format
    df_long <- build_long_format_data(items, reference, comparisons)
    cat("Long-format design matrix (first 10 rows):\n")
    print(head(df_long, 10))
    cat("\n")

    # --- Fit probit GLMM (exact Thurstone Case V) ---
    cat(strrep("=", 50), "\n")
    cat("Probit GLMM (exact Thurstone Case V)\n")
    cat(strrep("=", 50), "\n\n")

    model_probit <- fit_glmm(df_long, items, reference, link = "probit")

    cat("Model summary:\n")
    print(summary(model_probit))
    cat("\n")

    cat("Thurstone scale values (mu = sqrt(2) * lambda):\n")
    scale_vals <- thurstone_scale_values(model_probit, items, reference, link = "probit")
    scale_vals$true_mu <- mu_true[scale_vals$item]
    print(scale_vals)
    cat("\n")

    # --- Fit logit GLMM (Bradley-Terry) ---
    cat(strrep("=", 50), "\n")
    cat("Logit GLMM (Bradley-Terry)\n")
    cat(strrep("=", 50), "\n\n")

    model_logit <- fit_glmm(df_long, items, reference, link = "logit")

    cat("Model summary:\n")
    print(summary(model_logit))
    cat("\n")

    cat("Approximate Thurstone scale values (logit/1.7 * sqrt(2)):\n")
    scale_vals_logit <- thurstone_scale_values(model_logit, items, reference, link = "logit")
    scale_vals_logit$true_mu <- mu_true[scale_vals_logit$item]
    print(scale_vals_logit)

    invisible(list(
        model_probit = model_probit,
        model_logit = model_logit,
        data = df_long
    ))
}


# Run demo if executed directly
if (!interactive() || identical(environment(), globalenv())) {
    demo()
}
