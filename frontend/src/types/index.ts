// Type definitions for Personal Finance App

export interface Category {
  id: number;
  name: string;
  type: 'income' | 'expense';
  color: string;
  // Enhanced Budget Fields (Feature 1001)
  budget_limit?: number;
  budget_period?: 'daily' | 'weekly' | 'monthly' | 'yearly';
  budget_type?: 'fixed' | 'percentage' | 'rolling_average';
  budget_priority?: 'critical' | 'essential' | 'important' | 'discretionary';
  budget_percentage?: number;
  budget_rolling_months?: number;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: number;
  date: string;
  amount: number;
  category_id: number;
  category_name?: string;
  category_color?: string;
  description: string;
  type: 'income' | 'expense';
  is_income: boolean;
  is_expense: boolean;
  absolute_amount: number;
  created_at: string;
  updated_at: string;
}

export interface Investment {
  id: number;
  asset_name: string;
  asset_type: string;
  quantity: number;
  purchase_price: number;
  current_price: number;
  purchase_date: string;
  total_invested: number;
  current_value: number;
  total_gain_loss: number;
  gain_loss_percentage: number;
  is_profitable: boolean;
  created_at: string;
  updated_at: string;
}

export interface DashboardData {
  financial_summary: {
    total_income: number;
    total_expenses: number;
    net_income: number;
  };
  investment_summary: {
    total_value: number;
    total_gain_loss: number;
  };
  expense_breakdown: Array<{
    name: string;
    color: string;
    total: number;
  }>;
  recent_transactions: Transaction[];
}

export interface SpendingTrends {
  period: string;
  start_date: string;
  end_date: string;
  trends: Array<{
    month: string;
    total: number;
  }>;
}

export interface InvestmentPerformance {
  total_investments: number;
  performance_data: Array<{
    asset_name: string;
    asset_type: string;
    total_invested: number;
    current_value: number;
    total_gain_loss: number;
    gain_loss_percentage: number;
    is_profitable: boolean;
  }>;
}

export interface PaginationInfo {
  page: number;
  per_page: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface TransactionsResponse {
  transactions: Transaction[];
  pagination: PaginationInfo;
}

export interface ApiError {
  error: string;
}

// Form data types
export interface TransactionFormData {
  date: string;
  amount: number;
  category_id: number;
  description: string;
  type: 'income' | 'expense';
}

export interface CategoryFormData {
  name: string;
  type: 'income' | 'expense';
  color: string;
}

export interface InvestmentFormData {
  asset_name: string;
  asset_type: string;
  quantity: number;
  purchase_price: number;
  current_price?: number;
  purchase_date: string;
}

// Budget-related types
export interface BudgetSuggestion {
  category_id: number;
  category_name: string;
  suggested_amount: number;
  reasoning: string;
  confidence_score: number;
}

export interface BudgetProgress {
  category_id: number;
  category_name: string;
  budget_limit: number;
  spent_amount: number;
  remaining_amount: number;
  spent_percentage: number;
  status: 'under' | 'warning' | 'over' | 'critical';
  days_remaining: number;
  daily_pace: number;
  projected_overspend: number;
}

// Advanced Budget Tracking Types (Feature 1002)
export interface AdvancedBudgetProgress extends BudgetProgress {
  health_score: number;
  period_info: {
    start_date: string;
    end_date: string;
    total_days: number;
    days_elapsed: number;
    days_remaining: number;
  };
  pace_analysis: {
    daily_pace: number;
    expected_daily: number;
    pace_ratio: number;
    predicted_overspend: number;
  };
  variance_analysis: {
    expected_spent: number;
    variance_amount: number;
    variance_percentage: number;
  };
}

export interface BudgetHistoricalTrends {
  period: string;
  period_start: string;
  period_end: string;
  categories: Array<{
    category_id: number;
    category_name: string;
    budget_limit: number;
    spent_amount: number;
    spent_percentage: number;
    health_score: number;
  }>;
  total_budgeted: number;
  total_spent: number;
  total_remaining: number;
  overall_progress: number;
}

export interface TransactionBudgetImpact {
  transaction_id: number;
  transaction_amount: number;
  category_name: string;
  budget_limit: number;
  spending_before: number;
  spending_after: number;
  percentage_before: number;
  percentage_after: number;
  percentage_change: number;
  severity: 'low' | 'warning' | 'critical' | 'none';
  impact_message: string;
  recommendations: string[];
}

export interface BudgetPerformanceMetrics {
  overall_score: number;
  categories_tracked: number;
  score_interpretation: string;
}

export interface BudgetPredictiveAlert {
  type: 'pace' | 'variance' | 'health' | 'warning';
  category_id: number;
  category_name: string;
  severity: 'high' | 'medium' | 'low';
  message: string;
  current_pace?: number;
  expected_pace?: number;
  days_to_overspend?: number;
  predicted_overspend?: number;
  expected_spent?: number;
  actual_spent?: number;
  variance_amount?: number;
  health_score?: number;
  recommendation?: string;
}

export interface AdvancedBudgetProgressResponse {
  progress: AdvancedBudgetProgress[];
  summary: {
    total_budgeted: number;
    total_spent: number;
    total_remaining: number;
    overall_progress: number;
    categories_count: number;
    categories_over_budget: number;
    categories_warning: number;
    categories_under_budget: number;
    average_health_score: number;
    performance_score: number;
  };
  alerts: Array<{
    type: string;
    category: string;
    message: string;
    severity: string;
  }>;
  generated_at: string;
}

export interface BudgetHistoricalTrendsResponse {
  trends: BudgetHistoricalTrends[];
  period_months: number;
  generated_at: string;
}

export interface TransactionBudgetImpactResponse {
  impact_analysis: TransactionBudgetImpact;
  generated_at: string;
}

export interface BudgetPerformanceResponse {
  performance: BudgetPerformanceMetrics;
  generated_at: string;
}

export interface BudgetPredictiveAlertsResponse {
  alerts: BudgetPredictiveAlert[];
  total_alerts: number;
  high_priority: number;
  medium_priority: number;
  generated_at: string;
}

export interface BudgetSummary {
  total_budgeted: number;
  total_spent: number;
  total_remaining: number;
  overall_progress: number;
  categories_count: number;
  categories_over_budget: number;
  categories_warning: number;
  categories_under_budget: number;
}

export interface EffectiveBudgetCalculation {
  category_id: number;
  category_name: string;
  effective_budget: number;
  calculation_method: string;
  factors: {
    total_income?: number;
    historical_average?: number;
    percentage_used?: number;
  };
}

export interface BudgetSuggestionsResponse {
  suggestions: BudgetSuggestion[];
  total_suggestions: number;
  generated_at: string;
}

export interface BudgetProgressResponse {
  progress: BudgetProgress[];
  summary: BudgetSummary;
  generated_at: string;
}

export interface EffectiveBudgetResponse {
  calculations: EffectiveBudgetCalculation[];
  total_income: number;
  generated_at: string;
}

// Budget form data types
export interface BudgetFormData {
  category_id: number;
  budget_limit: number;
  budget_period: 'daily' | 'weekly' | 'monthly' | 'yearly';
  budget_type: 'fixed' | 'percentage' | 'rolling_average';
  budget_priority: 'critical' | 'essential' | 'important' | 'discretionary';
  budget_percentage?: number;
  budget_rolling_months?: number;
}

export interface BulkBudgetUpdateData {
  updates: Array<{
    category_id: number;
    budget_limit: number;
  }>;
  inflation_adjustment?: number;
}

// Chart data types
export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface LineChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    tension: number;
  }>;
}

export interface DoughnutChartData {
  labels: string[];
  datasets: Array<{
    data: number[];
    backgroundColor: string[];
    borderColor: string[];
    borderWidth: number;
  }>;
}

export interface BarChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor: string[];
    borderColor: string[];
    borderWidth: number;
  }>;
}
