# Feature 0001: Monthly Budget Planning

**Description**: Users can set monthly budget limits for each expense category, stored in the database and editable via API.

**Stories**:
- Story 0001-0001: As a user, I want to set a monthly budget for a category so I can plan my spending.
- Story 0001-0002: As a user, I want to update or remove a budget limit for a category.
- Story 0001-0003: As a user, I want to view all budget limits in the categories list.

**Solution**:
- Add a `budget_limit` field (Numeric) to the `Category` model (only for 'expense' types).
- Extend `/api/categories` endpoints: POST/PUT to include `budget_limit`, GET to return it.
- Validate: Budget limit must be positive, only for expenses.
