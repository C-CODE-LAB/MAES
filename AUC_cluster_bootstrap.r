# AUROC and AUPRC with 95% patient-cluster bootstrap confidence intervals
# Example: MAES prediction of a clinical deterioration event (CDE) within 6 hours.
# Each row is one eligible prediction timepoint. CHID identifies the patient.
data <- read.csv("path/to/cde_predictions.csv", colClasses = c(CHID = "character"))
score <- data$MAES
event <- data$EVENT_6  # 1 = CDE within 6 hours, 0 = no CDE within 6 hours
stopifnot(all(c("CHID", "MAES", "EVENT_6") %in% names(data)), is.numeric(score))

keep <- !is.na(data$CHID) & is.finite(score) & event %in% c(0, 1)
patient_id <- data$CHID[keep]
score <- score[keep]
event <- event[keep]

calculate_auc <- function(score, event) {
  if (!any(event == 1) || !any(event == 0)) {
    return(c(AUROC = NA_real_, AUPRC = NA_real_))
  }

  auroc <- as.numeric(pROC::roc(event, score, levels = c(0, 1),
                                direction = "<", quiet = TRUE)$auc)
  auprc <- PRROC::pr.curve(scores.class0 = score[event == 1],
                           scores.class1 = score[event == 0],
                           curve = FALSE, dg.compute = FALSE)$auc.integral
  c(AUROC = auroc, AUPRC = auprc)
}

# Point estimates use all eligible timepoints.
estimate <- calculate_auc(score, event)

# Draw patients with replacement. If drawn twice, all their rows enter twice.
rows_by_patient <- split(seq_along(event), patient_id)
n_patients <- length(rows_by_patient)
stopifnot(n_patients >= 2)
set.seed(20261029)
B <- 1000
draws <- matrix(NA_real_, nrow = B, ncol = 2, dimnames = list(NULL, names(estimate)))
for (b in seq_len(B)) {
  patients <- sample.int(n_patients, n_patients, replace = TRUE)
  rows <- unlist(rows_by_patient[patients], use.names = FALSE)
  draws[b, ] <- calculate_auc(score[rows], event[rows])
}

# Percentile CIs use replicates with both outcome classes.
valid <- complete.cases(draws)
ci <- matrix(NA_real_, nrow = 2, ncol = 2)
if (sum(valid) >= 20) {
  ci <- apply(draws[valid, , drop = FALSE], 2, quantile, probs = c(0.025, 0.975), type = 7)
}
print(data.frame(metric = names(estimate), estimate = unname(estimate),
                 lower_95 = unname(ci[1, ]), upper_95 = unname(ci[2, ]),
                 valid_replicates = sum(valid)), row.names = FALSE)
