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

// Feature 2001 - Income types
export interface Income {
  id: number;
  amount: number;
  type?: string | null;
  frequency: 'weekly' | 'bi-weekly' | 'biweekly' | 'monthly' | 'annually' | 'yearly';
  source_name: string;
  is_bonus: boolean;
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

// Feature 1004 - Budget Analytics Types
export interface BudgetVarianceItem {
  category_id: number;
  category_name: string;
  budget_limit: number;
  spent_amount: number;
  variance_amount: number;
  variance_percentage: number;
  status: 'over' | 'warning' | 'under' | 'no_budget';
  recommendation: string;
}

export interface BudgetVarianceResponse {
  period: { start_date: string; end_date: string };
  categories: BudgetVarianceItem[];
  summary: {
    total_budgeted: number;
    total_spent: number;
    overall_progress: number;
    avg_variance_percentage: number;
    categories_over: number;
    categories_warning: number;
    categories_under: number;
  };
  generated_at: string;
}

export interface SpendingPatternsResponse {
  period: { start_date: string; end_date: string; days: number };
  top_categories: Array<{
    category_id: number;
    category_name: string;
    total_spent: number;
    share_percentage: number;
  }>;
  spending_spikes: Array<{
    category_id: number;
    category_name: string;
    last7_spent: number;
    prior7_spent: number;
    spike_ratio: number;
  }>;
  generated_at: string;
}

export interface ForecastItem {
  category_id: number;
  category_name: string;
  budget_limit: number;
  spent_to_date: number;
  daily_pace: number;
  forecasted_spend: number;
  projected_over_amount: number;
  status: 'projected_over' | 'tight' | 'on_track';
}

export interface ForecastsResponse {
  period: { start_date: string; end_date: string; days_elapsed: number; total_days: number };
  forecasts: ForecastItem[];
  generated_at: string;
}

export interface RecommendationsResponse {
  recommendations: Array<{ category_id: number; category_name: string; recommendations: string[] }>;
  generated_at: string;
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

export interface IncomeFormData {
  amount: number;
  type?: string;
  frequency: 'weekly' | 'bi-weekly' | 'biweekly' | 'monthly' | 'annually' | 'yearly';
  source_name: string;
  is_bonus?: boolean;
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

// Intelligent Alerts (Feature 1003)
export interface AlertItem {
  id: number;
  type: 'budget_threshold' | 'anomaly' | 'health' | 'pace' | 'variance' | string;
  category_id?: number;
  category_name?: string;
  severity: 'high' | 'medium' | 'low';
  message: string;
  channels: string[];
  status: 'active' | 'dismissed' | 'snoozed';
  snooze_until?: string | null;
  metadata?: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface AlertCounts {
  total: number;
  high_priority: number;
  medium_priority: number;
  low_priority: number;
}

export interface AlertListResponse {
  alerts: AlertItem[];
  counts: AlertCounts;
  generated_at: string;
}

export interface NotificationPreferences {
  in_app_enabled: boolean;
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  quiet_hours_start?: string | null;
  quiet_hours_end?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface AnomalyDetectionResponse {
  category_id: number;
  amount: number;
  average_daily: number;
  multiplier_threshold: number;
  is_anomaly: boolean;
  alert?: AlertItem;
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

// ============================================================================
// BUDGET METHODOLOGY TYPES (Feature 1005)
// ============================================================================

export interface BudgetMethodology {
  id: number;
  name: string;
  description: string;
  methodology_type: 'zero_based' | 'percentage_based' | 'envelope';
  is_active: boolean;
  is_default: boolean;
  configuration: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface BudgetMethodologyFormData {
  name: string;
  description: string;
  methodology_type: 'zero_based' | 'percentage_based' | 'envelope';
  is_active: boolean;
  is_default: boolean;
  configuration: Record<string, any>;
}

// Configuration types for different methodologies
export interface ZeroBasedConfiguration {
  // Zero-based budgeting typically doesn't need specific configuration
}

export interface PercentageBasedConfiguration {
  needs_percentage: number;     // e.g., 50 for 50/30/20 rule
  wants_percentage: number;     // e.g., 30 for 50/30/20 rule
  savings_percentage: number;   // e.g., 20 for 50/30/20 rule
}

export interface EnvelopeConfiguration {
  allow_envelope_transfer: boolean;
  rollover_unused: boolean;
  max_transfer_percentage?: number;
}

// Calculation result types
export interface BudgetAllocation {
  category_id: number;
  category_name: string;
  priority: string;
  allocated_amount: number;
  percentage_of_income: number;
  category_type?: string; // For percentage-based (needs/wants/savings)
}

export interface EnvelopeAllocation {
  category_id: number;
  category_name: string;
  priority: string;
  envelope_amount: number;
  percentage_of_income: number;
  envelope_status: string;
}

export interface ZeroBasedCalculationResult {
  methodology: string;
  total_income: number;
  allocations: BudgetAllocation[];
  unallocated: number;
  total_allocated: number;
  recommendations: string[];
}

export interface PercentageBasedCalculationResult {
  methodology: string;
  total_income: number;
  allocations: BudgetAllocation[];
  category_breakdown: {
    needs: {
      budget: number;
      allocated: number;
      remaining: number;
      categories: BudgetAllocation[];
    };
    wants: {
      budget: number;
      allocated: number;
      remaining: number;
      categories: BudgetAllocation[];
    };
    savings: {
      budget: number;
      allocated: number;
      remaining: number;
      categories: BudgetAllocation[];
    };
  };
  recommendations: string[];
}

export interface EnvelopeCalculationResult {
  methodology: string;
  total_income: number;
  envelopes: EnvelopeAllocation[];
  total_allocated: number;
  unallocated: number;
  recommendations: string[];
}

export type MethodologyCalculationResult = 
  | ZeroBasedCalculationResult 
  | PercentageBasedCalculationResult 
  | EnvelopeCalculationResult;

export interface MethodologyCalculationResponse {
  calculation_result: MethodologyCalculationResult;
  generated_at: string;
}

export interface MethodologyApplicationResponse {
  message: string;
  calculation_result: MethodologyCalculationResult;
  auto_updated: boolean;
  generated_at: string;
}

export interface MethodologyValidationResponse {
  methodology_id: number;
  methodology_name: string;
  is_valid: boolean;
  error_message: string | null;
  configuration: Record<string, any>;
}

export interface MethodologyComparison {
  methodology_id: number;
  methodology_name: string;
  methodology_type: string;
  calculation_result: MethodologyCalculationResult;
}

export interface MethodologyComparisonResponse {
  comparisons: MethodologyComparison[];
  total_income: number;
  generated_at: string;
}

export interface MethodologyRecommendation {
  methodology_type: 'zero_based' | 'percentage_based' | 'envelope';
  reason: string;
  confidence: number;
  best_for: string;
}

export interface UserFinancialProfile {
  total_income: number;
  total_expenses: number;
  savings_rate: number;
  categories_count: number;
  overspending_categories: number;
}

export interface MethodologyRecommendationsResponse {
  recommendations: MethodologyRecommendation[];
  user_profile: UserFinancialProfile;
  generated_at: string;
}

export interface MethodologyActivationResponse {
  message: string;
  methodology: BudgetMethodology;
}

// Form data for methodology operations
export interface MethodologyCalculationRequest {
  total_income?: number;
}

export interface MethodologyApplicationRequest {
  total_income?: number;
  auto_update: boolean;
}

export interface MethodologyComparisonRequest {
  methodology_ids: number[];
  total_income?: number;
}

// Budget Goals Types (Feature 1006)
export interface BudgetGoal {
  id: number;
  name: string;
  description?: string;
  target_amount: number;
  current_amount: number;
  deadline?: string;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
  categories: Category[];
}

export interface BudgetGoalFormData {
  name: string;
  description?: string;
  target_amount: number;
  deadline?: string;
}

export interface BudgetGoalResponse {
  goals: BudgetGoal[];
}

export interface AllocateCategoryData {
  category_id: number;
}