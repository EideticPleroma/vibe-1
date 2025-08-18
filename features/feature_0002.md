# Feature 0002: Budget Progress Tracking

**Description**: Calculate and display current spending vs. budget for each category in the dashboard.

**Stories**:
- Story 0002-0001: As a user, I want to see spending progress (e.g., % used) for each budgeted category in the dashboard.
- Story 0002-0002: As a user, I want progress to update in real-time as transactions are added.

**Solution**:
- In get_dashboard_data, query spending per category and compare to budget_limit.
- Add budget_progress to dashboard response (e.g., {category: {spent: x, budget: y, percentage: z}}).
- Handle cases where budget is 0 or not set.
