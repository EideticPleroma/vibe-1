// API service for Personal Finance App
// Handles all HTTP requests to the Flask backend

import axios, { AxiosResponse } from 'axios';
import {
  Category,
  Transaction,
  Investment,
  Income,
  DashboardData,
  SpendingTrends,
  InvestmentPerformance,
  BudgetVarianceResponse,
  SpendingPatternsResponse,
  ForecastsResponse,
  RecommendationsResponse,
  TransactionsResponse,
  TransactionFormData,
  CategoryFormData,
  InvestmentFormData,
  IncomeFormData,
  BudgetSuggestionsResponse,
  BudgetProgressResponse,
  EffectiveBudgetResponse,
  BudgetFormData,
  BulkBudgetUpdateData,
  AdvancedBudgetProgressResponse,
  BudgetHistoricalTrendsResponse,
  TransactionBudgetImpactResponse,
  BudgetPerformanceResponse,
  BudgetPredictiveAlertsResponse,
  AlertListResponse,
  AlertItem,
  NotificationPreferences,
  AnomalyDetectionResponse,
  ApiError
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.data?.error) {
      console.error('API Error:', error.response.data.error);
    } else {
      console.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Categories API
export const categoriesApi = {
  getAll: async (): Promise<Category[]> => {
    const response = await api.get<Category[]>('/categories');
    return response.data;
  },

  create: async (data: CategoryFormData): Promise<Category> => {
    const response = await api.post<Category>('/categories', data);
    return response.data;
  },

  update: async (id: number, data: Partial<CategoryFormData>): Promise<Category> => {
    const response = await api.put<Category>(`/categories/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/categories/${id}`);
    return response.data;
  },
};

// Transactions API
export const transactionsApi = {
  getAll: async (params?: {
    page?: number;
    per_page?: number;
    category_id?: number;
    type?: 'income' | 'expense';
    start_date?: string;
    end_date?: string;
  }): Promise<TransactionsResponse> => {
    const response = await api.get<TransactionsResponse>('/transactions', { params });
    return response.data;
  },

  create: async (data: TransactionFormData): Promise<Transaction> => {
    const response = await api.post<Transaction>('/transactions', data);
    return response.data;
  },

  update: async (id: number, data: Partial<TransactionFormData>): Promise<Transaction> => {
    const response = await api.put<Transaction>(`/transactions/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/transactions/${id}`);
    return response.data;
  },
};

// Investments API
export const investmentsApi = {
  getAll: async (): Promise<Investment[]> => {
    const response = await api.get<Investment[]>('/investments');
    return response.data;
  },

  create: async (data: InvestmentFormData): Promise<Investment> => {
    const response = await api.post<Investment>('/investments', data);
    return response.data;
  },

  update: async (id: number, data: Partial<InvestmentFormData>): Promise<Investment> => {
    const response = await api.put<Investment>(`/investments/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/investments/${id}`);
    return response.data;
  },
};

// Incomes API (Feature 2001)
export const incomesApi = {
  getAll: async (): Promise<Income[]> => {
    const response = await api.get<Income[]>('/incomes');
    return response.data;
  },

  create: async (data: IncomeFormData): Promise<Income> => {
    const response = await api.post<Income>('/incomes', data);
    return response.data;
  },

  update: async (id: number, data: Partial<IncomeFormData>): Promise<Income> => {
    const response = await api.put<Income>(`/incomes/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/incomes/${id}`);
    return response.data;
  },
};

// Dashboard API
export const dashboardApi = {
  getData: async (params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<DashboardData> => {
    const response = await api.get<DashboardData>('/dashboard', { params });
    return response.data;
  },
};

// Analytics API
export const analyticsApi = {
  getSpendingTrends: async (months: number = 6): Promise<SpendingTrends> => {
    const response = await api.get<SpendingTrends>('/analytics/spending-trends', {
      params: { months }
    });
    return response.data;
  },

  getInvestmentPerformance: async (): Promise<InvestmentPerformance> => {
    const response = await api.get<InvestmentPerformance>('/analytics/investment-performance');
    return response.data;
  },

  // Feature 1004 endpoints
  getBudgetVariance: async (params?: { start_date?: string; end_date?: string }): Promise<BudgetVarianceResponse> => {
    const response = await api.get<BudgetVarianceResponse>('/analytics/budget-variance', { params });
    return response.data;
  },

  getSpendingPatterns: async (days: number = 30): Promise<SpendingPatternsResponse> => {
    const response = await api.get<SpendingPatternsResponse>('/analytics/spending-patterns', { params: { days } });
    return response.data;
  },

  getForecasts: async (): Promise<ForecastsResponse> => {
    const response = await api.get<ForecastsResponse>('/analytics/forecasts');
    return response.data;
  },

  getRecommendations: async (): Promise<RecommendationsResponse> => {
    const response = await api.get<RecommendationsResponse>('/analytics/recommendations');
    return response.data;
  },
};

// Budget API
export const budgetApi = {
  getSuggestions: async (): Promise<BudgetSuggestionsResponse> => {
    const response = await api.get<BudgetSuggestionsResponse>('/budget/suggestions');
    return response.data;
  },

  getProgress: async (): Promise<BudgetProgressResponse> => {
    const response = await api.get<BudgetProgressResponse>('/budget/progress');
    return response.data;
  },

  calculateEffectiveBudget: async (params?: {
    total_income?: number;
  }): Promise<EffectiveBudgetResponse> => {
    const response = await api.get<EffectiveBudgetResponse>('/budget/calculate-effective', { params });
    return response.data;
  },

  updateCategoryBudget: async (categoryId: number, data: BudgetFormData): Promise<Category> => {
    const response = await api.put<Category>(`/categories/${categoryId}`, data);
    return response.data;
  },

  bulkUpdateBudgets: async (data: BulkBudgetUpdateData): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/budget/bulk-update', data);
    return response.data;
  },

  copyBudgetTemplate: async (params?: {
    inflation_adjustment?: number;
  }): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/budget/copy-template', params);
    return response.data;
  },

  // Advanced Budget Tracking APIs (Feature 1002)
  getAdvancedProgress: async (params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<AdvancedBudgetProgressResponse> => {
    const response = await api.get<AdvancedBudgetProgressResponse>('/budget/progress/advanced', { params });
    return response.data;
  },

  getHistoricalTrends: async (months: number = 6): Promise<BudgetHistoricalTrendsResponse> => {
    const response = await api.get<BudgetHistoricalTrendsResponse>('/budget/trends/historical', {
      params: { months }
    });
    return response.data;
  },

  getTransactionImpact: async (transactionId: number): Promise<TransactionBudgetImpactResponse> => {
    const response = await api.get<TransactionBudgetImpactResponse>(`/budget/transaction-impact/${transactionId}`);
    return response.data;
  },

  getPerformanceScore: async (): Promise<BudgetPerformanceResponse> => {
    const response = await api.get<BudgetPerformanceResponse>('/budget/performance-score');
    return response.data;
  },

  getPredictiveAlerts: async (): Promise<BudgetPredictiveAlertsResponse> => {
    const response = await api.get<BudgetPredictiveAlertsResponse>('/budget/predictive-alerts');
    return response.data;
  },
};

// Intelligent Alerts API (Feature 1003)
export const alertsApi = {
  list: async (params?: {
    status?: 'active' | 'dismissed' | 'snoozed';
    severity?: 'high' | 'medium' | 'low';
    type?: string;
    category_id?: number;
  }): Promise<AlertListResponse> => {
    const response = await api.get<AlertListResponse>('/alerts', { params });
    return response.data;
  },

  create: async (data: {
    type: string;
    message: string;
    category_id?: number;
    severity?: 'high' | 'medium' | 'low';
    channels?: string[];
    metadata?: Record<string, any>;
  }): Promise<AlertItem> => {
    const response = await api.post<AlertItem>('/alerts', data);
    return response.data;
  },

  dismiss: async (alertId: number): Promise<{ message: string; alert: AlertItem }> => {
    const response = await api.post<{ message: string; alert: AlertItem }>(`/alerts/${alertId}/dismiss`);
    return response.data;
  },

  snooze: async (alertId: number, hours: number = 24): Promise<{ message: string; alert: AlertItem }> => {
    const response = await api.post<{ message: string; alert: AlertItem }>(`/alerts/${alertId}/snooze`, { hours });
    return response.data;
  },

  getPreferences: async (): Promise<{ preferences: NotificationPreferences }> => {
    const response = await api.get<{ preferences: NotificationPreferences }>('/alerts/preferences');
    return response.data;
  },

  updatePreferences: async (
    prefs: Partial<NotificationPreferences>
  ): Promise<{ preferences: NotificationPreferences }> => {
    const response = await api.post<{ preferences: NotificationPreferences }>('/alerts/preferences', prefs);
    return response.data;
  },

  detectAnomaly: async (data: { category_id: number; amount: number; multiplier?: number }): Promise<AnomalyDetectionResponse> => {
    const response = await api.post<AnomalyDetectionResponse>('/alerts/anomalies/detect', data);
    return response.data;
  },
};

// Utility functions
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

export const formatPercentage = (value: number): string => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
};

export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const getCategoryColor = (category: Category | undefined): string => {
  return category?.color || '#6b7280';
};

export const isPositiveAmount = (amount: number): boolean => {
  return amount > 0;
};

export const getTransactionTypeColor = (type: 'income' | 'expense'): string => {
  return type === 'income' ? 'text-success-600' : 'text-danger-600';
};

export const getTransactionTypeIcon = (type: 'income' | 'expense'): string => {
  return type === 'income' ? '↑' : '↓';
};

// Error handling utilities
export const handleApiError = (error: any): string => {
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

export const isApiError = (error: any): error is ApiError => {
  return error && typeof error.error === 'string';
};

// ============================================================================
// BUDGET METHODOLOGY API (Feature 1005)
// ============================================================================

export const budgetMethodologyApi = {
  // Get all methodologies
  getAll: async (): Promise<BudgetMethodology[]> => {
    const response = await api.get('/budget/methodologies');
    return response.data;
  },

  // Get active methodology
  getActive: async (): Promise<BudgetMethodology | null> => {
    try {
      const response = await api.get('/budget/methodologies/active');
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  },

  // Create new methodology
  create: async (data: BudgetMethodologyFormData): Promise<BudgetMethodology> => {
    const response = await api.post('/budget/methodologies', data);
    return response.data;
  },

  // Update methodology
  update: async (id: number, data: Partial<BudgetMethodologyFormData>): Promise<BudgetMethodology> => {
    const response = await api.put(`/budget/methodologies/${id}`, data);
    return response.data;
  },

  // Delete methodology
  delete: async (id: number): Promise<void> => {
    await api.delete(`/budget/methodologies/${id}`);
  },

  // Activate methodology
  activate: async (id: number): Promise<MethodologyActivationResponse> => {
    const response = await api.post(`/budget/methodologies/${id}/activate`);
    return response.data;
  },

  // Calculate budget using methodology
  calculate: async (id: number, data?: MethodologyCalculationRequest): Promise<MethodologyCalculationResponse> => {
    const response = await api.post(`/budget/methodologies/${id}/calculate`, data || {});
    return response.data;
  },

  // Apply methodology to categories
  apply: async (id: number, data: MethodologyApplicationRequest): Promise<MethodologyApplicationResponse> => {
    const response = await api.post(`/budget/methodologies/${id}/apply`, data);
    return response.data;
  },

  // Validate methodology configuration
  validate: async (id: number): Promise<MethodologyValidationResponse> => {
    const response = await api.get(`/budget/methodologies/${id}/validate`);
    return response.data;
  },

  // Compare multiple methodologies
  compare: async (data: MethodologyComparisonRequest): Promise<MethodologyComparisonResponse> => {
    const response = await api.post('/budget/methodologies/compare', data);
    return response.data;
  },

  // Get methodology recommendations
  getRecommendations: async (): Promise<MethodologyRecommendationsResponse> => {
    const response = await api.get('/budget/methodologies/recommendations');
    return response.data;
  }
};

export default api;
