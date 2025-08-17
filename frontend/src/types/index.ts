// Type definitions for Personal Finance App

export interface Category {
  id: number;
  name: string;
  type: 'income' | 'expense';
  color: string;
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
