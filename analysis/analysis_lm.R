# %%
library(tidyverse)
library(lme4)
library(lmerTest)
library(jsonlite)
library(broom.mixed)
library(ppcor)

# %%
# ancova of long term memory dprime on condition and encoding time
# including wm dprime as covariate

exclude_file <- "./output_data/excluded_sessions/exclude_sessions_v1.json"
excluded <- fromJSON(exclude_file)$to_exclude

# lm data
lm_data <- read.csv("./output_data/aggregated/aggregated_v1_lm.csv")
cat("n =", n_distinct(lm_data$session_id), "\n")

lm_data <- lm_data |>
  filter(
    !session_id %in% excluded,
    condition_name != "mixed"
  ) |>
  select(session_id, dprime, encoding_time, condition_name) |>
  rename(
    lm_dprime = dprime
  )

# wm data
wm_data <- read.csv("./output_data/aggregated/aggregated_v1_vs.csv")
wm_data <- wm_data |>
  filter(
    !session_id %in% excluded,
    condition_name != "mixed"
  ) |>
  select(session_id, condition_name, dprime, encoding_time) |>
  rename(
    wm_dprime = dprime
  )

combined_data <- lm_data |>
  inner_join(wm_data, by=c("session_id", "condition_name", "encoding_time")) |>
  mutate(
    encoding_time = factor(
      ifelse(encoding_time == 400, "short", "long"),
      levels = c("short", "long"),
      ordered = TRUE
    ),
    condition = factor(condition_name, levels = c("visual", "semantic"))
  )

model <- lmer(
  lm_dprime ~ condition * encoding_time + wm_dprime + (1 | session_id),
  data = combined_data
)

# Fixed effects table
write.csv(
  tidy(model),
  "./results/v1/lmm_lm_dprime_ancova_coefficients.csv",
  row.names = FALSE
)

anova_table <- as.data.frame(anova(model))
anova_table$term <- rownames(anova_table)
write.csv(
  anova_table,
  "./results/v1/lmm_lm_dprime_ancova.csv",
  row.names = FALSE
)

# %%
# interindividual difference in lm performance

exclude_file <- "./output_data/excluded_sessions/exclude_sessions_v1.json"
excluded <- fromJSON(exclude_file)$to_exclude

# lm data
lm_data <- read.csv("./output_data/aggregated/aggregated_v1_lm.csv")

lm_data <- lm_data |>
  filter(!session_id %in% excluded) |>
  summarise(
    lm_dprime = mean(dprime),
    .by = session_id
  )

# wm data
wm_data <- read.csv("./output_data/aggregated/aggregated_v1_vs.csv")
combined_data <- wm_data |>
  filter(
    !session_id %in% excluded,
    condition_name != "mixed"
  ) |>
  summarise(
    wm_dprime = mean(dprime), 
    .by = c(session_id, condition_name)
  ) |>
  pivot_wider(
    names_from = condition_name,
    values_from =  wm_dprime
  ) |>
  inner_join(lm_data, by = "session_id")

# save residuals
combined_data <- combined_data |>
  mutate(
    resid_lm_visual = residuals(lm(lm_dprime ~ visual)),
    resid_semantic = residuals(lm(semantic ~ visual)),
    resid_lm_semantic = residuals(lm(lm_dprime ~ semantic)),
    resid_visual = residuals(lm(visual ~ semantic))
  )

write.csv(
  combined_data, 
  "./figures/v1_final/lm_residuals.csv",
  row.names = FALSE
)

# partial correlations
pcor_result <- pcor(combined_data[, c("lm_dprime", "semantic", "visual")])
sink("./results/v1/partial_correlations.txt")
cat("=== Partial Correlations ===\n\n")
print(pcor_result)
sink()


#%%
# trial-by-trial logistic regression of long term accuracy on wm accuracy

# Load excluded sessions
exclude_file <- "./output_data/excluded_sessions/exclude_sessions_v1.json"
excluded <- fromJSON(exclude_file)$to_exclude

# Load data
long_data <- read_csv("./output_data/long/combined_data.csv")
long_data <- long_data |> filter(!session_id %in% excluded)


# Summary for plotting
lm_by_wm_accuracy <- long_data |>
  filter(condition_name != "mixed") |>
  mutate(condition_name = factor(condition_name, levels = c("visual", "semantic"))) |>
  drop_na(correct_wm) |>
  group_by(session_id, condition_name, correct_wm) |>
  summarise(correct_lm = mean(correct_lm, na.rm = TRUE), .groups = "drop")

ggplot(lm_by_wm_accuracy,
       aes(x = factor(correct_wm), y = correct_lm, fill = condition_name)) +
  geom_boxplot() + 
  scale_fill_manual(values = c("semantic" = "#EF5350", "visual" = "#26C6DA"))


# Boxplot
# ggplot(lm_by_wm_accuracy,
#        aes(x = factor(correct_wm) , y = correct_lm, fill = condition_name)) +
#   geom_boxplot()



# Prepare model data
model_data <- long_data |>
  filter(condition_name != "mixed") |>
  drop_na(correct_lm, correct_wm) |>
  mutate(correct_wm = factor(correct_wm, levels = c(FALSE, TRUE)))

# Logistic GLMM with random intercept per session
logit_model <- glmer(
  correct_lm ~ correct_wm * condition_name + (1 | session_id),
  data = model_data,
  family = binomial
)

summary(logit_model)

# Odds ratios with confidence intervals
exp(fixef(logit_model))
exp(confint(logit_model, method = "Wald")) 
tidy(logit_model) |> write_csv("./results/v1/log_regression_lm_wm.csv")

