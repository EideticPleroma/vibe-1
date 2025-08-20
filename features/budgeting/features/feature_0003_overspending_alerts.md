# Feature 0003: Overspending Alerts

**Description**: Generate alerts if spending exceeds 80% or 100% of budget.

**Stories**:
- Story 0003-0001: As a user, I want alerts in the dashboard if a category is over budget.
- Story 0003-0002: As a user, I want customizable alert thresholds (e.g., warning at 80%).

**Solution**:
- Add alert logic in dashboard: If spent > threshold * budget, add to alerts array in response.
- Default thresholds: warning at 80%, over at 100%.
