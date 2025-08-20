# Feature 2001: Income Management System

**Description**: Users can input, edit, and manage their income sources including gross income, net income, and bonus income. This information is editable in the budget configuration page and integrates with budgeting calculations.

**Stories**:
- Story 2001-0001: As a user, I want to add multiple income sources (gross, net, bonus) so I can track all my earnings.
- Story 2001-0002: As a user, I want to edit my income amounts in the budget config page.
- Story 2001-0003: As a user, I want to view my total income breakdown in the budget dashboard.
- Story 2001-0004: As a user, I want to categorize income by type (salary, freelance, investments, etc.).
- Story 2001-0005: As a user, I want to set income frequency (weekly, bi-weekly, monthly, annually).

**Solution**:
- Create new `Income` model with fields: amount, type, frequency, source_name, is_bonus
- Add API endpoints: POST/PUT/GET/DELETE for income management
- Integrate income data with budget calculation engine
- Add income management UI to budget configuration page
- Display income breakdown in dashboard with totals and percentages
